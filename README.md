# Shongwe Motors

Python/PyQt5 desktop dealership management and appointment-booking application, being upgraded from an educational prototype into a tested portfolio project.

## Project status: initial audit, 29 October 2026

**The existing Python source has not been published to this new repository yet.** It was audited from the owner's separately supplied assignment archive. That archive contains an insecure hardcoded demonstration credential and must not be pushed to this public repository unchanged.

Audited baseline: four Qt Designer interfaces (login, customers, vehicles, bookings), Python application controller, SQLite database layer, customer/vehicle CRUD, appointment bookings, calendar and live clock. The included MySQL script is optional and is **not** the currently used database.

An isolated audit found **15 passing baseline tests and 7 strict expected failures** covering booking collisions, historical data loss, reused IDs, invalid values and sold vehicles. GUI testing on Windows is still outstanding.

## Engineering priorities

1. Transaction-safe prevention of overlapping bookings and clear appointment cancellation/status rules.
2. Preserve booking history by replacing destructive cascade deletion with archival and safe migrations.
3. Replace hardcoded credentials with secure password storage and controller-level session protection.
4. Guarantee stable record codes, validate all writes and add backup/recovery controls.
5. Introduce regression/GUI tests, CI, polished UI, reproducible setup and screenshots.

**Read:** [Detailed source audit](docs/AUDIT_2026-10-29.md) | [Roadmap](docs/ROADMAP.md) | [Testing](docs/TESTING.md) | [Continuation](docs/CONTINUE_HERE.md).

## Safety policy

Never commit real customer data, ID numbers, populated databases, passwords, local backups, logs or the unsanitised original ZIP. Claims of implemented or tested features require supporting evidence.

## Portfolio acceptance goal

A reviewer will eventually be able to launch the desktop application, create an admin account, manage customers and vehicles, schedule/cancel/reschedule appointments without conflicts, preserve booking history and reproduce automated tests against synthetic fixtures. The application is not yet a production release.