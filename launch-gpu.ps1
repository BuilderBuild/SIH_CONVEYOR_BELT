param([int]$Port = 8502)
$ErrorActionPreference = "Stop"
$gpuPython = Join-Path $PSScriptRoot ".venv-conveyx-gpu\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $gpuPython)) { throw "The approved ConveyX GPU environment is not installed." }
& $gpuPython -c "import torch; assert torch.cuda.is_available(), 'CUDA is unavailable'; print(torch.__version__, torch.cuda.get_device_name(0))"
if ($LASTEXITCODE -ne 0) { throw "CUDA verification failed; use launch.ps1 with CPU settings." }
& (Join-Path $PSScriptRoot "launch.ps1") -Python $gpuPython -Port $Port
exit $LASTEXITCODE
