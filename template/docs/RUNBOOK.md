# Runbook

The working commands for this project, recorded once so each worktree and session doesn't rediscover them. Keep each entry to the exact command and a line on when to use it; replace the guidance under a heading once it's filled.

## Bootstrap a worktree

Many worktrees share one machine. Derive every per-worktree value (ports, base URL) from one identifier such as the worktree path, keep local state (database, caches) relative to the checkout, and wrap install, local database setup, and migrations in one idempotent repo script.

## Run locally

The exact command that starts the app, in a second idempotent repo script. Prefer injecting secrets at runtime from the secrets manager over a local env file, and pass per-worktree values as flags rather than stored copies.

## Migrations

How to create and apply one locally and remotely. Migration ids must not collide across branches: use a timestamp prefix or a check in CI.

## Remote commands

How the secrets manager feeds the hosting and database CLIs, with the one invocation form that works.

## Wait on CI and finish a PR

How to wait for checks and confirm the merge and deploy in this runtime and host.

## Subagents and review

How to launch a T3 subagent and a PR review in this runtime.

## Known vendor errors

One line each: date, error text, cause, fix.
