<#
 Builds the portable Windows app.
   .\scripts\build_windows.ps1            -> dist\InstagramResearchSuite\ (portable folder, fastest start)
   .\scripts\build_windows.ps1 -OneFile   -> dist\InstagramResearchSuite.exe (single file)
 Requires Python 3.10+ on PATH.
#>
param([switch]$OneFile)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pytest -q
if ($OneFile) { $env:IRS_ONEFILE = "1" } else { Remove-Item Env:IRS_ONEFILE -ErrorAction SilentlyContinue }
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean InstagramResearchSuite.spec
if ($OneFile) { $out = "dist\InstagramResearchSuite.exe" } else { $out = "dist\InstagramResearchSuite\InstagramResearchSuite.exe" }
Write-Host "`nBuilt: $out"
Write-Host "Portable: data is stored in a 'data' folder next to the .exe (falls back to %LOCALAPPDATA% if read-only)."
