# harness

A small, project-agnostic rule set for AI coding agents (Claude Code, Codex, anything
that reads `AGENTS.md`), plus `harness-sync`, which copies it into repos and keeps
them up to date without overwriting local edits.

## What's here

| Path | Purpose | Copied into projects? |
|---|---|---|
| `template/AGENTS.md` | The rules. Loaded in full every session. | yes |
| `template/PROJECT_CONFIG.md` | Per-project defaults; values marked "Set during setup" must be answered. | yes |
| `template/docs/MAINTENANCE.md` | The recurring maintenance audit. | yes |
| `template/docs/languages/*.md` | Language-specific rules, read on demand. | yes |
| `INSTALL.md` | Steps an agent follows to install the harness into a repo. | no |
| `harness-sync` | Installs and updates the template in a repo. | no |
| `REVIEW.md` | Brief for a model reviewing and lightening this harness, plus the review log. | no |
| `RATIONALE.md` | Why each rule exists. | no |
| `AGENTS.md`, `CLAUDE.md` | Rules for agents working on this repo itself. | no |
| `.github/workflows/budget.yml` | CI word budget for `template/AGENTS.md`. | no |
| `LICENSE` | MIT. | no |

## How agents load it (why it's split this way)

- **Always loaded:** in a project, `AGENTS.md` (and `CLAUDE.md`, which imports it with `@AGENTS.md`)
  goes into the context of every session in full. `@` imports and build steps that
  concatenate files don't save context; they only change how the rules are authored.
- **On demand:** a plain link costs nothing until the agent opens it. `AGENTS.md`
  points to `docs/languages/<language>.md` with an explicit trigger ("before editing
  code in a language"), so Python rules don't ride along in a TypeScript session.
- **Rule of thumb:** every-task rules go in `AGENTS.md`; rules that apply only when a
  trigger fires go in a linked file. Add your own language by dropping in
  `docs/languages/<language>.md`. `harness-sync` leaves files it doesn't own alone.

## Adopt it

Tell your coding agent: **"Follow INSTALL.md in github.com/mattsilv/harness."**
The rest of this section is the manual version.

With `harness-sync` (needs Python 3.9+ and git; `gh` for the optional checks):

```bash
git clone https://github.com/mattsilv/harness ~/gh/harness
ln -sf ~/gh/harness/harness-sync ~/.local/bin/harness-sync
cd your-repo && harness-sync init   # never overwrites existing files
```

Without it: copy `template/` into your repo and add `@AGENTS.md` to `CLAUDE.md`.

```bash
harness-sync init          # new or existing repo: write missing files, record baseline
harness-sync check         # silent unless the harness changed, config is unset, conflicts remain, or maintenance is overdue
harness-sync diff          # what the harness changed since this repo last applied it
harness-sync apply [path]  # 3-way merge harness changes into local files, keeping local edits
```

- **Baseline:** `.harness/base/<path>` holds the harness text last applied. Commit it.
  `diff` compares harness to harness, so local additions never show as noise.
- **Approval:** nothing updates on its own. `check` prints a notice; the agent shows
  `diff`, summarizes, and runs `apply` after the operator says yes.
- **Unset values:** any `PROJECT_CONFIG.md` line still reading "Set during setup" is
  reported every session until answered.
- **Maintenance:** `check` reads the tracking issue named in `PROJECT_CONFIG.md` (via
  `gh`, cached 1h) and nags when the audit interval in `docs/MAINTENANCE.md` has passed.
- **CI gate:** with merge policy `auto`, `check` confirms the default branch requires
  status checks and warns to treat merges as `on-request` until it does.
- **Session start:** run `harness-sync check` from a Claude Code `SessionStart` hook
  (e.g. `git rev-parse --git-dir >/dev/null 2>&1 && harness-sync check || true`), or
  tell other agents to run it in their global `AGENTS.md`.
- **Fork:** set `HARNESS_SYNC_REPO` to your fork's clone URL.

## Change it

Open a PR against `template/`. Preview its effect on a project before merging:

```bash
cd your-repo && HARNESS_SYNC_SOURCE=/path/to/harness-branch/template harness-sync diff
```

Every rule needs a line in `RATIONALE.md`. CI fails if `template/AGENTS.md` grows past
its word budget (`.github/workflows/budget.yml`); raising the budget is a deliberate
edit in the same PR.

When a new frontier model ships, or once a quarter, give a model this repo and ask it
to follow [REVIEW.md](REVIEW.md).

Everything here is public: no PII, hostnames, or project specifics.
