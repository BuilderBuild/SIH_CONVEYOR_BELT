$ErrorActionPreference = "Stop"
$statePath = Join-Path $PSScriptRoot "outputs\tunnel\session.json"
if (-not (Test-Path -LiteralPath $statePath)) {
    Write-Host "No tracked background tunnel. For a foreground tunnel, press Ctrl+C in its terminal."
    exit 0
}
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$tunnelProcess = Get-Process -Id $state.process_id -ErrorAction SilentlyContinue
if ($tunnelProcess) {
    $details = Get-CimInstance Win32_Process -Filter "ProcessId=$($state.process_id)"
    # PowerShell 7 may deserialize ISO JSON timestamps directly as DateTime.
    # Avoid a culture-dependent DateTime -> string -> DateTime round trip.
    $started = if ($state.started_at -is [DateTime]) {
        $state.started_at.ToUniversalTime()
    } elseif ($state.started_at -is [DateTimeOffset]) {
        $state.started_at.UtcDateTime
    } else {
        [DateTimeOffset]::Parse([string]$state.started_at, [Globalization.CultureInfo]::InvariantCulture).UtcDateTime
    }
    $timeDifference = [Math]::Abs(($tunnelProcess.StartTime.ToUniversalTime() - $started).TotalSeconds)
    if (-not [string]::Equals($details.ExecutablePath, $state.client_path, [StringComparison]::OrdinalIgnoreCase) -or
        -not $details.CommandLine.Contains($state.origin) -or
        -not $details.CommandLine.Contains('--allowed-mail') -or $timeDifference -gt 15) {
        throw "The recorded PID no longer matches this protected tunnel. No process was stopped."
    }
    Stop-Process -Id $state.process_id -ErrorAction Stop
}
$state.status = 'stopped'
$state | Add-Member -NotePropertyName stopped_at -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
$state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8
Write-Host "Public sharing stopped. The local ConveyX application is still available separately."
