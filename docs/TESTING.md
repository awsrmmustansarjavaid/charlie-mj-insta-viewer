# Testing

Run unit tests:

```powershell
pip install -r requirements-dev.txt
pytest -q
```

Manual Windows release checklist:
- Launch on a clean Windows 10/11 64-bit machine.
- Launch from a writable folder and from a read-only folder.
- Confirm fallback data directory behaviour.
- Load both 587-row demo lists and check visible completion status.
- Save snapshots, restart the app, and confirm history persists.
- Compare two snapshots and verify additions/removals.
- Export CSV and open it in Excel.
- Confirm no credentials or private data are written to logs.
