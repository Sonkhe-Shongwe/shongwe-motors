# Prioritised engineering roadmap

**Principle:** incrementally upgrade the existing four-screen PyQt5 desktop system and SQLite persistence; do not rewrite it as a web application or replace databases without a demonstrated need.

| Phase | Priority | Deliverable | Exit criteria |
|---|---|---|---|
| 0. Safe initial import | P0 | Sanitize legacy plaintext credential, add .gitignore, privacy-safe examples, test harness, baseline snapshot | No secrets, national IDs or populated DB files committed; baseline reproduced |
| 1. Booking integrity | P0 | Appointment duration and availability rules, active/cancelled status, atomic conflict detection in transaction | Identical/overlapping times blocked; adjacent allowed; double concurrent writer test passes; cancellation preserves history |
| 2. Retention and schema migrations | P0 | Archive/delete rules, non-cascading historical relationships, versioned migrations, backups, code allocation | Booking history survives customer/vehicle archive; old record codes remain unchanged; migration/restoration passes |
| 3. Authentication | P0 | First-run admin setup, hashed and salted credentials, session state, login failure handling, protected screens | No hardcoded password; unauthorized navigation blocked; logout revokes access; sensitive data stays outside Git |
| 4. Reliability and architecture | P1 | Service/repository split, type and value validation, SQLite connection handling, currency representation, logging | CRUD and booking parity; failure paths tested; no unexplained state loss |
| 5. Portfolio polish | P2 | Slot availability UI, cancel/reschedule/history, screenshots, setup docs, lint/CI, optional verified Windows package | Demo can be run from fresh synthetic data; full manual GUI path and automated tests pass |

## Must-have automated checks

- Existing customer, vehicle, booking create/list/delete actions preserved until explicit retirement.
- FK and uniqueness; invalid negative money/mileage, dates, times, sold vehicle and duplicate identity rejected.
- Two simultaneous conflicting bookings from separate database connections; overlapping/adjacent intervals; start/end boundary cases.
- Customer and vehicle archival preserve bookings; cancel/reschedule maintain original and event history.
- Migration from anonymized legacy database with and without collisions; rollback and backup restoration.
- Password hashing and first-run account setup; bad login/lockout/logout/session navigation.
- Windows/PyQt GUI smoke tests for all four pages; error paths, keyboard flows, empty states.
- GitHub Actions run tests with synthetic SQLite fixture, linters, and scan for secrets/PII.

## Business decisions still open

Appointment duration (fixed or per type), allowed hours, consultant and customer overlap, the meaning of Reserved inventory, booking status transitions, explicit permanent purge rules and whether the long-term product stays local desktop or becomes multi-user networked.

## Development protocol

First write a failing requirement test, then make the narrowest compatible code change. Verify the full baseline, preserve old data, run a GUI smoke pass whenever the environment supports it, and capture actual evidence. Each coherent phase belongs in a reviewable PR with documentation updates. A proposed feature is not implemented until the test gate passes.

## Master blueprint (29 October 2026)

The [Shongwe Motors 1.0 Master Development Blueprint](MASTER_DEVELOPMENT_BLUEPRINT_1_0.md) consolidates this earlier roadmap into proposed milestones M0-M7 and gates G0-G8. **Do not interpret the blueprint as implemented functionality or automatically approved business decisions.** Where this legacy roadmap differs in sequencing or scope, review the decision register and keep tests and data preservation as the controlling release conditions. The next checkpoint is M0 Windows parity plus explicitly resolved booking policy D-01..D-06 before schema or scheduling code changes.
