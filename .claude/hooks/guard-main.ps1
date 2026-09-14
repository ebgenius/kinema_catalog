<#
.SYNOPSIS
    Refuse `git commit` and `git push` when they would advance the default branch.

.DESCRIPTION
    main advances only through a reviewed PR. Work belongs on a type/short-slug
    branch; see CLAUDE.md.

    This exists because the written rule alone was not enough: five commits
    landed directly on main in one session before anyone noticed. A hook
    notices every time.

    Reads a Claude Code PreToolUse payload on stdin and, when it decides to
    block, prints a permissionDecision of "deny" with a reason.

    Two rules shape everything below, both learned from guards that looked fine
    and were not:

    1. Decide per command segment, never by matching the whole command. A
       commit message is data sitting in the same string as the commands, so a
       regex over the lot reads prose as structure -- that is how `git commit -m
       "remember to --dry-run first"` used to be waved through on main.

    2. Ask git, in the repository the command actually names. "Which branch am I
       on" is not "which branch does this write to": push.default, upstream
       configuration, remote.<name>.push, a wildcard refspec and `-C` can each
       send a push somewhere the command text never mentions.

    Fails OPEN. If the payload will not parse, or git cannot answer, the command
    is allowed. A guard that blocks all shell work when it misfires is worse
    than the problem it solves.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------- tokenising

function Get-Tokens([string]$Segment) {
    # Whitespace-separated tokens with every shell quote removed.
    #
    # Removed throughout the token, not just trimmed from its ends. The shell
    # concatenates around quotes, so `HEAD:"main"` and even `m"ai"n` reach git
    # as `main`; a guard that only strips the outside sees neither.
    #
    # Safe to do unconditionally: git refuses a ref name containing a quote, so
    # removing them cannot merge two distinct refs into one.
    @($Segment -split '\s+' | Where-Object { $_ } | ForEach-Object { $_ -replace '["'']', '' } | Where-Object { $_ })
}

function Get-Args([string]$Segment) {
    # Non-flag tokens, with a leading '+' (force refspec) removed.
    @(Get-Tokens $Segment | Where-Object { $_ -notmatch '^-' } | ForEach-Object { $_ -replace '^\+', '' } | Where-Object { $_ })
}

function Remove-HereStrings([string]$Command) {
    # Blank out here-string bodies before anything reads the command structure.
    #
    # A commit message is data, and in this workflow it arrives as @'...'@ --
    # paragraphs of prose sitting inside the same shell call as the push that
    # follows it. Left in, every word of it is a token: a message mentioning
    # "the main thread" made the push check see a push to main.
    #
    # Ordinary quotes are deliberately left in place here. They are short enough
    # to hold a real ref, and `git push origin "main"` must still be caught --
    # Get-Tokens strips them from the token instead, where a ref is compared.
    $stripped = $Command -replace "(?s)@'.*?'@", ' '
    return $stripped -replace '(?s)@".*?"@', ' '
}

#: Global git options that consume the following token as their value, so the
#: subcommand scan must step over both.
$script:GitOptionsWithValue = @('-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path')

function Get-GitSubcommand([string]$Segment) {
    # The subcommand only, e.g. 'commit' from `git -C repo -c k=v commit -m x`.
    #
    # Matching the word anywhere in the line is not good enough: `\bcommit\b`
    # also fires on `git commit-graph` (a '-' is a word boundary) and on
    # `git log --grep=commit`, blocking read-only commands that merely mention
    # it. Only the subcommand position decides.
    $tokens = @(Get-Tokens $Segment)
    $i = [array]::IndexOf($tokens, 'git')
    if ($i -lt 0) { return $null }
    for ($i++; $i -lt $tokens.Count; $i++) {
        $token = $tokens[$i]
        if ($token -in $script:GitOptionsWithValue) { $i++; continue }
        if ($token -match '^-') { continue }
        return $token
    }
    return $null
}

function Join-LineContinuations([string]$Command, [string]$Shell) {
    <#
        A newline preceded by this shell's continuation character is not a
        command boundary.

        Shell-specific on purpose. Treating both characters as continuations
        looked harmless and was not: PowerShell does not continue on `\`, so

            git status \
            git push origin main

        was merged into one segment whose subcommand read as 'status', and the
        push went unseen. Joining a line that the real shell keeps separate
        hides whatever is on the second line.
    #>
    switch ($Shell) {
        'Bash'       { return $Command -replace '\\[ \t]*\r?\n', ' ' }
        'PowerShell' { return $Command -replace '`[ \t]*\r?\n', ' ' }
        default      { return $Command }
    }
}

function Get-Segments([string]$Command, [string]$Shell) {
    # Each `;`, `&&`, `||`, `|` or *newline* separated part is its own command
    # line. The newline matters: a single tool call routinely holds several
    # statements on separate lines, and without it `git add -A` and
    # `git commit -m x` were one segment whose subcommand read as `add`.
    @((Join-LineContinuations $Command $Shell) -split '(?:&&|\|\||[;|]|\r?\n)' | Where-Object { $_ -and $_.Trim() })
}

# ------------------------------------------------------------- git invocation

function Get-GitContextArgs([string]$Segment) {
    <#
        The -C / --git-dir / --work-tree options from this segment, so every
        probe runs against the repository the command actually names.

        Without this the hook asks about its own working directory while the
        command operates elsewhere: `git -C ../other push` was judged by this
        checkout's branch and configuration, which is the wrong repository.
    #>
    $tokens = @(Get-Tokens $Segment)
    $ctx = @()
    for ($i = 0; $i -lt $tokens.Count; $i++) {
        $t = $tokens[$i]
        if (($t -eq '-C' -or $t -eq '--git-dir' -or $t -eq '--work-tree') -and ($i + 1) -lt $tokens.Count) {
            $ctx += @($t, $tokens[$i + 1])
            $i++
        }
        elseif ($t -match '^(--git-dir|--work-tree)=(.+)$') {
            $ctx += @($Matches[1], $Matches[2])
        }
    }
    return , $ctx
}

function Invoke-Git([string[]]$Ctx, [string[]]$GitArgs) {
    # Returns trimmed stdout, or $null when git fails. Never throws: a probe
    # that cannot answer must leave the decision to fail open.
    try {
        $out = (& git @Ctx @GitArgs 2>$null | Out-String)
        if ($LASTEXITCODE -ne 0) { return $null }
        if ([string]::IsNullOrWhiteSpace($out)) { return '' }
        return $out.Trim()
    } catch {
        return $null
    }
}

function Test-GitRefExists([string[]]$Ctx, [string]$Ref) {
    try {
        & git @Ctx show-ref --verify --quiet $Ref 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-CurrentBranch([string[]]$Ctx) {
    # symbolic-ref, not `rev-parse --abbrev-ref HEAD`: rev-parse cannot name the
    # branch before the first commit exists (it errors and prints "HEAD"), so a
    # fresh repo sitting on main would sail straight through. symbolic-ref
    # reports "main" there, and fails on a detached HEAD -- which is not main,
    # so allowing is the right answer anyway.
    return (Invoke-Git $Ctx @('symbolic-ref', '--short', '--quiet', 'HEAD'))
}

function Expand-GitAlias([string]$Segment, [string[]]$Ctx) {
    <#
        Replace a git alias with what it stands for, once.

        Without this the subcommand check reads the alias name: with
        `alias.p = push`, `git p origin main` has subcommand 'p', is neither a
        commit nor a push as far as the hook is concerned, and sails through
        while pushing main.

        Expanded once only, which matches git: aliases are not recursive. A
        shell alias (`!...`) becomes the body itself, since that body is the
        command line that actually runs.
    #>
    $sub = Get-GitSubcommand $Segment
    if ([string]::IsNullOrWhiteSpace($sub)) { return $Segment }

    $expansion = Invoke-Git $Ctx @('config', '--get', "alias.$sub")
    if ([string]::IsNullOrWhiteSpace($expansion)) { return $Segment }

    if ($expansion.StartsWith('!')) { return $expansion.Substring(1) }

    # Swap the alias token for its expansion, leaving the rest of the line alone.
    $tokens = @($Segment -split '\s+' | Where-Object { $_ })
    for ($i = 0; $i -lt $tokens.Count; $i++) {
        if (($tokens[$i] -replace '["'']', '') -eq $sub) {
            $tokens[$i] = $expansion
            break
        }
    }
    return ($tokens -join ' ')
}

# ----------------------------------------------------------- push destinations

function Get-PushRefspecs([string]$Segment, [string[]]$Ctx) {
    # The refspec arguments of a push, with the remote name or URL dropped.
    $argv = @(Get-Args $Segment)
    $i = [array]::IndexOf($argv, 'push')
    if ($i -lt 0 -or ($i + 1) -ge $argv.Count) { return @() }

    $rest = @($argv[($i + 1)..($argv.Count - 1)])
    if ($rest.Count -eq 0) { return @() }

    $remotes = @()
    $listed = Invoke-Git $Ctx @('remote')
    if ($listed) { $remotes = @($listed -split '\r?\n' | Where-Object { $_ }) }

    $first = $rest[0]
    $isRemote = ($remotes -contains $first) -or
                ($first -match '^(https?://|git@|ssh://|git://|file://|\.{1,2}/)')

    # A remote may not be configured yet (a fresh clone-less repo, or a URL
    # typed straight in), so fall back on what the token is: a refspec names a
    # ref that exists here, or carries ':' or '*'. Anything else in first
    # position is the remote. Without this `git push origin v1.0` read 'origin'
    # as a refspec, found it was not a tag, and refused a legitimate tag push.
    if (-not $isRemote -and $first -notmatch '[:*]') {
        $isRemote = -not (Test-GitRefExists $Ctx "refs/heads/$first") -and
                    -not (Test-GitRefExists $Ctx "refs/tags/$first") -and
                    ($first -ne 'HEAD')
    }

    if ($isRemote) {
        if ($rest.Count -le 1) { return @() }
        $rest = @($rest[1..($rest.Count - 1)])
    }
    return $rest
}

function Get-RefspecDestination([string]$Refspec) {
    # The right-hand side of src:dst, or the whole thing when it is one-sided.
    $dst = $Refspec
    if ($dst.Contains(':')) { $dst = $dst.Substring($dst.LastIndexOf(':') + 1) }
    return ($dst -replace '^refs/heads/', '')
}

function Test-RefspecsTargetMain([string[]]$Refspecs) {
    # Compared as a whole ref, not a substring, so `fix/domain-main` and
    # `feature/main` are left alone -- only the branch actually called main.
    foreach ($r in $Refspecs) {
        if ((Get-RefspecDestination $r) -eq 'main') { return $true }
    }
    return $false
}

function Test-PushesAllBranches([string]$Segment, [string[]]$Refspecs) {
    <#
        Forms that carry every branch, main included, without naming it.

        --branches is the modern spelling of --all and was missed entirely; the
        matching refspec ':' and wildcards like refs/heads/*:refs/heads/* were
        read as ordinary refspecs whose destination simply was not "main".
    #>
    if ($Segment -match '(^|\s)--(all|branches|mirror)(\s|$)') { return $true }
    foreach ($r in $Refspecs) {
        if ($r -eq ':') { return $true }
        if ((Get-RefspecDestination $r) -match '\*') { return $true }
    }
    return $false
}

function Get-ConfiguredPushRefspecs([string[]]$Ctx, [string]$Remote) {
    # remote.<name>.push decides where a bare `git push` goes before
    # push.default is ever consulted.
    if ([string]::IsNullOrWhiteSpace($Remote)) { return @() }
    $configured = Invoke-Git $Ctx @('config', '--get-all', "remote.$Remote.push")
    if ([string]::IsNullOrWhiteSpace($configured)) { return @() }
    return @($configured -split '\r?\n' | Where-Object { $_ })
}

function Get-PushRemote([string]$Segment, [string[]]$Ctx, [string]$Branch) {
    $argv = @(Get-Args $Segment)
    $i = [array]::IndexOf($argv, 'push')
    if ($i -ge 0 -and ($i + 1) -lt $argv.Count) {
        $remotes = @()
        $listed = Invoke-Git $Ctx @('remote')
        if ($listed) { $remotes = @($listed -split '\r?\n' | Where-Object { $_ }) }
        if ($remotes -contains $argv[$i + 1]) { return $argv[$i + 1] }
    }
    if ($Branch) {
        $configured = Invoke-Git $Ctx @('config', '--get', "branch.$Branch.remote")
        if ($configured) { return $configured }
    }
    return 'origin'
}

function Get-ImplicitPushTarget([string[]]$Ctx, [string]$Segment) {
    <#
        The branch a refspec-less `git push` would actually update, resolved
        from configuration alone.

        With push.default=upstream and an upstream of origin/main, `git push`
        from feat/x updates main -- git reports it as
        refs/heads/feat/x:refs/heads/main. Nothing in the command text mentions
        main, and HEAD is not main, so the other checks pass it honestly.

        Read from config rather than `git push --dry-run`: a hook must not reach
        the network, where it could hang or prompt for credentials.
    #>
    $branch = Get-CurrentBranch $Ctx
    if ([string]::IsNullOrWhiteSpace($branch)) { return $null }

    # remote.<name>.push wins over push.default.
    $remote = Get-PushRemote $Segment $Ctx $branch
    foreach ($spec in (Get-ConfiguredPushRefspecs $Ctx $remote)) {
        if ($spec -eq ':') { return 'main' }
        $dst = Get-RefspecDestination $spec
        if ($dst -eq 'main' -or $dst -match '\*') { return 'main' }
    }

    $mode = Invoke-Git $Ctx @('config', '--get', 'push.default')
    if ([string]::IsNullOrWhiteSpace($mode)) { $mode = 'simple' }   # git >= 2.0

    switch ($mode) {
        { $_ -in @('upstream', 'tracking') } {
            # Goes to the configured upstream whatever the local name is.
            $merge = Invoke-Git $Ctx @('config', '--get', "branch.$branch.merge")
            if ([string]::IsNullOrWhiteSpace($merge)) { return $null }
            return ($merge -replace '^refs/heads/', '')
        }
        'matching' {
            # Pushes every branch that already exists on the remote, so a local
            # main rides along no matter which branch HEAD is on.
            if (Test-GitRefExists $Ctx 'refs/heads/main') { return 'main' }
            return $null
        }
        default {
            # simple and current push to the branch of the same name; simple
            # refuses outright when the upstream is named differently.
            return $branch
        }
    }
}

function Test-TagOnlyPush([string]$Segment, [string[]]$Refspecs, [string[]]$Ctx) {
    <#
        True only when every refspec in the push is a tag.

        "Any argument is a tag" was not enough: `git push origin v1.0 HEAD` on
        main passed the ref check (no token equals main), hit the carve-out
        because v1.0 is a tag, and advanced main through HEAD. One real tag
        anywhere exempted the whole push.

        Ask git rather than guessing from the name -- a pattern like `v\d` also
        matches branches called v2 or v10-experiment.
    #>
    $hasTagsFlag = ((Get-Tokens $Segment) -contains '--tags')
    if ($Refspecs.Count -eq 0) { return $hasTagsFlag }

    foreach ($r in $Refspecs) {
        $src = $r
        if ($src.Contains(':')) { $src = $src.Substring(0, $src.IndexOf(':')) }
        $src = $src -replace '^refs/tags/', ''
        if ([string]::IsNullOrWhiteSpace($src)) { return $false }
        if (-not (Test-GitRefExists $Ctx "refs/tags/$src")) { return $false }
    }
    return $true
}

function Test-SegmentIsDryRun([string]$Segment) {
    # An exact option token, never a substring of the command.
    #
    # `$command -match '--dry-run'` let `git commit -m "remember to --dry-run
    # first"` through on main: prose matched the flag. Same shape as the tag
    # bug -- a whole-command regex over data.
    $tokens = @(Get-Tokens $Segment)
    return (($tokens -contains '--dry-run') -or ($tokens -contains '-n'))
}

# --------------------------------------------------------------- the decision

function Get-DenyReason([string]$Command, [string]$Shell) {
    # Returns a reason to refuse, or $null to allow.
    $cmd = Remove-HereStrings $Command

    # Expand aliases first: the subcommand is what everything below keys on.
    $segments = @()
    foreach ($raw in (Get-Segments $cmd $Shell)) {
        $ctx = Get-GitContextArgs $raw
        $expanded = Expand-GitAlias $raw $ctx
        # A shell alias body can itself be several commands.
        foreach ($piece in (Get-Segments $expanded $Shell)) {
            $segments += , @{ Text = $piece; Ctx = (Get-GitContextArgs $piece) }
        }
    }

    $commitSegments = @($segments | Where-Object { (Get-GitSubcommand $_.Text) -eq 'commit' })
    $pushSegments   = @($segments | Where-Object { (Get-GitSubcommand $_.Text) -eq 'push' })
    if ($commitSegments.Count -eq 0 -and $pushSegments.Count -eq 0) { return $null }

    # A dry run changes nothing -- but only when every push really carries the
    # option and nothing is being committed alongside it.
    if ($commitSegments.Count -eq 0 -and $pushSegments.Count -gt 0) {
        $allDry = $true
        foreach ($seg in $pushSegments) {
            if (-not (Test-SegmentIsDryRun $seg.Text)) { $allDry = $false; break }
        }
        if ($allDry) { return $null }
    }

    foreach ($seg in $commitSegments) {
        if ((Get-CurrentBranch $seg.Ctx) -eq 'main') {
            return @"
Committing on 'main' is blocked. main only advances through a reviewed PR.

Create a branch first, then commit there:
    git checkout -b <type>/<short-slug>     # fix/ feat/ docs/ chore/

Then push it and open a draft PR, and wait for review before going further.
See CLAUDE.md. (Tag pushes and --dry-run are allowed on main.)
"@
        }
    }

    foreach ($seg in $pushSegments) {
        $ctx = $seg.Ctx
        $refspecs = @(Get-PushRefspecs $seg.Text $ctx)

        # Named outright, in any spelling: main, refs/heads/main, HEAD:main, +main.
        if (Test-RefspecsTargetMain $refspecs) {
            return @"
Pushing to 'main' is blocked. main only advances through a reviewed PR.

Push your branch instead, then open a draft PR and wait for review:
    git push -u origin <type>/<short-slug>

See CLAUDE.md.
"@
        }

        # --all / --branches / --mirror / ':' / wildcard refspecs carry main
        # along from any branch without ever naming it.
        if ((Test-PushesAllBranches $seg.Text $refspecs) -and (Test-GitRefExists $ctx 'refs/heads/main')) {
            return @"
This push carries every branch, 'main' included. main only advances through a
reviewed PR.

Name the branch you mean instead:
    git push -u origin <type>/<short-slug>

See CLAUDE.md.
"@
        }

        # Tag pushes are how a release is cut and never advance a branch. If git
        # cannot confirm every refspec is a tag the push is simply not exempted.
        # Checked before the destination below, because `git push --tags origin`
        # carries no refspec at all and would otherwise be judged by the branch
        # a bare push would have updated.
        if (Test-TagOnlyPush $seg.Text $refspecs $ctx) { continue }

        # No refspec still has a destination, and it is not always this branch.
        if ($refspecs.Count -eq 0) {
            if ((Get-ImplicitPushTarget $ctx $seg.Text) -eq 'main') {
                return @"
This push updates 'main', even though the command does not name it. main only
advances through a reviewed PR.

Name the branch you mean instead:
    git push -u origin <type>/<short-slug>

See CLAUDE.md.
"@
            }
        }

        if ((Get-CurrentBranch $ctx) -eq 'main') {
            return @"
Pushing on 'main' is blocked. main only advances through a reviewed PR.

Create a branch first, then commit there:
    git checkout -b <type>/<short-slug>     # fix/ feat/ docs/ chore/

Then push it and open a draft PR, and wait for review before going further.
See CLAUDE.md. (Tag pushes and --dry-run are allowed on main.)
"@
        }
    }

    return $null
}

function Allow {
    # Silence is consent: emitting nothing leaves the permission decision alone.
    exit 0
}

function Deny([string]$Reason) {
    @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $Reason
        }
    } | ConvertTo-Json -Depth 5 -Compress
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { Allow }
    $payload = $raw | ConvertFrom-Json
    $command = $payload.tool_input.command
    if ([string]::IsNullOrWhiteSpace($command)) { Allow }

    $toolName = ''
    if ($payload.PSObject.Properties.Name -contains 'tool_name') { $toolName = [string]$payload.tool_name }
} catch {
    Allow
}

# Which shell ran this decides what continues a line. When the payload does not
# say, judge it as both and refuse if either reading would advance main --
# guessing wrong in the permissive direction is how a push goes unseen.
$shells = switch -regex ($toolName) {
    'PowerShell' { @('PowerShell'); break }
    'Bash'       { @('Bash'); break }
    default      { @('Bash', 'PowerShell') }
}

foreach ($shell in $shells) {
    try {
        $reason = Get-DenyReason $command $shell
    } catch {
        # Fail open, as everywhere else here -- but a guard that crashes is
        # indistinguishable from one that approves, so make it possible to see.
        if ($env:KINEMA_GUARD_DEBUG) { [Console]::Error.WriteLine("guard-main: $_") }
        $reason = $null
    }
    if ($reason) { Deny $reason }
}

Allow
