<#
.SYNOPSIS
    Cases for guard-main.ps1. Run from anywhere:

        pwsh -NoProfile -File .claude/hooks/test-guard-main.ps1

.DESCRIPTION
    The guard is the only thing standing between a stray `git commit` and an
    unreviewed change on the default branch, and it is easy to break in a way
    that looks fine: a hook that crashes emits nothing, and emitting nothing
    means "allow". So a broken guard and a permissive one are indistinguishable
    from the outside, and both of the bugs these cases were written after had
    exactly that shape.

    Drives the real hook the way Claude Code does -- a PreToolUse payload on
    stdin, a permissionDecision on stdout -- rather than testing its functions
    in isolation, because the wiring is where it went wrong.

    Exits non-zero with a count of misbehaving cases.
#>

param(
    [string]$Hook = (Join-Path $PSScriptRoot 'guard-main.ps1')
)

Set-StrictMode -Version Latest

$script:failures = 0

function Invoke-Hook([string]$Command, [string]$Shell = 'Bash', [string]$Cwd) {
    <#
        Returns 'allow', 'deny', or a description of why neither.

        The hook exits 0 whatever it decides, and says "deny" by printing JSON.
        So the two failure shapes are a nonzero exit, and output that is neither
        empty nor a decision -- both of which otherwise read as "allow", which
        is the direction that hides a broken guard.

        Checked structurally rather than by matching error wording: a guess at
        the wording misses whatever phrasing was not anticipated, and
        `Cannot find path ...` is one that would have slipped through.
    #>
    # tool_name and cwd are part of the real payload: the first decides which
    # character continues a line, the second is where a `cd` starts from. The
    # cases carry both, with cwd defaulting to where the hook is launched.
    if (-not $Cwd) { $Cwd = (Get-Location).ProviderPath }
    $payload = @{ tool_name = $Shell; cwd = $Cwd; tool_input = @{ command = $Command } } | ConvertTo-Json -Compress
    $out = $payload | & pwsh -NoProfile -File $Hook 2>&1 | Out-String
    $code = $LASTEXITCODE

    if ($code -ne 0) { return "hook exited $code : $(($out -split "`n")[0].Trim())" }
    if ([string]::IsNullOrWhiteSpace($out)) { return 'allow' }
    try {
        $decision = ($out | ConvertFrom-Json).hookSpecificOutput.permissionDecision
    } catch {
        return "unparseable output: $(($out -split "`n")[0].Trim())"
    }
    if ($decision -eq 'deny') { return 'deny' }
    if ($decision -eq 'allow') { return 'allow' }
    return "unexpected decision '$decision'"
}

function Check([string]$Name, [string]$Command, [bool]$ShouldDeny, [string]$In, [string]$Shell = 'Bash', [string]$Cwd) {
    $expected = if ($ShouldDeny) { 'deny' } else { 'allow' }
    if ($In) { Push-Location $In }
    try {
        $actual = Invoke-Hook $Command $Shell $Cwd
    } finally {
        if ($In) { Pop-Location }
    }
    $ok = ($actual -eq $expected)
    if (-not $ok) { $script:failures++ }
    "{0} {1,-52} expected={2,-5} got={3}" -f `
        $(if ($ok) { '  ok  ' } else { ' FAIL ' }), $Name, $expected, $actual
}

function New-RepoOnBranch([string]$Branch) {
    <#
        A throwaway repository sitting on a given branch.

        The interesting half of this guard only acts when HEAD is the default
        branch, and the workflow it enforces means the suite is always run from
        a feature branch -- where every such case is allowed for the wrong
        reason and proves nothing. `git init -b` gives a real one to test
        against without touching the checkout.

        No commit is needed: symbolic-ref reports the branch of an empty repo,
        which is the case the hook was written to handle.
    #>
    $dir = Join-Path ([IO.Path]::GetTempPath()) ("guardtest-" + [guid]::NewGuid().ToString('N'))
    & git init --quiet -b $Branch $dir 2>&1 | Out-Null
    return $dir
}

$branch = (& git symbolic-ref --short --quiet HEAD 2>$null)
"=== guard-main.ps1, from branch '$branch' ==="
""

# --- refused from any branch, because they advance main ---------------------
Check 'push origin main' 'git push origin main' $true
Check 'push origin HEAD:main' 'git push origin HEAD:main' $true
Check 'push origin HEAD:refs/heads/main' 'git push origin HEAD:refs/heads/main' $true
Check 'force-push +main' 'git push origin +main' $true
Check 'quoted ref: push origin "main"' 'git push origin "main"' $true
Check 'a tag cannot smuggle main alongside it' 'git push origin v0.3.1 main' $true

# --- allowed -----------------------------------------------------------------
Check 'push a feature branch' 'git push -u origin feat/thing' $false
Check 'a branch merely named like main' 'git push origin fix/domain-main' $false
Check 'dry run changes nothing' 'git push --dry-run origin main' $false
Check 'read-only command mentioning main' 'git log --grep=main' $false
Check 'commit-graph is not commit' 'git commit-graph write' $false

# --- a commit message is prose, not command structure ------------------------
# Assembled from arrays: a here-string containing a here-string terminates the
# outer one, which is the same class of confusion the hook itself had.
$marker = '@' + "'"
$endMarker = "'" + '@'

Check 'message mentioning main, while pushing a branch' (@(
    'git add -A'
    "git commit -q -m $marker"
    'Fix the thing'
    ''
    'Now on the main thread, since the import blocks.'
    $endMarker
    'git push'
) -join "`n") $false

Check 'message quoting a push-to-main instruction' (@(
    "git commit -m $marker"
    'Docs: describe releasing'
    ''
    '    git push origin main'
    ''
    'is how a release used to be cut.'
    $endMarker
) -join "`n") $false

# --- quote concatenation, which the shell resolves before git sees it --------
Check 'push origin HEAD:"main"' 'git push origin HEAD:"main"' $true
Check 'push origin m"ai"n' 'git push origin m"ai"n' $true
Check "push origin 'main'" "git push origin 'main'" $true

# --- a continued line is one command, not two --------------------------------
# Splitting on every newline put the destination in a segment of its own, where
# nothing was looking for it. Both shells' continuation characters, since either
# may be what reaches the hook.
$backslash = [char]92
$backtick = [char]96

Check 'push continued with a backslash (bash)' (@(
    "git push origin $backslash"
    'main'
) -join "`n") $true

# Declared as PowerShell input: the backtick only continues a line there, and
# the hook now applies each shell's own rule rather than both at once.
Check 'push continued with a backtick (PowerShell)' (@(
    "git push origin $backtick"
    'main'
) -join "`n") $true -Shell 'PowerShell'

Check 'continuation with trailing space before the newline' (@(
    "git push origin $backslash  "
    'main'
) -join "`n") $true

# The join must not swallow a real boundary: a backslash inside a token is not
# a continuation unless the newline follows it directly.
Check 'a path containing a backslash is not a continuation' (@(
    'git commit -m "see C:\ws\notes.md"'
    'git push -u origin feat/thing'
) -join "`n") $false

# --- the branch-sensitive half, tested against a repo that is on main --------
# Run from this checkout these are allowed for the wrong reason: the workflow
# keeps HEAD on a feature branch, so every case below would pass no matter what
# the hook did. Throwaway repositories give both branches.
$mainRepo = New-RepoOnBranch 'main'
$featureRepo = New-RepoOnBranch 'feat/thing'
try {
    $addThenCommit = @('git add -A', 'git commit -m "wip"') -join "`n"

    # The headline regression: `git add` on the line above used to hide the
    # commit entirely, because segments did not split on newlines.
    Check 'add then commit, on main' $addThenCommit $true -In $mainRepo
    Check 'add then commit, on a feature branch' $addThenCommit $false -In $featureRepo

    Check 'plain commit on main' 'git commit -m "wip"' $true -In $mainRepo
    Check 'plain commit on a feature branch' 'git commit -m "wip"' $false -In $featureRepo

    # A commit message mentioning the branch is still just prose, on main too.
    Check 'message mentioning main, committing on a feature branch' (@(
        "git commit -m $marker"
        'Now on the main thread, since the import blocks.'
        $endMarker
    ) -join "`n") $false -In $featureRepo

    Check 'push on main with no refspec' 'git push' $true -In $mainRepo
    Check 'dry run on main' 'git push --dry-run' $false -In $mainRepo
} finally {
    Remove-Item -Recurse -Force $mainRepo, $featureRepo -ErrorAction SilentlyContinue
}

# --- a push that never names main, but lands on it ---------------------------
# The suite used to test the refspec-less push only from main, where it is caught
# for a reason that has nothing to do with the refspec. From a feature branch the
# same command reaches main whenever configuration says so, and every check in
# the hook passed it: the text holds no "main", and HEAD is not main.
function New-RepoWithMain([hashtable]$Config) {
    <#
        A repo with a real commit, a main branch and a feat/x checkout.

        A commit is needed here, unlike the empty repos above: these cases turn on
        whether refs/heads/main exists, and on branch.<name>.merge, neither of
        which means anything before something has been committed.
    #>
    $dir = Join-Path ([IO.Path]::GetTempPath()) ("guardtest-" + [guid]::NewGuid().ToString('N'))
    & git init --quiet -b main $dir 2>&1 | Out-Null
    Push-Location $dir
    try {
        & git config user.email 'test@example.invalid' 2>&1 | Out-Null
        & git config user.name 'guard test' 2>&1 | Out-Null
        Set-Content -Path (Join-Path $dir 'f.txt') -Value 'x'
        & git add -A 2>&1 | Out-Null
        & git commit -qm init 2>&1 | Out-Null
        & git checkout -q -b feat/x 2>&1 | Out-Null
        if ($Config) {
            foreach ($key in $Config.Keys) { & git config $key $Config[$key] 2>&1 | Out-Null }
        }
    } finally {
        Pop-Location
    }
    return $dir
}

$upstreamIsMain = New-RepoWithMain @{
    'push.default'          = 'upstream'
    'branch.feat/x.remote'  = 'origin'
    'branch.feat/x.merge'   = 'refs/heads/main'
}
$upstreamIsSelf = New-RepoWithMain @{
    'push.default'          = 'upstream'
    'branch.feat/x.remote'  = 'origin'
    'branch.feat/x.merge'   = 'refs/heads/feat/x'
}
$plainSimple = New-RepoWithMain @{ 'push.default' = 'simple' }
$matching    = New-RepoWithMain @{ 'push.default' = 'matching' }

try {
    # The bypass: git reports this one as refs/heads/feat/x:refs/heads/main.
    Check 'bare push whose upstream is main' 'git push' $true -In $upstreamIsMain

    # The same setting must not condemn an ordinary branch.
    Check 'bare push whose upstream is itself' 'git push' $false -In $upstreamIsSelf
    Check 'bare push under push.default=simple' 'git push' $false -In $plainSimple

    # matching pushes every branch that exists on the remote, main included,
    # regardless of which one is checked out.
    Check 'bare push under push.default=matching' 'git push' $true -In $matching

    # --all and --mirror carry main from anywhere.
    Check 'push --all from a feature branch' 'git push --all origin' $true -In $plainSimple
    Check 'push --mirror from a feature branch' 'git push --mirror origin' $true -In $plainSimple

    # Naming a branch explicitly still decides it, whatever the config says.
    Check 'explicit branch beats an upstream of main' 'git push origin feat/x' $false -In $upstreamIsMain
} finally {
    Remove-Item -Recurse -Force $upstreamIsMain, $upstreamIsSelf, $plainSimple, $matching `
        -ErrorAction SilentlyContinue
}

# --- review findings -------------------------------------------------------
# Every case below is a command that reached main while the guard said allow.

$aliasRepo = New-RepoWithMain @{
    'alias.p'    = 'push'
    'alias.yolo' = '!git push origin main'
}
$otherOnMain = New-RepoWithMain @{}          # left checked out on feat/x
$pushConfig  = New-RepoWithMain @{
    'remote.origin.push' = 'refs/heads/*:refs/heads/*'
}

# Checked out on main, and carrying a real tag: the tag carve-out has to be
# tested against a tag git can actually verify.
$mainWithTag = New-RepoWithMain @{}
& git -C $mainWithTag checkout -q main 2>&1 | Out-Null
& git -C $mainWithTag tag v1.0 2>&1 | Out-Null

# The repository `git -C` points at, sitting on main while the caller is not.
$mainRepoForC = New-RepoWithMain @{}
& git -C $mainRepoForC checkout -q main 2>&1 | Out-Null

try {
    # An alias hid the subcommand: `git p ...` was neither commit nor push.
    Check 'alias expands to a push to main' 'git p origin main' $true -In $aliasRepo
    Check 'shell alias hiding a push to main' 'git yolo' $true -In $aliasRepo
    Check 'an alias that is not a push is still fine' 'git p origin feat/x' $false -In $aliasRepo

    # Every form that carries all branches, none of which names main.
    Check 'push --branches' 'git push --branches origin' $true -In $otherOnMain
    Check 'matching refspec ":"' 'git push origin :' $true -In $otherOnMain
    Check 'wildcard refspec' 'git push origin refs/heads/*:refs/heads/*' $true -In $otherOnMain

    # remote.<name>.push decides a bare push before push.default is consulted.
    Check 'bare push with a wildcard remote.push' 'git push' $true -In $pushConfig

    # A tag anywhere used to exempt the whole push, HEAD included.
    Check 'tag plus HEAD on main' 'git push origin v1.0 HEAD' $true -In $mainWithTag
    Check 'a genuine tag-only push on main' 'git push origin v1.0' $false -In $mainWithTag
    Check 'pushing only tags on main' 'git push --tags origin' $false -In $mainWithTag

    # --dry-run was matched against the whole command, prose included.
    Check 'commit whose message mentions --dry-run' `
        'git commit -m "remember to --dry-run first"' $true -In $mainWithTag
    Check 'a real dry run is still allowed' 'git push --dry-run origin main' $false -In $mainWithTag

    # -C names another repository; the probes must follow it there.
    Check 'commit into another repo that is on main' `
        "git -C `"$mainRepoForC`" commit -m wip" $true -In $otherOnMain

    # PowerShell does not continue a line on a backslash, so the two halves are
    # separate commands and the push must still be seen.
    Check 'backslash newline under PowerShell' (@(
        'git status \'
        'git push origin main'
    ) -join "`n") $true -In $otherOnMain -Shell 'PowerShell'

    # ...while bash does continue, and the joined line is one push to main.
    Check 'backslash newline under bash' (@(
        'git push origin \'
        'main'
    ) -join "`n") $true -In $otherOnMain -Shell 'Bash'
} finally {
    Remove-Item -Recurse -Force $aliasRepo, $otherOnMain, $pushConfig, $mainWithTag, $mainRepoForC `
        -ErrorAction SilentlyContinue
}

# --- round three: quoting, option values, and where a command runs ----------
# Each of these reached main, or was refused for text git never sees.

$featureRepo = New-RepoWithMain @{}                     # on feat/x, main exists
$mainRepo    = New-RepoWithMain @{}
& git -C $mainRepo checkout -q main 2>&1 | Out-Null     # on main
$parentDir   = Split-Path -Parent $mainRepo
$mainLeaf    = Split-Path -Leaf $mainRepo

# Paths the way a bash command writes them: forward slashes, and the /c/...
# form Git Bash uses on Windows.
$mainFwd    = $mainRepo -replace '\\', '/'
$featureFwd = $featureRepo -replace '\\', '/'
$parentFwd  = $parentDir -replace '\\', '/'
$mainMsys   = if ($mainFwd -match '^([A-Za-z]):(.*)$') { '/' + $Matches[1].ToLower() + $Matches[2] } else { $mainFwd }

# A repository whose path contains a space, so the quote-aware tokeniser is
# tested on a real one rather than only on a temp root that happens to have none.
$spacedParent = Join-Path ([IO.Path]::GetTempPath()) ("guard space " + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $spacedParent | Out-Null
$spacedRepo = Join-Path $spacedParent 'repo on main'
& git init --quiet -b main $spacedRepo 2>&1 | Out-Null
& git -C $spacedRepo config user.email 'test@example.invalid' 2>&1 | Out-Null
& git -C $spacedRepo config user.name 'guard test' 2>&1 | Out-Null
Set-Content -Path (Join-Path $spacedRepo 'f.txt') -Value 'x'
& git -C $spacedRepo add -A 2>&1 | Out-Null
& git -C $spacedRepo commit -qm init 2>&1 | Out-Null
$spacedFwd = $spacedRepo -replace '\\', '/'

try {
    # A quoted flag is still the flag once the shell hands it to git.
    Check 'quoted --all' 'git push origin "--all"' $true -In $featureRepo
    Check 'quoted --mirror' "git push origin '--mirror'" $true -In $featureRepo
    Check 'quoted --branches' 'git push "--branches" origin' $true -In $featureRepo

    # ...and a flag's name inside one quoted value is not the flag.
    Check 'push option whose value mentions --all' `
        'git push -u origin feat/x --push-option "skip --all checks"' $false -In $featureRepo

    # After -o, "-n" is the option's value and git really pushes.
    Check 'push -o -n on main is not a dry run' 'git push -o -n' $true -In $mainRepo
    Check 'push -o --dry-run on main is not a dry run' 'git push -o --dry-run' $true -In $mainRepo
    Check 'a real -n dry run on main' 'git push -n' $false -In $mainRepo

    # A refspec the shell expands is unknowable, so refused.
    Check 'push origin $BRANCH' 'git status; BRANCH=main; git push origin $BRANCH' $true -In $featureRepo
    Check 'push origin ${BRANCH}' 'git push origin ${BRANCH}' $true -In $featureRepo
    Check 'push origin $(cat b)' 'git push origin $(cat branchfile)' $true -In $featureRepo
    # ...but a literal refspec next to an unrelated expansion elsewhere is fine.
    Check 'expansion in a message, literal refspec' 'git push -u origin feat/x -o "run $CI"' $false -In $featureRepo

    # Interpolated paths are single-quoted so a space in them survives, which is
    # also what a careful caller would write.
    Check 'bash: cd into a repo on main, then commit' "cd '$mainFwd' && git commit -m wip" $true -In $featureRepo
    Check 'bash: cd into a path with spaces, then commit' "cd '$spacedFwd' && git commit -m wip" $true -In $featureRepo
    Check 'pwsh: Set-Location into a repo on main; commit' "Set-Location '$mainRepo'; git commit -m wip" $true `
        -In $featureRepo -Shell 'PowerShell'
    # The other direction: leaving main for a feature repo must not be refused
    # because of where the command started.
    Check 'bash: cd out of main into a feature repo, then commit' "cd '$featureFwd' && git commit -m wip" $false -In $mainRepo

    # A subshell's cd applies inside it and is undone after it.
    Check 'bash: commit inside a subshell that cd-ed to main' "(cd '$mainFwd' && git commit -m wip)" $true -In $featureRepo
    Check 'bash: subshell cd to main does not leak out' "(cd '$mainFwd') && git commit -m wip" $false -In $featureRepo
    Check 'bash: subshell cd away from main does not leak out' "(cd '$featureFwd') && git commit -m wip" $true -In $mainRepo
    # An escaped ) inside the subshell is echo's argument, not the end of it.
    Check 'bash: escaped ) does not close the subshell early' "(cd '$mainFwd' && echo \) && git commit -m wip)" $true -In $featureRepo

    # pushd moves; popd moves back.
    Check 'bash: pushd into a repo on main, then commit' "pushd '$mainFwd' && git commit -m wip" $true -In $featureRepo
    Check 'bash: pushd then popd, then commit' "pushd '$mainFwd' && popd && git commit -m wip" $false -In $featureRepo

    # A relative -C is relative to wherever the cd left the shell.
    Check 'bash: relative -C after cd' "cd '$parentFwd' && git -C '$mainLeaf' commit -m wip" $true -In $featureRepo

    # Git Bash writes C:\... as /c/...; that is still the repository on main.
    Check 'bash: cd using the /c/ path form' "cd '$mainMsys' && git commit -m wip" $true -In $featureRepo

    # A cd that cannot be resolved without running the shell: refuse a commit or
    # push after it, but leave read-only commands alone.
    Check 'bash: cd to a variable, then commit' 'cd "$REPO" && git commit -m wip' $true -In $featureRepo
    Check 'bash: cd to a variable, then a read-only command' 'cd "$REPO" && git status' $false -In $featureRepo

    # `a || b` runs b only if a failed, so both directories are candidates and
    # either one on main is enough to refuse.
    Check 'bash: cd to main || commit is judged in both places' "cd '$mainFwd' || git commit -m wip" $true -In $featureRepo

    # A conditional cd may be skipped, so the directory it would have left is
    # still a candidate: on main, a skipped `cd feature` must not launder a
    # commit into looking like a feature-branch one.
    Check 'bash: skipped cd (&& false && cd) still judged on main' `
        "git status && false && cd '$featureFwd'; git commit -m wip" $true -In $mainRepo
    Check 'pwsh: skipped Set-Location still judged on main' `
        "if (`$false) { Set-Location '$featureRepo' }; git commit -m wip" $true -In $mainRepo -Shell 'PowerShell'

    # The payload's cwd is where the shell really is, not where the hook starts.
    Check 'payload cwd on main, hook launched elsewhere' 'git commit -m wip' $true -In $featureRepo -Cwd $mainRepo

    # A subshell around the whole push used to hide the subcommand.
    Check 'push to main wrapped in a subshell' '(git push origin main)' $true -In $featureRepo
} finally {
    Remove-Item -Recurse -Force $featureRepo, $mainRepo, $spacedParent -ErrorAction SilentlyContinue
}

""
if ($script:failures -eq 0) {
    'all cases behaved'
    exit 0
}
"$($script:failures) case(s) wrong"
exit $script:failures
