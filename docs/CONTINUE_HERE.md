# Shongwe Motors continuity handoff

**Last checkpoint:** 29 October 2026. **Repo:** Sonkhe-Shongwe/shongwe-motors, default branch main.

The public repository was **initially empty**. The actual original Python/PyQt5/SQLite source was independently audited from the owner's uploaded 28432673_INF2611_Assignment_04.zip. Archive SHA-256 c907eac6c995de2bfb9a23c67daa5d6e9f76b7cde2a3510d4a1d2aa0d5a52d50. The original archive contains a plaintext login secret and should **not** be uploaded directly to this public repo.

## Current source architecture

main.py (490 lines) owns AppController, LoginWindow, CustomerWindow, VehicleWindow, BookingWindow. database.py (194 lines) stores customers, vehicles and bookings through SQLite and enables FK checks; the extra MySQL SQL file is an unused alternative schema. Four .ui files and a logo are editable in Qt Designer. Booking UI has calendar/time and CRUD-style operations.

## Audit outcome

15 passing pytest checks plus 7 strict xfails confirming vulnerabilities. Same vehicle+date+time booked twice. Customer or vehicle deletion cascades to booking history. Codes reused after deleting highest row. Invalid negative values/date-time and sold-vehicle booking accepted by direct DB calls. Hardcoded plaintext login credential in original source. PyQt GUI was not run, because PyQt5 was unavailable in the test runtime.

## Next implementation action

Prepare **sanitized** source import with .gitignore and tests, then implement transaction-safe booking conflict checks using an explicit business-rule contract. Prioritize history retention with migrations and account-based login before making a public app release. Preserve original four-screen behaviour and historical record codes. Update this file and testing evidence with each verified milestone.

## Ground truth

Refer to AUDIT_2026-10-29.md, ROADMAP.md and TESTING.md; check current GitHub commits/issues before acting. Never mistake proposed changes for implemented fixes. Run only synthetic/disposable DB tests until verified backup/migration safeguards exist. Do not push customer data or legacy credentials.

## Tracked work items (created 29 October 2026)

- [#1: Secure source import and regression baseline](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/1)
- [#2: Transaction-safe booking conflict prevention](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/2)
- [#3: Preserve bookings during customer/vehicle archival](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/3)
- [#4: Replace hardcoded authentication](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/4)
- [#5: Database constraints, identifiers and migrations](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/5)

**Repository state after audit:** documentation-only initial commits; Python source and executable tests are not yet committed. The latest GitHub issues and actual branch commits supersede this dated snapshot.
