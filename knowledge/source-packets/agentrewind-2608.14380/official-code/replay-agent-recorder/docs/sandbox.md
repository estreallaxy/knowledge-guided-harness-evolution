# Sandbox (experimental alpha)

`replay sandbox` runs an agent's target workspace in a Docker or Podman
container and records checkpoints for the parts of the world that Replay can
observe. It is an experimental alpha feature: interfaces and recovery details
may change between releases.

Sandbox is not a virtual machine snapshot and is not an unrestricted security
boundary. Use it with a disposable workspace and a container runtime you
control.

## Quickstart

```bash
mkdir demo-ws
printf 'v1\n' > demo-ws/app.txt

SID=$(replay sandbox up --image alpine:3.20 --workspace ./demo-ws)
replay sandbox exec --session "$SID" -- 'echo cached > /tmp/cache.txt'
replay sandbox exec --session "$SID" -- 'echo v2 > app.txt'
replay sandbox checkpoint --session "$SID" --label 'after change'
replay sandbox timeline --session "$SID"
replay sandbox goto --session "$SID" ckpt_000000 --reason 'restore the demo'
replay sandbox diff --session "$SID" ckpt_000000 ckpt_000001
replay sandbox down --session "$SID" --purge
```

The session directory is stored under `.replay/sandbox/` unless an explicit
root is supplied. Add that directory to your own ignore rules when it should
never be committed.

## What a checkpoint contains

The checkpoint registry is append-only. Each row records the session head,
workspace tree, container rootfs handle, process manifest, and side-effect
ledger watermark available at that point in time.

- **Files**: declared Git workspace files can be compared and restored.
- **Rootfs**: package installs, `/tmp`, and other writes inside the container
  are restored by recreating the container from a committed image.
- **Processes**: the process table is classified as restartable or lost.
  Restart is best effort and does not preserve live memory.
- **Ledger**: observable network and mutating command effects are recorded for
  review; they are not undone by a rewind.

`goto` moves backward, forward, or sideways through the checkpoint DAG. A
pre-navigation checkpoint is written first, so a navigation operation can be
reviewed and itself reversed. `rewind` remains an alias for `goto` in the CLI.
`fork` creates an independent child session from a checkpoint. `pause` and
`resume` control the container process group.

## Docker and Podman

Docker is the default runtime. Select rootful Podman explicitly:

```bash
replay sandbox up --runtime podman --image alpine:3.20 --workspace ./demo-ws
```

The runtime, image cache, permissions, networking, and storage limits belong
to the user. Replay does not download a private image or configure a remote
daemon. Real runtime tests are opt-in and are not part of the default offline
test command.

## External effects and strict ledger mode

The ledger can classify requests and mutating commands as reversible,
irreversible, or opaque. It never claims that an HTTP request, publication, or
other external action has been cancelled. With strict mode, a navigation that
would roll over an irreversible or opaque entry requires an explicit force
decision:

```bash
replay sandbox up --strict-ledger --image alpine:3.20 --workspace ./demo-ws
```

Request bodies are not stored by the built-in proxy. TLS payloads remain
opaque unless the client itself exposes metadata. Programs that bypass the
configured proxy are not guaranteed to appear in the ledger.

## MCP and `wrap`

The MCP server exposes timeline, diff, checkpoint, navigation, fork, pause,
and resume tools over stdio:

```bash
replay sandbox mcp --session "$SID"
```

`replay wrap --workspace . -- claude` installs the MCP entry and hook files
needed by a Claude Code session, then launches the command with the session
environment. Hook handling is fail-open: if the runtime is unavailable,
commands can run on the host and no checkpoint is taken. Review generated
`.mcp.json` and `.claude/settings.local.json` before committing them.

## Current limits

- CRIU-style live process-memory restoration is not a stable alpha capability.
- A recreated container can lose interactive shells and in-memory state.
- Service restart is best effort and environment variables are not captured as
  a portable process snapshot.
- Files outside declared workspaces and external side effects are outside the
  rollback guarantee.
- Image layers consume storage; use `replay sandbox gc` or start a new session
  when a long run grows large.
- Sandbox should not be presented as a complete VM snapshot, a network
  isolation guarantee, or a way to revoke actions already sent to the world.

The fake-runner tests in `replay/tests/test_sandbox_*.py` exercise the session,
registry, domains, ledger, MCP, navigation, GC, and CLI contracts without a
running container. Docker/Podman and third-party CLI checks are intentionally
separate.
