# Harness evaluation (maintainer-only)

Fixed prompts for a planned smoke test that compares harness revisions on the same
tasks. It is not runnable yet; the fixture, evaluator, and procedure are tracked in
[issue #13](https://github.com/mattsilv/harness/issues/13). Nothing here ships to projects.

## Create prompt

> Create a minimal local to-do app: add a nonblank task, mark it complete or incomplete, delete it, and preserve tasks across reloads. Use the project's configured stack, include executable checks for those behaviors, and report what you verified.

## Update prompt

> Add All, Active, and Completed filters to the existing to-do app. Preserve saved tasks and the existing add, toggle, delete, and reload behavior; add executable checks for filtering and report what you verified.
