# CI

Read before changing CI runners, workflows, or test storage (AGENTS.md, Delivery).

## Workflows

- Scope jobs by path so docs-only changes skip build and test, but keep every required check reporting: a workflow skipped at its trigger never reports and blocks the merge. Filter inside the workflow (job conditions, a final gate job) instead.
- One runner lane per job: each job owns one slot, with its own workspace, ports, and databases, and shares nothing writable with other jobs.

## Storage

- Put anything that calls fsync (test databases, scratch directories, build intermediates) in an ephemeral workspace: tmpfs, a RAM disk, or a container tmpfs mount, created per job and removed at its end. Parallel jobs that fsync to one durable disk queue on its filesystem journal, and wall time grows with job count. One 20 s suite took 337 s across 8 slots.
- Size the tmpfs from the job's measured peak; it counts against RAM. Point the test tool at it by environment variable or flag, not a hard-coded path.
- Keep dependency caches (package stores, toolchains, build caches) on durable disk: they are read-mostly, and losing them costs a rebuild.

## Capacity

- Measure before adding slots: run the same suite at 1, 2, 4, and 8 concurrent jobs and record wall time per job. Add a slot only while per-job time stays near the 1-job time. If it climbs, a shared resource (disk, RAM, CPU, network) is the limit; fix that first.
- Set slots from measured throughput (jobs finished per minute), not queue length. A long queue with flat or falling throughput means too many slots.
- Record the measurement, slot count, and storage in **CI runners** in PROJECT_CONFIG.md.

## Where to run

- Prefer hosted runners. Use self-hosted only where it beats hosted minutes on cost and the host is always on.
- Never run untrusted code (forks, unreviewed branches) on a self-hosted runner.
- Capacity beyond the recorded default can be new spend: ask first (AGENTS.md, Autonomy).
