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
    <#
        The arguments git would actually receive: split on whitespace outside
        quotes, with the quotes themselves removed.

        Quote-aware on purpose. Splitting on every space first and stripping
        quotes afterwards got both directions wrong:

          - `git push origin "--all"` became the token `"--all"`, which no flag
            check recognised, although the shell hands git a plain --all.
          - `--push-option "skip --all checks"` became three tokens, one of
            them --all, although git receives a single option value.

        Quotes are still removed throughout a word, since the shell concatenates
        around them: `HEAD:"main"` and `m"ai"n` both reach git as main. That is
        safe because git refuses a ref name containing a quote.

        Backslash is literal outside quotes -- Windows paths depend on it -- and
        escapes only a double quote inside one (`\"`, or PowerShell's `` `" ``).
    #>
    $words = New-Object System.Collections.Generic.List[string]
    $word = New-Object System.Text.StringBuilder
    $inWord = $false
    $quote = ''
    for ($i = 0; $i -lt $Segment.Length; $i++) {
        $ch = [string]$Segment[$i]
        $next = if (($i + 1) -lt $Segment.Length) { [string]$Segment[$i + 1] } else { '' }
        if ($quote -eq '') {
            if ($ch -match '\s') {
                if ($inWord) { $words.Add($word.ToString()); [void]$word.Clear(); $inWord = $false }
            } elseif ($ch -eq "'" -or $ch -eq '"') {
                $quote = $ch; $inWord = $true
            } else {
                [void]$word.Append($ch); $inWord = $true
            }
        } elseif ($quote -eq "'") {
            if ($ch -eq "'") {
                if ($next -eq "'") { [void]$word.Append("'"); $i++ }     # PowerShell's ''
                else { $quote = '' }
            } else {
                [void]$word.Append($ch)
            }
        } else {
            if (($ch -eq '\' -or $ch -eq '`') -and $next -eq '"') { [void]$word.Append('"'); $i++ }
            elseif ($ch -eq '"') { $quote = '' }
            else { [void]$word.Append($ch) }
        }
    }
    if ($inWord) { $words.Add($word.ToString()) }
    @($words | Where-Object { $_ })
}

function Get-Args([string]$Segment) {
    # Non-flag tokens, with a leading '+' (force refspec) removed.
    @(Get-Tokens $Segment | Where-Object { $_ -notmatch '^-' } | ForEach-Object { $_ -replace '^\+', '' } | Where-Object { $_ })
}

function Test-HasShellExpansion([string]$Token) {
    # A token whose value the shell computes before git sees it: $VAR, ${VAR},
    # $(...), a backtick substitution. Its final text is unknowable here, so a
    # refspec carrying one cannot be compared against main.
    return ($Token -match '\$' -or $Token.Contains('`'))
}

function Measure-Structural([string]$Text) {
    <#
        Counts of parentheses, braces and backticks that are real shell
        structure -- outside quotes and not backslash-escaped -- plus the last
        such character seen.

        A raw count treated `echo \)` as closing a subshell, because the escaped
        `)` given to echo looked like a delimiter. Grouping has to be measured
        the way the shell reads it, not by matching the character anywhere.
    #>
    $o = 0; $c = 0; $ob = 0; $cb = 0; $bt = 0; $last = ''
    $quote = ''
    for ($i = 0; $i -lt $Text.Length; $i++) {
        $ch = [string]$Text[$i]
        if ($quote -ne '') {
            if ($ch -eq $quote) { $quote = '' }
            elseif ($ch -eq '\' -and $quote -eq '"') { $i++ }   # \" inside double quotes
            continue
        }
        if ($ch -eq '\') { $i++; continue }                     # escapes the next char
        if ($ch -eq "'" -or $ch -eq '"') { $quote = $ch; continue }
        switch ($ch) {
            '(' { $o++;  $last = '(' }
            ')' { $c++;  $last = ')' }
            '{' { $ob++; $last = '{' }
            '}' { $cb++; $last = '}' }
            '`' { $bt++; $last = '`' }
            default { if ($ch -notmatch '\s') { $last = 'x' } }
        }
    }
    return @{ Open = $o; Close = $c; OpenBrace = $ob; CloseBrace = $cb; Backtick = $bt; Last = $last }
}

#: git push options that take their value as the *next* argument. Git consumes
#: that argument whatever it looks like, including a leading dash.
$script:PushOptionsWithValue = @('-o', '--push-option', '--receive-pack', '--exec', '--repo')

function Get-PushTokens([string]$Segment) {
    <#
        Tokens of a push with the values of value-taking options dropped.

        `git push -o -n` sends "-n" as a push option; it is not a dry run. Read
        token by token without this, the -n looked like the flag and the whole
        push was exempted as changing nothing.
    #>
    $tokens = @(Get-Tokens $Segment)
    $kept = @()
    for ($i = 0; $i -lt $tokens.Count; $i++) {
        $kept += $tokens[$i]
        if ($tokens[$i] -in $script:PushOptionsWithValue) { $i++ }
    }
    return $kept
}

function Get-PushArgs([string]$Segment) {
    # Non-flag push arguments, option values excluded, leading '+' removed.
    @(Get-PushTokens $Segment | Where-Object { $_ -notmatch '^-' } | ForEach-Object { $_ -replace '^\+', '' } | Where-Object { $_ })
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

function Get-GitContextArgs([string]$Segment, [string]$Shell) {
    <#
        The -C / --git-dir / --work-tree options from this segment, so every
        probe runs against the repository the command actually names.

        Without this the hook asks about its own working directory while the
        command operates elsewhere: `git -C ../other push` was judged by this
        checkout's branch and configuration, which is the wrong repository.

        Paths go through the same host translation as `cd`, so a Git Bash
        `-C /c/work/repo` is probed where git really finds it.
    #>
    $tokens = @(Get-Tokens $Segment)
    $ctx = @()
    for ($i = 0; $i -lt $tokens.Count; $i++) {
        $t = $tokens[$i]
        if (($t -eq '-C' -or $t -eq '--git-dir' -or $t -eq '--work-tree') -and ($i + 1) -lt $tokens.Count) {
            $value = ConvertTo-HostPath $tokens[$i + 1] $Shell
            if (-not $value) { $value = $tokens[$i + 1] }
            $ctx += @($t, $value)
            $i++
        }
        elseif ($t -match '^(--git-dir|--work-tree)=(.+)$') {
            $name = $Matches[1]
            $value = ConvertTo-HostPath $Matches[2] $Shell
            if (-not $value) { $value = $Matches[2] }
            $ctx += @($name, $value)
        }
    }
    # Unrolled on purpose: callers wrap the result in @(), which gives the same
    # array for zero, one or many options. `return , $ctx` did not survive that.
    return $ctx
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
    $argv = @(Get-PushArgs $Segment)
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

        The flags are compared as exact tokens, as git receives them. A regex
        over the raw segment wanted whitespace before "--", so the quoted
        `git push origin "--all"` slipped past it -- and it matched the words
        inside `--push-option "skip --all checks"`, refusing a push that
        carries nothing but feat/x.
    #>
    $tokens = @(Get-PushTokens $Segment)
    foreach ($flag in @('--all', '--branches', '--mirror')) {
        if ($tokens -contains $flag) { return $true }
    }
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
    $argv = @(Get-PushArgs $Segment)
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
    $hasTagsFlag = (@(Get-PushTokens $Segment) -contains '--tags')
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
    # An exact option token, never a substring of the command -- and never the
    # value of an option that takes one.
    #
    # `$command -match '--dry-run'` let `git commit -m "remember to --dry-run
    # first"` through on main: prose matched the flag. And `git push -o -n`
    # sends "-n" as a push option: git really pushes, but a plain token scan
    # read it as a dry run and exempted the push.
    $tokens = @(Get-PushTokens $Segment)
    return (($tokens -contains '--dry-run') -or ($tokens -contains '-n'))
}

# ----------------------------------------------------- where each command runs

$script:OnWindows = ([IO.Path]::DirectorySeparatorChar -eq '\')

function ConvertTo-HostPath([string]$Path, [string]$Shell) {
    <#
        A path as written in the command, translated to one this process can
        test. $null when it cannot be translated.

        Only Git Bash on Windows needs this. It writes C:\work as /c/work, and a
        mount such as /tmp points somewhere only cygpath knows. Tested as-is,
        neither exists, and a cd into a repository on main would look like a cd
        into nothing.
    #>
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    if (-not $script:OnWindows -or $Shell -ne 'Bash' -or -not $Path.StartsWith('/')) { return $Path }
    if ($Path -match '^/([A-Za-z])(/.*)?$') {
        $rest = if ($Matches[2]) { $Matches[2] } else { '/' }
        return ($Matches[1].ToUpperInvariant() + ':' + $rest)
    }
    try {
        $translated = (& cygpath -w $Path 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $translated) { return $translated }
    } catch { }
    return $null
}

function Resolve-Directory([string]$Base, [string]$Target, [string]$Shell) {
    <#
        Where `cd <Target>` from <Base> lands, or $null when that cannot be known
        without running the shell.

        $null is the answer for anything expanded at run time -- variables,
        globs, substitutions, ~user -- and for a directory that does not exist
        here. In each case the alternative is to keep judging the old directory,
        which is exactly the bypass this tracking exists to close.
    #>
    if ([string]::IsNullOrWhiteSpace($Target)) { return $null }
    if ($Target -match '[$`%*?{}()<>!\[\]]') { return $null }
    if ($Target -eq '~' -or $Target.StartsWith('~/') -or $Target.StartsWith('~\')) {
        $Target = $HOME + $Target.Substring(1)
    } elseif ($Target.StartsWith('~')) {
        return $null
    }
    $hostTarget = ConvertTo-HostPath $Target $Shell
    if (-not $hostTarget) { return $null }
    try {
        $full = [IO.Path]::GetFullPath([IO.Path]::Combine($Base, $hostTarget))
    } catch {
        return $null
    }
    if (Test-Path -LiteralPath $full -PathType Container) { return $full }
    return $null
}

#: Commands that move the working directory, per shell, and what each does.
$script:DirectoryCommands = @{
    Bash       = @{ 'cd' = 'set'; 'pushd' = 'push'; 'popd' = 'pop' }
    PowerShell = @{
        'cd' = 'set'; 'chdir' = 'set'; 'sl' = 'set'; 'set-location' = 'set'
        'pushd' = 'push'; 'push-location' = 'push'; 'popd' = 'pop'; 'pop-location' = 'pop'
    }
}

function Get-DirectoryChange([string]$Core, [string]$Shell) {
    # A cd / pushd / popd (or its PowerShell cmdlet) and its target, or $null.
    $table = $script:DirectoryCommands[$Shell]
    if (-not $table) { return $null }
    $tokens = @(Get-Tokens $Core)
    if ($tokens.Count -eq 0) { return $null }
    $i = 0
    if ($tokens[0] -eq 'builtin' -and $tokens.Count -gt 1) { $i = 1 }
    $kind = $table[$tokens[$i].ToLowerInvariant()]
    if (-not $kind) { return $null }

    for ($j = $i + 1; $j -lt $tokens.Count; $j++) {
        $t = $tokens[$j]
        if ($t -eq '-') { return @{ Kind = $kind; Target = '-' } }
        if ($Shell -eq 'PowerShell' -and $t -match '^-(Path|LiteralPath)$') {
            if (($j + 1) -lt $tokens.Count) { return @{ Kind = $kind; Target = $tokens[$j + 1] } }
            return @{ Kind = $kind; Target = $null }
        }
        if ($Shell -eq 'PowerShell' -and $t -match '^-StackName$') { $j++; continue }
        if ($t.StartsWith('-')) { continue }
        return @{ Kind = $kind; Target = $t }
    }
    return @{ Kind = $kind; Target = $null }
}

function Merge-Directories([object[]]$First, [object[]]$Second) {
    # Union, first occurrence kept. Emitted unrolled; callers wrap in @().
    $seen = @{}
    foreach ($d in (@($First) + @($Second))) {
        if ($d -and -not $seen.ContainsKey([string]$d)) {
            $seen[[string]$d] = $true
            $d
        }
    }
}

function Resolve-DirectoryChange($Change, [object[]]$Dirs, [object[]]$Prev, $DirStack, [string]$Shell) {
    # Where the candidate directories go after one cd / pushd / popd.
    if ($Change.Kind -eq 'pop') {
        if ($DirStack.Count -eq 0) { return @{ Unknown = $true } }
        return @{ Unknown = $false; Dirs = @($DirStack.Pop()) }
    }

    $target = $Change.Target
    if ($null -eq $target) {
        # A bare `cd` goes home in bash. A bare pushd swaps the stack, and
        # PowerShell's bare Set-Location is version-dependent: not guessed.
        if ($Shell -eq 'Bash' -and $Change.Kind -eq 'set') { $target = $HOME }
        else { return @{ Unknown = $true } }
    }

    if ($target -eq '-') {
        if (@($Prev).Count -eq 0) { return @{ Unknown = $true } }
        $resolved = @($Prev)
    } else {
        $resolved = @()
        foreach ($d in $Dirs) {
            $r = Resolve-Directory $d $target $Shell
            if (-not $r) { return @{ Unknown = $true } }
            $resolved += $r
        }
    }

    if ($Change.Kind -eq 'push') { $DirStack.Push(@($Dirs)) }
    return @{ Unknown = $false; Dirs = @(Merge-Directories @() $resolved) }
}

function Split-GroupMarks([string]$Text, [string]$Shell) {
    <#
        The command inside any grouping, and how many subshells it opens and
        closes.

        `(git push origin main)` used to be read as a command whose first token
        was "(git", so there was no git subcommand and the push went unseen.

        Only bash scopes the directory: `(cd x && ...)`, `$(...)` and a backtick
        substitution all leave the outer shell where it was. A PowerShell group
        or subexpression runs in the same session, where Set-Location persists,
        so there it strips the marks but opens nothing.
    #>
    $core = $Text.Trim()
    $opens = 0
    $closes = 0
    $bash = ($Shell -eq 'Bash')
    while ($core.Length -gt 0) {
        if ($core.StartsWith('$(')) { $core = $core.Substring(2).TrimStart(); $opens++ }
        elseif ($core.StartsWith('(')) { $core = $core.Substring(1).TrimStart(); $opens++ }
        elseif ($core.StartsWith('{')) { $core = $core.Substring(1).TrimStart() }
        elseif ($bash -and $core.StartsWith('`')) { $core = $core.Substring(1).TrimStart(); $opens++ }
        else { break }
    }
    while ($core.Length -gt 0) {
        # Structural counts, so an escaped or quoted `)` inside a command (an
        # `echo \)` argument, say) is not mistaken for the end of a subshell.
        $m = Measure-Structural $core
        if ($m.Last -eq ')' -and $m.Close -gt $m.Open) {
            $core = $core.Substring(0, $core.Length - 1).TrimEnd(); $closes++
        }
        elseif ($m.Last -eq '}' -and $m.CloseBrace -gt $m.OpenBrace) {
            $core = $core.Substring(0, $core.Length - 1).TrimEnd()
        }
        elseif ($bash -and $m.Last -eq '`' -and ($m.Backtick % 2 -eq 1)) {
            $core = $core.Substring(0, $core.Length - 1).TrimEnd(); $closes++
        }
        else { break }
    }
    if (-not $bash) { $opens = 0; $closes = 0 }
    return @{ Core = $core; Opens = $opens; Closes = $closes }
}

function Get-SegmentsWithSeparators([string]$Command, [string]$Shell) {
    # Get-Segments, keeping the operator on each side of every segment: a cd
    # means something different before `&&`, before `||`, and inside a bash
    # pipeline. Emitted unrolled; callers wrap in @().
    $parts = @((Join-LineContinuations $Command $Shell) -split '(&&|\|\||[;|]|\r?\n)')
    $before = ''
    for ($k = 0; $k -lt $parts.Count; $k += 2) {
        $text = $parts[$k]
        $after = if (($k + 1) -lt $parts.Count) { $parts[$k + 1] } else { '' }
        if ($text -and $text.Trim()) {
            @{ Text = $text; Before = $before; After = $after }
        }
        $before = $after
    }
}

function Test-RootedGitContext([object[]]$Ctx) {
    # True when -C or --git-dir names an absolute location, which git uses
    # whatever directory the command started in.
    $list = @($Ctx)
    for ($i = 0; ($i + 1) -lt $list.Count; $i += 2) {
        if ($list[$i] -in @('-C', '--git-dir') -and [IO.Path]::IsPathRooted([string]$list[$i + 1])) { return $true }
    }
    return $false
}

$script:UnresolvedDirectoryReason = @"
This git command runs after a directory change the guard cannot resolve -- a cd
to a variable or substitution, a path that does not exist here, or a popd past
where the command started -- so it cannot tell which repository, or which
branch, it would change.

Name the repository explicitly instead:
    git -C <path/to/repo> commit ...
    git -C <path/to/repo> push -u origin <type>/<short-slug>

See CLAUDE.md.
"@

# --------------------------------------------------------------- the decision

function Get-DenyReason([string]$Command, [string]$Shell, [string]$StartDir) {
    # Returns a reason to refuse, or $null to allow.
    $cmd = Remove-HereStrings $Command
    if ([string]::IsNullOrWhiteSpace($StartDir)) { $StartDir = (Get-Location).ProviderPath }

    <#
        Where each command runs, tracked through the command line.

        A later `git commit` used to be judged in the hook's own directory
        whatever came before it, so `cd ../repo-on-main && git commit` committed
        onto main while the guard looked at a feature branch.

        $dirs is a list, not one directory, because control flow leaves the
        answer open. Within a `&&` / `||` chain a command runs only if the ones
        before it succeeded, so a `cd` there is deterministic *for a command
        still in the same chain*: if the cd was skipped, so is that command. But
        an unconditional separator (`;` or a newline) starts a fresh command
        that runs whatever happened before -- so the shell could be wherever the
        chain finished, or wherever it aborted. $abortDirs carries those
        aborted-chain directories and is merged back in at each `;`.

        $unknown records a change that could not be resolved at all; after it, a
        commit or push is refused rather than guessed at.
    #>
    $dirs = @($StartDir)
    $prev = @()
    $abortDirs = @()
    $unknown = $false
    $dirStack = New-Object System.Collections.Stack
    $groupStack = New-Object System.Collections.Stack

    $segments = @()
    foreach ($part in @(Get-SegmentsWithSeparators $cmd $Shell)) {
        $marks = Split-GroupMarks $part.Text $Shell
        $core = $marks.Core
        $before = $part.Before
        $isConditional = ($before -eq '&&') -or ($before -eq '||')
        $isUnconditional = ($before -eq '') -or ($before -eq ';') -or ($before -match '[\r\n]')

        # A fresh unconditional command could run after the chain aborted, so
        # the directories it might have stopped in become candidates again. A
        # conditional command records the current directory as one such stopping
        # point, in case the chain breaks right here.
        if ($isUnconditional -and @($abortDirs).Count -gt 0) {
            $dirs = @(Merge-Directories $dirs $abortDirs)
            $abortDirs = @()
        }
        elseif ($isConditional) {
            $abortDirs = @(Merge-Directories $abortDirs $dirs)
        }

        for ($o = 0; $o -lt $marks.Opens; $o++) {
            $groupStack.Push(@{ Dirs = $dirs; Prev = $prev; Abort = $abortDirs; Unknown = $unknown; DirStack = $dirStack.Clone() })
        }

        $change = if ($core) { Get-DirectoryChange $core $Shell } else { $null }
        if ($change) {
            # Each side of a bash pipeline is its own subshell, so a cd there
            # moves nothing that follows.
            $inPipeline = ($Shell -eq 'Bash') -and (($before -eq '|') -or ($part.After -eq '|'))
            if (-not $inPipeline -and -not $unknown) {
                $result = Resolve-DirectoryChange $change $dirs $prev $dirStack $Shell
                if ($result.Unknown) {
                    $unknown = $true
                } else {
                    $prev = $dirs
                    $dirs = @($result.Dirs)
                }
            }
        }
        elseif ($core -and (Get-GitSubcommand $core)) {
            $segCtx = @(Get-GitContextArgs $core $Shell)
            if ($unknown -and -not (Test-RootedGitContext $segCtx)) {
                # Only a commit or a push needs to know where it is; anything
                # else changes nothing this guard protects.
                foreach ($piece in @(Get-Segments (Expand-GitAlias $core $segCtx) $Shell)) {
                    if ((Get-GitSubcommand $piece) -in @('commit', 'push')) {
                        return $script:UnresolvedDirectoryReason
                    }
                }
            } else {
                # A command after `||` runs only when the one before it failed,
                # so a preceding cd may not have taken effect -- its start (prev)
                # is a candidate alongside where it would have gone.
                $judgeDirs = if ($before -eq '||') { @(Merge-Directories $dirs $prev) } else { @($dirs) }
                foreach ($dir in $judgeDirs) {
                    $base = @('-C', $dir)
                    # Aliases are per repository, so expand where the command runs.
                    $expanded = Expand-GitAlias $core (@($base) + $segCtx)
                    # A shell alias body can itself be several commands.
                    foreach ($piece in @(Get-Segments $expanded $Shell)) {
                        $pieceCore = (Split-GroupMarks $piece $Shell).Core
                        $segments += , @{ Text = $pieceCore; Ctx = (@($base) + @(Get-GitContextArgs $pieceCore $Shell)) }
                    }
                }
            }
        }

        for ($c = 0; $c -lt $marks.Closes; $c++) {
            if ($groupStack.Count -gt 0) {
                $saved = $groupStack.Pop()
                $dirs = $saved.Dirs; $prev = $saved.Prev; $abortDirs = $saved.Abort; $unknown = $saved.Unknown; $dirStack = $saved.DirStack
            }
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

        # A refspec the shell expands -- `git push origin $BRANCH` -- reaches
        # git as whatever the variable held, main included, while the token here
        # is the literal `$BRANCH`. The value cannot be known without running the
        # shell, so the destination is treated as unresolved and refused.
        foreach ($r in $refspecs) {
            if (Test-HasShellExpansion $r) {
                return @"
This push names its destination through a shell expansion ($r), so the guard
cannot tell whether it resolves to 'main'. main only advances through a reviewed
PR.

Name the branch literally instead:
    git push -u origin <type>/<short-slug>

See CLAUDE.md.
"@
            }
        }

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
    $payloadCwd = ''
    if ($payload.PSObject.Properties.Name -contains 'cwd') { $payloadCwd = [string]$payload.cwd }
} catch {
    Allow
}

# Where the shell really is. The Bash tool keeps its working directory between
# calls, so the payload's cwd -- not wherever this hook process happened to be
# started -- is where the first command of the line runs.
$startDir = (Get-Location).ProviderPath
try {
    if ($payloadCwd -and (Test-Path -LiteralPath $payloadCwd -PathType Container)) {
        $startDir = (Resolve-Path -LiteralPath $payloadCwd).ProviderPath
    }
} catch { }

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
        $reason = Get-DenyReason $command $shell $startDir
    } catch {
        # Fail open, as everywhere else here -- but a guard that crashes is
        # indistinguishable from one that approves, so make it possible to see.
        if ($env:KINEMA_GUARD_DEBUG) { [Console]::Error.WriteLine("guard-main: $_") }
        $reason = $null
    }
    if ($reason) { Deny $reason }
}

Allow
