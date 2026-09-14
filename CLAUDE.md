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

There are two intended enforcement points, but **only the local hook is live today** — the
GitHub ruleset described below is not configured on this repository. Treat a direct terminal
push as possible, not blocked.

**Locally**, `.claude/hooks/guard-main.ps1` refuses `git commit` and `git push` when they
would advance `main` — while HEAD is `main`, when a push names `main` in any spelling, and
when a push reaches `main` without naming it at all (an upstream of `main`, `push.default` of
`matching`, `--all`/`--branches`/`--mirror`, a `:` or wildcard refspec, or `remote.<name>.push`).
It resolves git aliases first and follows `-C` into whichever repository the command names.
It fails open: if it cannot determine the branch, the command proceeds.

This binds an agent going through Claude Code's tool calls. It does nothing about a person
typing `git push` in a terminal.

Failing open is also how it hides a break — a hook that crashes emits no decision, and no
decision means allow, so a broken guard and a working one look identical from outside. After
touching it, run its cases:

```powershell
pwsh -NoProfile -File .claude/hooks/test-guard-main.ps1
```

They cover both directions, because both have gone wrong: a commit message mentioning *main*
was refused as though it were a push, and `git add` on the line above a `git commit` hid the
commit entirely.

**On GitHub**, a `main_protect` ruleset should require a pull request and block force-pushes
and deletion on the default branch, with **no bypass actors** — direct pushes refused for
everyone, including the owner. Merges limited to rebase and squash. Zero approvals required,
since GitHub does not allow self-approval; the PR is the gate, not the count.

> **Not yet configured on this repository.** `gh api repos/ebgenius/kinema_catalog/rulesets`
> returns empty and `main` has no branch protection, so the local hook is currently the only
> thing enforcing any of this — and a hook only binds the agent, not a person with a terminal.
> Until the ruleset exists, treat the rule above as a convention rather than a guarantee.

The absence of a bypass is deliberate. A coding agent working here uses the owner's
credentials, so GitHub cannot distinguish the two — an owner bypass would be an agent bypass.
To push directly in an emergency, disable the ruleset in *Settings → Rules* for the moment it
is needed.
