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

This is enforced in two places.

**Locally**, `.claude/hooks/guard-main.ps1` refuses `git commit` and `git push` while HEAD is
`main`, and refuses any push naming `main` as its target from any branch. It fails open: if
it cannot determine the branch, the command proceeds.

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
