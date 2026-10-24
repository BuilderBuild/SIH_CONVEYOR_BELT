param(
    [Parameter(Mandatory = $true)]
    [string[]]$AllowedEmail,
    [ValidateRange(1, 65535)]
    [int]$Port = 8502,
    [switch]$Background
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$addresses = @($AllowedEmail | ForEach-Object { $_.Split(',') } | ForEach-Object { $_.Trim() })
if ($addresses.Count -eq 0) { throw "Provide at least one allowed email address." }
foreach ($address in $addresses) {
    try { $parsedAddress = [System.Net.Mail.MailAddress]::new($address) }
    catch { throw "Invalid allowed email address: $address" }
    if ($parsedAddress.Address -ne $address) { throw "Use a plain email address without a display name: $address" }
}

$clientCommand = Get-Command cloudflared -ErrorAction SilentlyContinue
$client = if ($clientCommand) { $clientCommand.Source } else { Join-Path $PSScriptRoot "tools\bin\cloudflared.exe" }
if (-not (Test-Path -LiteralPath $client)) {
    throw "Install the official cloudflared client or place it at tools\bin\cloudflared.exe. Instructions: PC_HOSTING.md"
}

$clientHelp = (& $client tunnel --help 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0 -or $clientHelp -notmatch '--allowed-mail') {
    throw "This cloudflared build does not advertise protected Quick Tunnels (--allowed-mail). Update from the official source. An unprotected tunnel will not be started."
}

$origin = "http://127.0.0.1:$Port"
try {
    $health = Invoke-WebRequest -Uri "$origin/_stcore/health" -TimeoutSec 5 -UseBasicParsing
    if ($health.StatusCode -ne 200) { throw "Unexpected health status: $($health.StatusCode)" }
} catch {
    throw "ConveyX is not responding on port $Port. Start .\launch-gpu.ps1 -Port $Port first. $($_.Exception.Message)"
}

Write-Host "Sharing ConveyX through a temporary, email-protected HTTPS tunnel."
if ($Background) {
    $tunnelDirectory = Join-Path $PSScriptRoot 'outputs\tunnel'
    New-Item -ItemType Directory -Force -Path $tunnelDirectory | Out-Null
    $statePath = Join-Path $tunnelDirectory 'session.json'
    if (Test-Path -LiteralPath $statePath) {
        $previous = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        if ($previous.status -ne 'stopped' -and (Get-Process -Id $previous.process_id -ErrorAction SilentlyContinue)) {
            throw "A tracked tunnel is already active. Run .\stop-sharing.ps1 before changing allowed addresses."
        }
    }
    $runId = [guid]::NewGuid().ToString('N')
    $stdoutLog = Join-Path $tunnelDirectory ($runId + '.stdout.log')
    $stderrLog = Join-Path $tunnelDirectory ($runId + '.stderr.log')
    $process = Start-Process -FilePath $client -ArgumentList @('tunnel','--url',$origin,'--allowed-mail',($addresses -join ',')) -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru
    $state = @{ process_id=$process.Id; client_path=$client; origin=$origin; allowed_emails=$addresses;
                started_at=[DateTime]::UtcNow.ToString('o'); stdout_log=$stdoutLog; stderr_log=$stderrLog; status='starting' }
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host "Started protected background tunnel PID $($process.Id). Run .\stop-sharing.ps1 to end public access."
    Write-Host "Connection details and logs: $statePath"
    exit 0
}
Write-Host "Only the configured email addresses should be admitted. Keep this terminal and ConveyX running."
Write-Host "Stop with Ctrl+C. The public URL expires when this tunnel stops."
& $client tunnel --url $origin --allowed-mail ($addresses -join ',')
exit $LASTEXITCODE
