$ErrorActionPreference = "Stop"

$timeoutSeconds = 90
$started = Get-Date

Write-Host "Waiting for Docker engine to become ready..."

while ($true) {
    try {
        $ready = docker version --format "{{if .Server}}ready{{else}}not-ready{{end}}" 2>$null
        if ($LASTEXITCODE -eq 0 -and "$ready" -eq "ready") {
            Write-Host "Docker engine is ready."
            exit 0
        }
    }
    catch {
        # Ignore transient startup failures while Docker Desktop initializes.
    }

    $elapsed = (Get-Date) - $started
    if ($elapsed.TotalSeconds -ge $timeoutSeconds) {
        Write-Error "Docker did not become ready within $timeoutSeconds seconds."
        exit 1
    }

    Start-Sleep -Seconds 1
}
