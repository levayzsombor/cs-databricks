# Dev Container Notes

This workspace uses a host-side Docker readiness check before Dev Containers starts.

## Why this exists

On some machines, VS Code can try to start the dev container before Docker Desktop finishes initializing the Linux engine. That causes errors like missing Docker named pipes or daemon connection failures.

## How it works

The dev container config uses `initializeCommand` with OS-specific commands:

- Windows: runs `.devcontainer/wait-for-docker.ps1`
- Linux/macOS: runs `.devcontainer/wait-for-docker.sh`

Each script:

- Polls `docker version` until the server is reachable
- Waits up to 90 seconds
- Exits with code `1` on timeout so startup fails fast with a clear reason

## Manual checks

Use these commands on the host:

```powershell
docker version --format "Client={{.Client.Version}} Server={{if .Server}}{{.Server.Version}}{{else}}NONE{{end}}"
docker info --format "Engine={{.ServerVersion}} OSType={{.OSType}} Name={{.Name}}"
```

Ready state means `Server` is not `NONE` and `docker info` returns engine details.

## If startup still fails

1. Ensure Docker Desktop shows Engine running.
2. Run `Dev Containers: Rebuild and Reopen in Container`.
3. If needed, run `Dev Containers: Rebuild Container Without Cache`.
4. Check `Dev Containers: Show Container Log` for the first failing step.
