# SHONGWE MOTORS
## Research and Modernisation Report

**Product and engineering strategy for a professional Python dealership application**  
**Date:** 29 October 2026  
**Research status:** Decision-support report; recommendations are not implemented features.  
**Code baseline:** `Sonkhe-Shongwe/shongwe-motors`, current published PyQt5/SQLite source and previously verified isolated tests.

---

# 1. Executive decision

**Recommendation:** Develop Shongwe Motors into a **local-first dealership operations and test-drive management system** for a small independent vehicle dealership. Retain Python, SQLite and the existing desktop workflows during the first engineering milestones. Make correctness, data protection and a demonstrable end-to-end business journey the differentiators. Defer a public customer website, payment gateway, full repair-shop ERP and AI features.

The ideal demonstrable journey is:

**Register a vehicle -> capture a customer enquiry -> schedule a conflict-free test drive -> record the appointment outcome -> progress an opportunity -> reserve or sell the vehicle -> review truthful operational metrics.**

The first non-negotiable task is to prevent lost booking history and double-bookings. Professional styling is important, but it cannot compensate for incorrect persistence or unverifiable outcomes.

## 1.1 Decisions in brief

| Question | Recommended answer | Why |
|---|---|---|
| Business identity | Independent dealership, not general auto-repair workshop | Existing vehicle inventory, sales consultations and test drives already fit this domain. |
| Platform | Single-machine Windows desktop, local-first | Low operational overhead, aligns with current implementation and makes an offline demonstration realistic. |
| Database | SQLite with explicit transactions and migrations | Adequate for the scoped single-machine use case; provides a genuine relational integrity story. |
| Framework | Keep PyQt5 initially; reassess PySide6 after functional parity | A large rewrite before correctness testing adds avoidable risk. Licensing needs deliberate treatment. |
| Core showcase | Transaction-safe appointment scheduling and traceable vehicle/customer history | High business value and strong technical interview material. |
| Differentiation | Measurable showroom workflow and explainable reporting | More distinctive than adding many unrelated modules. |
| Deployment | Reproducible Windows setup, then an independently tested installer | A passing unit-test suite alone cannot certify a working desktop package. |

# 2. Research method and evidence boundaries

This report combines four kinds of evidence. **S = directly inspected Shongwe Motors source or the established local regression baseline; O = an official technical or regulatory reference; V = a vendor's own product description; R = a public open-source repository's self-description; A = analysis and proposed design.** Vendor and repository descriptions show *claimed* capabilities; their underlying implementations were not independently audited. No field study of actual dealership staff was performed.

The source review covered `main.py`, `database.py`, `auth.py`, four `.ui` files, CI, requirements, tests and README in the published project ZIP. The published baseline has **22 passing tests and 7 expected failures (xfail)**. The expected failures represent known missing safeguards, not successful protection. The 29 October GitHub Actions run passed the configured headless Python checks; a live Windows GUI walkthrough, real concurrent-writer tests and a tested installer remain outstanding. [S]

The market review considered a South African dealership platform, automotive industry guidance, dealership showroom repositories, repair-shop software and scheduling software. Technical design guidance was drawn from SQLite, Python, Qt, pytest-qt, OWASP, NIST, PyInstaller and South Africa's Information Regulator. [O1-O13, V1-V5, R1-R3]

**Important constraint:** The following is a plan for an evidence-backed portfolio release, not a representation that Shongwe Motors already satisfies the proposed controls.

# 3. What Shongwe Motors is today

## 3.1 Verified functionality

| Existing capability | Current implementation | Maturity and limitation |
|---|---|---|
| Desktop interface | Four Qt Designer pages: login, customer, vehicle, booking. Loaded through `main.py`. | Source-level layout confirmed; final visual usability not tested on Windows. |
| Authentication | First-run local administrator, salted PBKDF2-SHA256 credential store in `auth.py`. | Safer than prior hardcoded login; still basic GUI access control and not full protection against OS-level data access. |
| Customer records | Create, list and delete; details include contact information and identity number. | Delete can remove linked bookings, so real customer data must not be used yet. |
| Vehicle inventory | Store VIN, make/model, price, mileage, condition and Available/Reserved/Sold status. | Missing database range checks and controlled status transitions. |
| Appointment management | Test Drive, Vehicle Viewing, Sales Consultation, Vehicle Collection; date, start time, customer, vehicle, consultant and notes. | No duration, conflict detection, lifecycle or rescheduling. |
| Database | SQLite, parametrised inserts and FKs enabled on each connection. | Destructive FK cascades; no versioned migrations, backup/restore protocol or hardened constraints. |
| Tests/CI | pytest, GitHub Actions on Python 3.11/3.12, 22 passing plus 7 expected failing checks. | Useful baseline; GUI, Windows installer and concurrency acceptance missing. |

Source-specific observations: `database.py` currently uses `MAX(id)+1` to suggest public codes; `add_booking()` inserts a booking without checking availability; `bookings` references customers and vehicles with `ON DELETE CASCADE`; vehicle prices use SQLite `REAL`; the database path remains beside the source code; and the booking form prevents past calendar dates but not necessarily an earlier time on the current date. The vehicle selector includes `Reserved` vehicles. [S]

## 3.2 Baseline risk register

| ID | Actual issue or open verification | Priority | Consequence |
|---|---|---|---|
| F01 | Same vehicle and timeslot accepted twice | Critical | Invalid commitments and unreliable appointments. |
| F02 | Customer or vehicle deletion cascades into bookings | Critical | Historical data loss and inaccurate reports. |
| F03 | No canonical appointment duration or active/cancelled status | Critical | Overlapping intervals cannot be modelled correctly. |
| F04 | Business identifiers can be reused after deletion | High | Broken external references and confusion. |
| F05 | Invalid prices, mileage and date/time can reach SQLite | High | Database is not an authoritative validity boundary. |
| F06 | Sold vehicle can be booked through the database API | High | GUI filtering does not protect persistence. |
| F07 | No versioned database upgrade or tested recovery | High | Future schema changes could damage existing records. |
| F08 | Data file stored alongside code, inconsistent with app-data credential location | High | Weak deployment and backup hygiene. |
| F09 | App-level login is not OS-level data encryption; no reset UI | Medium | Overstating security would be misleading. |
| F10 | GUI, accessibility and packaged Windows operation unverified | Medium | Cannot claim a release-ready desktop product. |
| F11 | Limited editing, search, booking follow-up and data export | Medium | Business workflow stops at record creation. |

**Implication:** Initial development should eliminate F01-F08 before broad new feature work. Fixing F01 without F02 would produce a scheduler that still loses history.

# 4. Competitive and comparable-product research

## 4.1 Industry-level dealership model

Automotive dealership guidance distinguishes inventory, CRM, lead follow-up and appointment-related workflows. This suggests that the useful core is a **connected customer, vehicle and opportunity record**, not disconnected CRUD screens. Industry guidance also describes lead sources and assignment to sales personnel. [O14]

For our scope, the minimal dealership business chain is:

1. **Inventory:** A unique vehicle stock unit with immutable history and current availability.
2. **Enquiry:** Customer interest in one or more specific vehicles.
3. **Appointment:** Test drive or viewing scheduled against a real resource and time interval.
4. **Outcome:** Attended, cancelled, no-show or completed, with a recorded follow-up.
5. **Opportunity:** New, contacted, test drive booked, negotiating, won or lost.
6. **Inventory transition:** Available, reserved for a defined reason, sold or archived.

These are *proposed* states; exact transition rules must be confirmed before implementation.

## 4.2 Comparison matrix

| Comparable system | Research-supported strengths | Adopt selectively | Avoid copying |
|---|---|---|---|
| **Refresh Tech, South Africa** (V1) | Vendor describes stock, customers, enquiry-to-sale pipeline, test-drive booking, staff assignment and reports. | A connected lead -> test drive -> sale progression and status-based dashboard. | Entire cloud platform, branded listings and every claimed integration. |
| **Tekmetric** (V2) | Vendor describes customer histories, appointments, notifications, reports, estimates, repair orders and role permissions. Primarily repair shops. | History, clear work status, role-conscious workflows and practical reporting concepts. | Repair-order billing, inspections and parts procurement in a dealership-first release. |
| **AutoLeap** (V3) | Vendor offers scheduling, work boards, customer contact, CRM and appointment reminders for workshops. | Calendar clarity, customer records and consistent follow-up. | Payments, marketing automation, technician and POS suites. |
| **Microsoft Bookings** (O1) | Service/staff availability and pre/post appointment buffer time. | A real availability engine with duration, staff assignment and blocked intervals. | Microsoft 365 integration and a customer portal as prerequisites. |
| **SimplyBook.me** (V4) | Configurable service durations, buffers, rescheduling, booking limits and confirmations. | Duration per appointment type, buffer, cancellation and rescheduling. | Broad consumer booking platform and promotional add-ons. |
| **Odoo Fleet** (V5) | Vehicle status, contracts, service cost and mileage-focused fleet tracking. | Vehicle history and well-defined lifecycle terminology. | Fleet finance, leasing contracts and general enterprise ERP. |
| **Murangi's Car Dealership** (R1) | Public UNISA PyQt5/MySQL student-project README describes login, inventory, customers and bookings. | Treat as a minimum feature benchmark, not a model for our architecture. | Repeating essentially the same four-screen assignment scope and stopping at basic CRUD. |
| **vehicle-showroom** (R2) | Open-source README claims leads, reservations, test drives, sales and reports in distinct modules. | Domain boundaries and linked states. | Rebuilding public showroom, quotes, payments and trade-ins immediately. |
| **dms** (R3) | Open-source README claims lead-to-delivery process, permissions, audits and many endpoints. | Auditability and explicit workflow contracts as design references. | Multi-tenancy, 85+ endpoints and enterprise permissions for a local desktop app. |

**Comparison caveat:** These rows summarise public product descriptions or README claims, not empirical tests, verified security quality or endorsements. The aim is to extract transferable design patterns.

## 4.3 Strongest transferable lessons

**Lesson A: Business state is more important than number of screens.** A record should have a reasoned lifecycle: an enquiry is not a sale; an appointment is not an inventory reservation; an available vehicle is not necessarily free for every appointment time. [A, O14, V1]

**Lesson B: Availability is an intersection of constraints.** A booking is valid only when the appointment fits the vehicle, the assigned consultant (if resource-bound), opening hours, existing active bookings and any buffer. Microsoft Bookings illustrates this type of scheduling rule. [O1]

**Lesson C: History is the source of trustworthy reporting.** Deleting appointments, changing their status without logging events or reusing IDs destroys the evidence needed for pipeline conversion or staff productivity indicators. [A]

**Lesson D: Define the narrow product boundary.** Auto-repair systems are useful references for operational discipline, but their estimates, repair orders, labour guides, parts and payments are outside our targeted dealership experience. [V2,V3]

**Lesson E: Compete on proof, not breadth.** An independently tested, single-machine app with reliable migrations and realistic demo data is a stronger early portfolio milestone than an unverified 20-page app. [A]

# 5. Recommended functional scope

## 5.1 Must-have for portfolio release 1.0

| Domain | Minimum complete experience | Demonstrates |
|---|---|---|
| Vehicles | Add, view, search/filter, edit, archive, status history; unique VIN; valid R price and mileage. | Data modelling, business validation, maintainable forms. |
| Customers | Register, search, edit, archive; documented data minimisation and duplicate handling. | Relationship integrity and privacy-aware implementation. |
| Appointments | List available slots, book, cancel, reschedule, mark attended/no-show/completed; detect interval overlaps. | Transactions, concurrency, temporal logic and testing. |
| Enquiries/opportunities | Record vehicle of interest, source, owner, stage, next action and outcome. | A coherent operational workflow beyond isolated CRUD. |
| Operations dashboard | Today's appointments, overdue follow-ups, stock by status, test-drive results and funnel counts. | Genuine SQL aggregation and KPI definition. |
| Authentication/data | First-run admin, tested credentials, safe backups, no sensitive data in Git. | Defensive application development. |
| Delivery | Reproducible setup, documented Windows demo, synthetic data and a tested build. | Software release engineering. |

## 5.2 High-value but optional after 1.0

- Appointment confirmations in a local printable form or drafted email, without sending real customer data to third parties.
- CSV export and stock-age reporting with explicit filters and accurate date definitions.
- Optional salesperson accounts and access rules, **only if** the product becomes multi-user in a meaningful way.
- Basic audit/activity timeline showing which operation changed a booking or vehicle status.
- Calendar week/day views with booked, available and unavailable slots clearly distinguished.

## 5.3 Defer or exclude

Do **not** prioritise finance and lending integrations, online payment capture, SMS/WhatsApp APIs, external vehicle-data subscriptions, AI chatbots, ML price prediction, real-time web sync, multi-branch multi-tenancy, comprehensive repair orders or a full public customer-facing website. They introduce security, legal, cost and operational obligations unrelated to the central goal.

A later expansion can be justified with a new use case and acceptance tests, rather than treating complexity as a goal.

# 6. Booking engine: the technical centrepiece

## 6.1 Proposed scheduling rules

Each appointment stores a stable internal ID, public booking code, customer ID, vehicle ID (optional for generic sales consultations if business rules permit), assigned consultant ID where applicable, appointment type, status, start time, end time, creation time and change history. A **duration** and optional **buffer** come from a documented appointment-type policy, with exceptions recorded explicitly.

Example *illustrative policy*, not confirmed dealership operating rules:

| Type | Example duration | Example resource | Blocking rule |
|---|---:|---|---|
| Test Drive | 45 min + 15 min buffer | Vehicle and consultant | Neither may have overlapping active appointments. |
| Vehicle Viewing | 30 min | Consultant; optionally vehicle | Block only the genuinely exclusive resources. |
| Sales Consultation | 45 min | Consultant | Vehicle is optional unless a specific unit is discussed. |
| Vehicle Collection | 30 min | Consultant and allocated vehicle | Require valid handover/ownership state. |

The application must make these rules configurable or deliberately document its fixed assumptions. A viewing need not always monopolise a vehicle in the way a test drive does; resource policy must reflect actual operation.

## 6.2 Correct overlap logic

Use half-open intervals `[start, end)` to permit back-to-back appointments. Two bookings conflict when:

`existing.start < requested.end AND existing.end > requested.start`

Only blocking statuses such as `confirmed` or `checked_in` should occupy a slot; a cancelled record remains in history without blocking availability. The status list and expiry policy are business design decisions.

**Critical:** A UI check followed by an independent INSERT is insufficient. For SQLite, begin an `IMMEDIATE` write transaction, re-read eligibility and overlapping active reservations, insert if valid, then commit. A competing writer must wait or fail safely; it must never independently commit the same exclusive resource interval. SQLite documents immediate transactions and single-writer behaviour. [O2]

Use a partial unique index for active identical starts as *defence in depth*. A SQLite partial index cannot, by itself, guarantee that arbitrary intervals do not overlap. It therefore supplements rather than replaces transactional checks. [O3]

## 6.3 Essential scenario tests

1. Same vehicle, same time, different customers: exactly one booking succeeds.
2. Same vehicle, start times 09:00 and 09:30 with 60-minute duration: second is rejected.
3. One appointment ends at 10:00, the next starts at 10:00 without buffer: allowed.
4. Cancelled appointment no longer blocks the slot but remains visible historically.
5. Two separate SQLite connections attempt the same resource booking simultaneously: exactly one succeeds.
6. Sold or archived vehicle is blocked from incompatible appointment types.
7. A changed/rescheduled appointment rechecks all conflicts and leaves no partial history.
8. A booking ending outside operating hours is rejected or requires explicit administrative override.
9. A consultant conflict is detected independently of the vehicle conflict, if consultant availability is a rule.
10. Invalid timestamps, impossible end-before-start times and past-time bookings are rejected at service boundaries.

# 7. Data architecture and integrity

## 7.1 Target entity model

Retain the existing `customers` and `vehicles` data, then migrate safely to stable **internal integer keys** for relationships while preserving visible customer, vehicle and booking codes as immutable alternative identifiers.

| Entity | Primary responsibility | Representative relationships |
|---|---|---|
| Customer | Contact and status; minimum necessary personal data | One-to-many Enquiries and Bookings |
| Vehicle | Stock unit, VIN and inventory lifecycle | One-to-many Enquiries and Bookings |
| StaffMember | Consultant identity and active status | One-to-many appointments and lead assignments |
| AppointmentType | Duration, buffer, resource policy | One-to-many Bookings |
| Booking | Scheduled interval, state and participants | Customer, optional Vehicle, optional StaffMember, AppointmentType |
| BookingEvent | Immutable event/action history | Many-to-one Booking |
| Enquiry/Opportunity | Customer interest, stage, source and follow-up | Customer, optionally Vehicle and StaffMember |
| InventoryEvent | Status and price history | Many-to-one Vehicle |
| SchemaMigration | Applied schema version/checkpoint | Database operational metadata |

A separate `VehicleReservation` may be added **later** if deposits, holds or stock allocation become real requirements. Do not conflate an appointment with a financial reservation.

## 7.2 Database invariants

- Foreign keys enforced **on every connection**, including migration/test connections. [O4]
- `UNIQUE` VIN and immutable public codes; stable nonreusable ID allocation.
- `CHECK` constraints for nonnegative mileage and price, valid states and valid event ordering where possible.
- Money stored as integer South African cents or a tested decimal representation; never rely on arbitrary binary floating-point rounding for financial totals.
- Creation/update and event timestamps stored consistently; document local timezone and daylight-saving assumptions for future multi-region extensions.
- Logical archive for historically referenced customers/vehicles; no silent cascade deletion of appointments.
- Explicit one-way status transitions with validated exceptions and audit records.
- Database write operations exposed through services and tested without a GUI.

## 7.3 Migration and recovery plan

A schema migration is a **data preservation operation**, not just `CREATE TABLE IF NOT EXISTS`. Before changing the database: create a verified backup, inspect existing booking collisions and invalid records, migrate on a copy, compare record counts and key references, run `PRAGMA foreign_key_check`, run `PRAGMA integrity_check`, then repeat on a controlled real upgrade. Keep older public codes intact.

SQLite table redesign commonly requires a table-copy pattern; Alembic documents batch migrations for this case. For a small app, a carefully tested `PRAGMA user_version` migration runner may be simpler than adopting an entire ORM immediately. Alembic is warranted only if schema growth justifies it. [O5]

Use SQLite's online backup API to make consistent local backups rather than casually copying an active database file. Define restore tests and explain where the backup is stored. [O6]

WAL can improve reader/writer interaction on a local filesystem, but it does not enable multiple simultaneous SQLite writers and is not a substitute for transactions. Do not put a WAL database on a shared network drive. [O7]

## 7.4 One code-level issue that deserves early attention

Python's `sqlite3.Connection` context manager commits or rolls back transactions **but does not close connections**. Refactor the current repeated `with connect()` usage to use a clearly owned connection lifecycle that reliably calls `close()`. [O8, S]

# 8. Authentication, privacy and operating assumptions

## 8.1 Correct security goal

For a single-user desktop prototype, **first-run local administrator authentication plus OS filesystem permissions** is an appropriate initial scope. It must not be misrepresented as multi-user, network-secure access control or encryption of the local customer database. Add actual staff users/RBAC only if there is a tested multi-user requirement.

The current `auth.py` uses PBKDF2-HMAC-SHA256 with 600,000 iterations and a random salt, an accepted configuration discussed by OWASP. OWASP generally prefers Argon2id for new password storage where practical, and NIST's single-factor password guidance expects a minimum of 15 characters. The current first-run minimum is 12; review that policy for the intended threat model rather than labelling the present design standards-certified. [O9, O10, S]

## 8.2 Privacy protection

The source includes South African identity number, contact and address fields. Those are sensitive business records even when the app is only a portfolio demonstration. Adopt data minimisation, synthetic demo identities, no personal data in logs/screenshots, clear retention policies, protected storage, backups that do not leave local control, and a recorded procedure for correcting or removing personal data where legally appropriate. The Information Regulator describes reasonable security safeguards and continuing risk review under POPIA. This is product-design guidance, not legal certification. [O11]

**Data location:** move the database out of the source checkout and into a per-user application-data directory. Explicitly document where data, credentials, logs, exports and backups reside. Keep all of them out of repository commits, installers and demo archives.

## 8.3 Avoid security theatre

Do not label the app 'bank-grade' or 'production secure' merely because passwords are hashed. Do not add unused JWT libraries, cloud tokens or complicated RBAC tables to a single-user Qt UI. Instead demonstrate a clear threat model, a safe default account workflow, reproducible tests and honest limitations.

# 9. Proposed application architecture

## 9.1 Make the smallest safe structural change

The current `main.py` controls all four windows and most form logic; `database.py` combines connection handling, schema and CRUD. Split responsibilities incrementally rather than rewriting the full GUI.

```
shongwe-motors/
  main.py                 # small app entry point
  app/
    ui/                   # Qt windows, Qt Designer .ui files, shared styling
    services/             # booking, vehicle, customer, enquiry, auth use cases
    domain/               # statuses, entities, scheduling policies, validation
    persistence/          # SQLite connection, repositories, migration runner
    reporting/            # SQL measures and CSV export adapters
  assets/
  tests/
    unit/
    integration/
    gui/
    migration/
  docs/
    architecture.md
    data_dictionary.md
    business_rules.md
    test_matrix.md
    decisions/
```

This is a **target structure**, not the current repository layout. Migrate in small slices: first the booking service and data layer, then other entities, then UI components. Keep compatibility adapters while tests protect old functionality.

## 9.2 Request path

**Qt form -> validated application service -> transaction-aware repository -> SQLite**. The UI owns display and input events, not database invariants. The service owns appointment business rules and transitions; the repository owns queries; SQLite enforces structural constraints.

Use `QAbstractTableModel` / `QTableView` when search, sort and row refresh become nontrivial. Qt's model/view architecture separates displayed data from its presentation. Do not refactor every table before there is a concrete benefit. [O12]

## 9.3 Why not a Django/React rewrite now?

| Option | Advantages | Costs and risks | Decision |
|---|---|---|---|
| Retain PyQt5 + SQLite; modularise | Lowest migration risk, offline, strong Python/SQL demonstration | Local single-machine scope, packaging and PyQt licensing work | **Preferred for 1.0** |
| Migrate to PySide6 + Qt6 | Official Qt Python bindings, LGPL/commercial licensing paths, longer-term Qt6 opportunity | API/Designer migration, new GUI regressions and packaging qualification | Consider after core acceptance |
| Django/FastAPI + web frontend | Multi-user accessibility, HTTP API, hosted demo potential | Changes operational and security model; duplicate frontend work | Only if a web product becomes an explicit goal |
| Full dealer management ERP | Wide feature coverage | Unmanageable scope, additional financial compliance and weak test depth | Reject for portfolio 1.0 |

**Licensing caveat:** Riverbank states PyQt5 is GPLv3 or commercially licensed, not LGPL. Qt for Python/PySide6 has LGPL and other licensing options subject to obligations. A public GitHub repository alone is not a software licence. Choose and document compatible licensing before distributing an executable. [O13]

# 10. User experience and portfolio presentation

## 10.1 Interface direction

Adopt a cohesive dealership operations interface: stable navigation for Dashboard, Inventory, Customers, Appointments, Opportunities and Settings; visible active user; consistent status names and actions; neutral backgrounds with one restrained automotive accent; readable forms and tables. Reuse the existing Shongwe Motors brand rather than imitating a commercial competitor.

**Highest-value interaction improvements:**

- Appointment calendar with clear booked/available intervals, staff selection and a prominent conflict explanation.
- Search and filters for inventory and customers; record details rather than enormous input forms.
- Edit/archive instead of destructive Delete; confirmation with an exact consequence and recovery guidance.
- Booking detail with status, timestamps and history; Cancel and Reschedule as explicit actions.
- Helpful empty states, consistent validation beside fields, keyboard Enter/Escape and clearly identified required data.
- Stable layouts at common Windows screen sizes and default scaling, with keyboard focus and accessible labels.

Avoid decorative dashboards with hardcoded numbers, charts that imply nonexistent sales, overly animated panels, inaccessible colour-only status and a 'premium' theme that leaves business errors unaddressed.

## 10.2 Genuine dashboard metrics

| Metric | Definition and prerequisites | Risk of misleading interpretation |
|---|---|---|
| Active inventory | Count of non-archived vehicles by genuine stock status | 'Reserved' must not be confused with a test-drive reservation. |
| Upcoming appointments | Confirmed bookings with start after the current local time | Must exclude cancelled, completed and no-show records. |
| Test-drive attendance rate | Completed/attended test drives divided by eligible scheduled test drives for a defined period | Do not include future bookings in the denominator. |
| Overdue follow-ups | Open opportunities with next_action_date before today | Requires reliable opportunity records, not inferred from notes. |
| Enquiry-to-test-drive rate | Distinct enquiries reaching a confirmed test drive divided by eligible enquiries in a defined cohort | Need one consistent lead/enquiry definition and deduplication. |
| Test-drive-to-sale rate | Distinct qualifying test-drive opportunities resulting in confirmed sale divided by a defined matured cohort | No sales result should be fabricated from a vehicle's Sold flag alone. |
| Stock age | Days since actual stock acquisition/intake to report date or sale date | Current `created_at` may not equal stock acquisition date. |

Use SQL queries with documented filters, units, date scope and sample records. These measures demonstrate both application engineering and database analytics without adding unrelated AI features.

# 11. Testing, CI and demonstrable engineering proof

## 11.1 Test pyramid appropriate to this app

| Level | Tools | Example checks |
|---|---|---|
| Domain/unit | pytest with pure Python | Status transitions, overlap boundaries, date/time, codes, validation. |
| SQLite integration | pytest + disposable file DB | FKs, constraints, migrations, rollback, history preservation, parallel connections. |
| GUI | pytest-qt `qtbot` | Form submission, navigation guards, error messages, cancel/reschedule UI, table refresh. |
| Desktop/packaging | Windows manual or automated smoke | First-run account, launch from clean directory, persistent database, backup restore and installer. |
| Static/CI | Ruff/compileall/GitHub Actions | Syntax, formatting/lint, tests and secret avoidance. |

`pytest-qt` supports PyQt5 widgets and simulating user interaction, which makes it suitable once the GUI is reliably launchable in CI. [O15] GitHub Actions provides official Python build/test workflow guidance. [O16]

## 11.2 Specific acceptance gates

| Gate | Release-blocking evidence |
|---|---|
| G0 Baseline | Old core workflows reproduced and screenshots recorded; no old customer data used. |
| G1 Scheduling | Same-slot and overlap, adjacent slot, cancel and two-connection race tests pass. |
| G2 Data preservation | Archive and migration retain all historical links; restore an independently verified backup. |
| G3 Authentication | No hardcoded secrets; first-run, login, logout, invalid login and interrupted setup tested. |
| G4 Workflow | Enquiry -> appointment -> outcome -> opportunity -> inventory change works with sample records. |
| G5 Reporting | SQL totals independently reconciled with seed records and status definitions. |
| G6 GUI | Main form, navigation, keyboard flows, validation and Windows screen sizes checked. |
| G7 Distribution | Build on Windows; clean machine runs without separate Python installed, correct Qt assets and DB placement. |
| G8 Documentation | Architecture, schema/ERD, decisions, screenshots, test evidence and known limitations complete. |

**Release policy:** Zero known critical data-loss or booking-integrity failures. Existing seven `xfail` tests should be converted to real passing assertions as their controls are implemented. A test count alone does not measure maturity.

## 11.3 Packaging and license checks

PyInstaller can bundle Python and dependencies but is not a cross-compiler: a Windows build must be produced on Windows. Include assets and Qt plugins correctly; test in a clean Windows environment. [O17]

A polished installer is valuable only after data location, setup, migrations and the core workflows are stable. Shipping an executable prematurely makes each future DB change harder to diagnose.

# 12. Prioritisation and engineering roadmap

Priorities are ordered by risk reduction and demonstrability, not screen count. Effort labels are *relative engineering sizing*, not delivery promises.

| Milestone | Priority | Size | Deliverables | Acceptance |
|---|---|---|---|---|
| M0 Baseline and domain decisions | P0 | S | Windows GUI walkthrough; capture screen inventory; define duration, staff availability and status vocabulary | Baseline documented and protected; decision record approved. |
| M1 Scheduling integrity | P0 | M | Booking service; intervals; conflict transaction; cancellation events; tests | Two-connection collision case passes; no overlapping active vehicle appointments. |
| M2 Safe database evolution | P0 | M | Migration system; archive; stable IDs; constraints; back up/restore | Existing synthetic legacy data preserved and verified; no cascade history loss. |
| M3 Authentication and data hygiene | P0 | S-M | User-data paths; credential policy; login/reset/recovery; redacted logs | Fresh Windows admin setup and access/logout proven. |
| M4 Coherent dealership journey | P1 | M | Enquiry/opportunity records; appointment outcomes; vehicle status rules | One end-to-end prospect-to-sale scenario works. |
| M5 UX and genuine reporting | P1 | M | Search/filter, booking calendar, dashboard, safe CSV export | Dashboard totals reconcile with fixture; user can complete flow without editing DB directly. |
| M6 Quality and release evidence | P1 | M | pytest-qt, Windows GUI tests, fixtures, installer, recovery rehearsal | Clean install, no real data bundled and all G0-G8 gates accepted. |
| M7 Selective future expansion | P2 | L | Optional multi-user design, notifications or hosted frontend | Separate requirements and acceptance criteria justify each addition. |

## 12.1 Optimised execution order

1. **Freeze the current baseline and clarify booking semantics.** No large UI rewrite.
2. **Implement booking overlap rules behind the current booking form.** Add tests before styling.
3. **Protect historical links and migrate storage safely.** Validate on copied SQLite databases.
4. **Finish local auth/recovery/data-location work.** Reduce security claims to what can be proved.
5. **Add the narrow enquiry and follow-up workflow.** Avoid CRM feature proliferation.
6. **Build a genuine operational dashboard and easy-to-use screens.** Every number originates from persisted test data.
7. **Test GUI and package for Windows.** Only then market the repository as a portfolio-ready application.

## 12.2 Trade-off scoring (analyst judgement)

Scores range from 1 (poor) to 5 (strong). These are **subjective planning scores**, not measured product ratings. Criteria weights: domain fit 30%; verified correctness path 25%; portfolio storytelling 20%; implementation efficiency 15%; release risk 10%.

| Strategy | Domain fit | Correctness path | Story | Efficiency | Risk | Weighted result |
|---|---:|---:|---:|---:|---:|---:|
| A. Scoped desktop dealership system | 5 | 5 | 5 | 5 | 4 | **4.90/5** |
| B. Immediate web-platform pivot | 4 | 3 | 4 | 1 | 2 | **3.10/5** |
| C. Full repair-shop/ERP clone | 2 | 2 | 2 | 1 | 1 | **1.75/5** |

The scoring supports the recommendation, but should not be interpreted as external survey evidence.

# 13. Portfolio and review readiness

A technical reviewer should be able to answer the following by inspecting or running the repository:

- **What real problem is solved?** Prevent scheduling conflicts, retain customer/vehicle history and manage the dealership's test-drive-to-sale journey.
- **Why this data model?** Stable identifiers, FKs, event history, constrained transitions, time intervals and clear cardinalities.
- **How is double-booking prevented?** Explicit interval overlap logic under a SQLite write transaction, plus race tests.
- **How do upgrades protect real users?** Versioned migrations, preflight, backup, reconciliation and rollback proof.
- **How are passwords and private details handled?** Hashed credentials, local app-data storage, synthetic fixtures and an honest security boundary.
- **How is software quality evidenced?** Reproducible unit/integration/GUI tests, CI, visible known limitations and controlled releases.
- **What business insights are real?** Documented SQL measures with precise populations, statuses and date filters.

Repository documentation should include a 60-90 second demonstration GIF/video (optional), 4-6 screenshots, an ERD, a simple architecture diagram, setup guide, synthetic demo-data reset command, test matrix, changelog and a 'known limitations' section. No inflated metrics or 'production-ready' claims without release evidence.

**Example CV/portfolio claim after the milestones pass (not yet accurate):** 'Developed a Python/Qt dealership management application with transactional SQLite booking conflict prevention, versioned database migrations, authenticated local access, customer and vehicle history, automated regression tests and operational reporting.'

# 14. Decisions to make before implementation

1. **Appointment resource rules:** Is the vehicle exclusive for viewings, or only for test drives and collection? Does a consultant have to be available?
2. **Duration and opening hours:** Fixed by appointment type or editable per booking? Which days/hours are bookable?
3. **Inventory statuses:** What does Reserved mean? Does a sale end future appointments automatically or require review?
4. **Outcome:** When can an appointment be marked completed versus attended, no-show, cancelled or rescheduled?
5. **Relationship retention:** Which records may be archived, when may an explicit privacy deletion be requested, and what histories should remain de-identified?
6. **Local-user model:** Is this a single independent dealer's desktop machine or a shared multi-user service? Default recommendation remains single-user.
7. **Distributable license:** Choose a license compatible with PyQt's GPL obligations or plan a separately validated migration to PySide6.

Until these are resolved, use explicit documented defaults in a policy module. Do not silently invent dealership business rules and present them as universal standards.

# 15. Final conclusion

Shongwe Motors can become a credible software-engineering portfolio project **without** becoming a large SaaS product. Its strongest potential is the intersection of relational database design, reliable booking logic, automotive-specific workflows, desktop UX, testing and business reporting.

The optimal route is **depth before breadth**: first eliminate double-booking and historical data loss; then establish safe schema migrations and authentication; then connect vehicles, customers, appointments and opportunities; then add genuinely useful dashboards; finally produce a clean Windows demo with reproducible tests and honest documentation.

There is one governing principle: **every meaningful feature must have a demonstrable business rule, an authoritative data model and a reproducible acceptance test.**

---

# Source register and reference links

All external sources were reviewed for this report on 29 October 2026. Links below identify published materials; vendor and repository capability descriptions should not be mistaken for independent quality assurance.

**Official guidance (O)**

- **O1. Microsoft Bookings, service and staff availability / buffer times:** https://learn.microsoft.com/en-us/microsoft-365/bookings/configure-service-availability?view=o365-worldwide
- **O2. SQLite transactions and BEGIN IMMEDIATE:** https://www.sqlite.org/lang_transaction.html
- **O3. SQLite partial indexes:** https://www.sqlite.org/partialindex.html
- **O4. SQLite foreign keys:** https://www.sqlite.org/foreignkeys.html
- **O5. Alembic migrations for SQLite:** https://alembic.sqlalchemy.org/en/latest/batch.html
- **O6. SQLite Online Backup API:** https://www.sqlite.org/backup.html
- **O7. SQLite write-ahead logging:** https://www.sqlite.org/wal.html
- **O8. Python sqlite3 connection context behaviour:** https://docs.python.org/3/library/sqlite3.html
- **O9. OWASP Password Storage Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **O10. NIST SP 800-63B digital authentication guidance:** https://pages.nist.gov/800-63-4/sp800-63b.html
- **O11. Information Regulator, guidance discussing POPIA security safeguards:** https://inforegulator.org.za/wp-content/uploads/2020/07/InfoRegSA-GuidanceNote-Processing-SpecialPersonalInformation-20210628.pdf
- **O12. Qt model/view programming:** https://doc.qt.io/qt-6/model-view-programming.html
- **O13. Riverbank PyQt license; Qt for Python licensing:** https://en.riverbankcomputing.com/software/pyqt ; https://wiki.qt.io/Qt_for_Python
- **O14. STAR dealership infrastructure guidelines:** https://www.starstandard.org/wp-content/uploads/2022/11/2020STARDealerInfrastructureGuidelineDIG-English.pdf
- **O15. pytest-qt documentation:** https://pytest-qt.readthedocs.io/en/master/intro.html
- **O16. GitHub Python build and test workflows:** https://docs.github.com/en/actions/tutorials/build-and-test-code/python
- **O17. PyInstaller manual:** https://pyinstaller.org/en/stable/

**Vendor/product materials (V)**

- **V1. Refresh Tech dealership product:** https://www.refreshtech.co.za/applications/vehicle-dealerships
- **V2. Tekmetric features:** https://www.tekmetric.com/feature/shop-management
- **V3. AutoLeap features:** https://autoleap.com/features/
- **V4. SimplyBook.me booking features:** https://simplybook.me/index.php/en/booking-system-features
- **V5. Odoo Fleet features:** https://www.odoo.com/app/fleet-features

**Open-source descriptions (R)**

- **R1. Murangi's Car Dealership (UNISA/PyQt5/MySQL):** https://github.com/MurangiTshabuse/car-dealership-management-system
- **R2. vehicle-showroom (reservations, leads, reporting):** https://github.com/Pyaephyo33/vehicle-showroom
- **R3. dms (lead to delivery, audits, permissions):** https://github.com/SaiPranavSoma/dms

**Local source (S)**

- **S. Shongwe Motors repository, tested baseline and documented open defects:** https://github.com/Sonkhe-Shongwe/shongwe-motors ; https://github.com/Sonkhe-Shongwe/shongwe-motors/blob/main/docs/AUDIT_2026-10-29.md ; https://github.com/Sonkhe-Shongwe/shongwe-motors/blob/main/docs/TESTING.md