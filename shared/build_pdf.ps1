param(
    [Parameter(Mandatory = $true)][string]$Html,
    [string]$Pdf
)
# Render an HTML report to PDF with the Edge headless engine (no extra toolchain).
$ErrorActionPreference = 'Stop'
$htmlPath = (Resolve-Path -LiteralPath $Html).Path
if (-not $Pdf) { $Pdf = [System.IO.Path]::ChangeExtension($htmlPath, '.pdf') }
$Pdf = [System.IO.Path]::GetFullPath($Pdf)

$edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw 'Microsoft Edge not found' }

$uri = ([System.Uri]$htmlPath).AbsoluteUri
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $edge --headless=new --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw `
    --virtual-time-budget=8000 --print-to-pdf="$Pdf" $uri 2>$null | Out-Null
$ErrorActionPreference = $prev

if (-not (Test-Path $Pdf)) { throw "PDF was not produced: $Pdf" }
Write-Output ("PDF: {0} ({1:N0} bytes)" -f $Pdf, (Get-Item $Pdf).Length)
