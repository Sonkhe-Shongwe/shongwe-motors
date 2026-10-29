# Shongwe Motors

A Python **PyQt5 desktop dealership administration and appointment-booking application**, using SQLite. The original four Qt Designer screens are preserved while the project is being hardened for an engineering portfolio.

**Status:** Runnable source published, isolated database/authentication tests verified. **Not production-ready:** booking conflict prevention, deletion/history retention and database validation still need the fixes tracked below. Windows GUI operation needs confirmation on a Windows system.

## Features available in the source

- First-run administrator account creation and login (no shared default password).
- Customer registration, table view and deletion.
- Vehicle inventory management, listing and live clock.
- Appointment booking with customer and vehicle selectors, calendar and time field.
- Local SQLite storage initialised on first launch.
- Four editable Qt Designer `.ui` files. No `pyuic5` compilation required to run.

**Data warning:** The original database deletion behaviour can cascade to booking history, and scheduling currently permits conflicting appointments. Use synthetic sample data until the P0 upgrades are complete.

## Windows installation and launch

1. Install Python **3.11 or 3.12** for Windows, with the Python launcher (`py`) available.
2. [Download ZIP](https://github.com/Sonkhe-Shongwe/shongwe-motors/archive/refs/heads/main.zip) and extract it, or clone the repository:

   ```powershell
   git clone https://github.com/Sonkhe-Shongwe/shongwe-motors.git
   cd shongwe-motors
   ```
3. Double-click **`setup_windows.bat`** to create `.venv` and install the PyQt5 dependency. This requires internet access for the initial dependency installation.
4. Double-click **`run_project.bat`**. Alternatively:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```
5. At first launch, enter a new administrator username and a password of at least 12 characters, confirm it, and sign in. **There is no default username or password.**

### Manual cross-platform launch

```bash
python -m venv .venv
# Activate the venv for your platform, then:
python -m pip install -r requirements.txt
python main.py
```

Requires a graphical desktop and Qt-compatible display server. The default database file is `shongwe_motors.db` beside `database.py`; its content is excluded from Git. Do not share or check in a populated database. The administrator record is stored **outside the repository** in the user's application-data directory (Windows: `%APPDATA%\ShongweMotors\admin.json`). Back up credentials and user data privately; there is currently no password-reset UI.

## Run automated tests

Tests use disposable SQLite databases and do **not** access any existing customer records:

```bash
python -m pip install 'pytest>=8,<10'
python -m pytest -q
```

The original known defects are marked with `xfail(strict=True)`. Expected failures are **not proof of correct behaviour**. CI runs syntax, database and login-store tests on Python 3.11 and 3.12. Since PyQt5 isn't required for these unit tests, GUI smoke testing is a separate manual acceptance gate.

## Project layout

| Location | Responsibility |
|---|---|
| `main.py` | PyQt5 windows and navigation controller |
| `auth.py` | First-run admin and password hashing |
| `database.py` | SQLite schema and CRUD operations |
| `*.ui`, `assets/` | Qt Designer screens and logo |
| `setup_windows.bat`, `run_project.bat` | Windows setup and startup |
| `tests/` | Reproducible isolated regression tests |
| `docs/` | Audit, roadmap, test findings and development handoff |

## Engineering progress and known risks

Review the [source audit](docs/AUDIT_2026-10-29.md), [roadmap](docs/ROADMAP.md), [test evidence](docs/TESTING.md) and [continuation handoff](docs/CONTINUE_HERE.md). The P0 implementation issues are: [#2 double-bookings](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/2), [#3 deletion/history loss](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/3), [#4 authentication hardening](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/4) and [#5 data integrity](https://github.com/Sonkhe-Shongwe/shongwe-motors/issues/5).

The shipped password storage replaces the demonstration plaintext credential with a salted PBKDF2 hash and basic GUI access control. **This is not a multi-user security boundary**: local filesystem and OS account permissions protect the SQLite and credential files. Other security work remains planned.

SQLite is the actual application database. `docs/schema_mysql_reference.sql` is a **historical reference only**, not an active integration.
