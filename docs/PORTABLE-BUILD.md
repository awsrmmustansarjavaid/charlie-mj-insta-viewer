# Portable build
`scripts\build_windows.ps1` (folder) or `-OneFile` (single exe), or the `Build Windows portable` GitHub Action (tag `v*` publishes a release).
* Folder build starts fastest; one-file build unpacks to a temp dir on each start (data still lives beside the exe).
* Data directory order: `--data-dir` → `IRS_DATA_DIR` → `<exe>\data` → `%LOCALAPPDATA%\InstagramResearchSuite` (if not writable, e.g. Program Files / read-only USB).
* Unsigned executables may trigger Windows SmartScreen; sign with your certificate for distribution.
* Not yet verified on a real Windows machine in this repository's development environment — run the build once and the app's Logs page for diagnostics.
