# Build a portable Windows folder distribution with PyInstaller.
# Run this script from the repository root in a Windows PowerShell terminal.

$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# Clean old build outputs to avoid packaging stale files.
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

pyinstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name InstagramResearchSuite `
    --collect-all PySide6 `
    main.py

# Create the portable writable-data folder next to the executable.
New-Item -ItemType Directory -Force -Path "dist\InstagramResearchSuite\data" | Out-Null
Write-Host "Build complete: dist\InstagramResearchSuite\InstagramResearchSuite.exe"
