param([string]$Python = "python", [int]$Port = 8502)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$runtimeDirectory = Join-Path $PSScriptRoot "outputs\runtime"
if (Test-Path -LiteralPath $runtimeDirectory) {
    $env:PYTHONPATH = $runtimeDirectory + [IO.Path]::PathSeparator + $env:PYTHONPATH
}
$env:YOLO_CONFIG_DIR = Join-Path $PSScriptRoot "outputs\yolo_config"
& $Python -c "import streamlit, ultralytics, cv2, torch"
if ($LASTEXITCODE -ne 0) { throw "Dependencies unavailable in $Python. See README.md. The old .venv is empty." }
& $Python -m streamlit run app.py --server.address 127.0.0.1 --server.port $Port
exit $LASTEXITCODE
