# Shongwe Motors development continuity

**Checkpoint: 29 October 2026, initial safe-source publication.** The published source+logo commit is `896aaf738c50b090073d0dc50ffb7ea41b21c296`. File-level Git object SHA verification matched all 23 local source and asset files against GitHub. CI for that commit succeeded (workflow run `40872299886`). Local tests: **22 passed, 7 strict xfails**. The original assignment ZIP was inspected and its Python, GUI, logo and Windows scripts were assembled into a publishable repository layout. **Never upload the original ZIP unchanged**, as it contains a plaintext demonstration login credential.

## Implemented in initial publication

- Preserved the four existing Qt Designer `.ui` pages, application controller, SQLite CRUD and appointment flow.
- Removed the shared password from `main.py` and all published documentation.
- Added `auth.py` with first-run administrator setup, PBKDF2-SHA256 salted hash, OS app-data credential storage, read-only verification and exclusive account creation.
- Protected desktop screen navigation using a controller session state and cleared it on logout.
- Added Windows setup/run scripts, `.gitignore`, isolated regression/auth tests and baseline GitHub CI workflow.
- No original customer data, live database, secrets or unrelated assignment files have been included.

## Unfixed, known defects

Original booking logic allows overlapping reservations. Deleting customers or vehicles cascades into appointment deletion. `MAX(id)+1` can reuse codes. Invalid numeric/date values and Sold-vehicle bookings can reach database functions. These remain marked as **strict xfail tests**, not fixed features. Follow GitHub issues #2, #3 and #5 and docs/AUDIT_2026-10-29.md.

## Verification limitations

Local syntax, SQLite/authentication tests and UI XML checks can be completed in a headless environment. Actual PyQt5 operation on Windows, installer behaviour, real migration/backups and concurrency tests need separate evidence. Test against synthetic databases only.

## Next milestone

Validate the published repository tree and GitHub Actions, then run the real Windows application from a clean checkout. Once the baseline is signed off, implement booking overlaps with transaction-safe writes, preserve booking history and create migration/backup tests. Keep GitHub README, docs/TESTING.md, docs/ROADMAP.md, this handoff and issue statuses aligned with verified results.
