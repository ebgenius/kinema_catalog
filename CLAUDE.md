# Working on kinema_catalog

## Never commit to `main`

`main` advances **only** through a reviewed PR. Every task that changes files starts on its
own branch:

```bash
git checkout -b <type>/<short-slug>     # fix/ feat/ docs/ chore/
```

Commit there, push the branch, open a **draft** PR, and wait for review before going
further. Do not merge, and do not switch back to `main` to keep working.

Tag pushes (`git push origin v0.1.0`) are fine on `main` — they cut a release and do not
advance the branch.

Both enforcement points are live: the local hook below, and the `main_protect` ruleset on
GitHub. A direct push to `main` is refused by the server, for everyone.

**Locally**, `.claude/hooks/guard-main.ps1` refuses `git commit` and `git push` when they
would advance `main` — while HEAD is `main`, when a push names `main` in any spelling, and
when a push reaches `main` without naming it at all (an upstream of `main`, `push.default` of
`matching`, `--all`/`--branches`/`--mirror`, a `:` or wildcard refspec, or `remote.<name>.push`).
It resolves git aliases first, reads arguments the way the shell hands them to git (a quoted
`"--all"` is `--all`; the value of `-o` is not a flag), and follows the command into whichever
repository it names — `-C`, and `cd`/`pushd`/`Set-Location` earlier on the same line, with
bash subshells undoing theirs. After a directory change it cannot resolve (a variable, a
missing path), it refuses a commit or push rather than guess. Otherwise it fails open: if it
cannot determine the branch, the command proceeds.

The hook fires on **every** `Bash` and `PowerShell` tool call, not only ones that begin with
`git` — a line like `cd ../other-repo && git commit` starts with `cd`, so a `git *` matcher
would never see it. It exits immediately for anything with no commit or push in it. It is
launched with `powershell` (Windows PowerShell 5.1, present on every Windows machine) rather
than `pwsh`, because a missing `pwsh` is a launch failure that emits nothing and so reads as
allow — the tests confirm the script runs under both. On a non-Windows clone the `command` in
`settings.json` must be changed to `pwsh`, and `main_protect` (below) is what should carry the
policy there regardless.

This binds an agent going through Claude Code's tool calls, and nothing else — a person
typing `git push` in a terminal never reaches it. That case is the ruleset's job, which is
why both exist: the hook explains the rule early, at the point of the mistake; the ruleset
is what actually holds.

Failing open is also how it hides a break — a hook that crashes emits no decision, and no
decision means allow, so a broken guard and a working one look identical from outside. After
touching it, run its cases:

```powershell
pwsh -NoProfile -File .claude/hooks/test-guard-main.ps1
```

They cover both directions, because both have gone wrong: a commit message mentioning *main*
was refused as though it were a push, and `git add` on the line above a `git commit` hid the
commit entirely.

**On GitHub**, the `main_protect` ruleset (id 22773751) requires a pull request and blocks
force-pushes and deletion on the default branch, with **no bypass actors** — direct pushes
refused for everyone, including the owner. Merges limited to rebase and squash. Zero
approvals required, since GitHub does not allow self-approval; the PR is the gate, not the
count.

Checking it takes two commands, because neither covers the claim alone:

```bash
# 1. What is actually in force on main. Catches the ruleset being disabled or
#    retargeted away from the default branch — a disabled ruleset's rules do not
#    appear here.
gh api repos/ebgenius/kinema_catalog/rules/branches/main --jq '[.[].type] | join(", ")'
# deletion, non_fast_forward, pull_request

# 2. On what terms, and for whom. This is the half the first command cannot see.
gh api repos/ebgenius/kinema_catalog/rulesets/22773751 --jq \
  '{name, enforcement, bypass_actors: (.bypass_actors | length)}
   + (.rules[] | select(.type == "pull_request") | .parameters
      | {approvals: .required_approving_review_count, merge: .allowed_merge_methods})'
# {"approvals":0,"bypass_actors":0,"enforcement":"active",
#  "merge":["squash","rebase"],"name":"main_protect"}
```

The first command lists rule *types* only. It cannot show bypass actors, and any
other active ruleset carrying the same three rules would print the same line — so on
its own it can never support "for everyone". **`bypass_actors: 0` in the second
command is what that phrase rests on.** (Enforcement mode is not a loophole here:
`evaluate` is an Enterprise-plan feature and this repository cannot use it, so a rule
listed by the first command is in force, not merely being observed.)

`require_extra_approval_for_unattributed_changes` is left at GitHub's default (on). The name
invites a wrong reading, so: it covers pull requests **Copilot opens under its own app
identity**, not commits carrying a `Co-Authored-By` trailer, and GitHub documents it as having
*no effect while a ruleset requires zero approvals*. It is inert here. It only starts to
matter if the required approval count ever rises above zero.

The absence of a bypass is deliberate. A coding agent working here uses the owner's
credentials, so GitHub cannot distinguish the two — an owner bypass would be an agent bypass.
To push directly in an emergency, disable the ruleset in *Settings → Rules* for the moment it
is needed.
