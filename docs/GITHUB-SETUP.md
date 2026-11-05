# Publishing this project to a NEW GitHub repository

1. On github.com create an **empty** repository (no README / .gitignore / license, so nothing conflicts).
2. Extract the zip. Open a terminal **inside the extracted `InstagramResearchSuite` folder** (the one containing `main.py`). The files must sit at the repository root, not in a sub-folder, or GitHub will not see `.github/workflows`.
3. Run:
   ```powershell
   git init -b main
   git add -A
   git commit -m "Instagram Research Suite 1.0.2"
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```
4. Check before pushing (both must be true):
   ```powershell
   git ls-files app/data      # lists 2 files (database.py, __init__.py)
   git ls-files .github       # lists ci.yml and build-windows.yml
   ```
5. Open the **Actions** tab. `CI` runs on every push (lint + tests). `Windows build` is manual (Actions → Windows build → Run workflow) or automatic when you push a tag:
   ```powershell
   git tag v1.0.2 && git push origin v1.0.2
   ```
   Tagged builds attach `InstagramResearchSuite-portable.zip` and `InstagramResearchSuite.exe` to a GitHub Release. Make sure *Settings → Actions → General → Workflow permissions* is set to **Read and write** so the release step can publish.

Local checks that mirror CI: `python -m ruff check .` and `python -m pytest`.

## Cleaning up an existing repository (no command line needed)
1. **Delete the old code**: on github.com open the `src` folder → click the **⋯** menu (top right of the file list) → **Delete directory** → commit. Do the same for any old test files in `tests/` that import `instagram_research_suite`.
2. **Overwrite the workflows**: in `.github/workflows/` the repository should contain exactly `ci.yml`, `tests.yml`, `windows-build.yml`. Use **Add file → Upload files** and drag in the `.github` folder from the patch zip (same names overwrite). Delete any other workflow file (for example `build-windows.yml`).
3. Upload `pyproject.toml`, `app/__init__.py`, `version_info.txt`, `CHANGELOG.md` from the patch zip.
4. Open the **Actions** tab: all runs should now be green. If one is red, open it and send me the log.
