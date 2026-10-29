# Test evidence and outstanding verification

**29 October 2026, initial code publication checkpoint**

The baseline tests run against fresh, temporary SQLite databases, not user data. The initial source audit recorded **15 passes and 7 strict expected failures**. After securely packaging the application, tests additionally verify administrator creation, password hashing, credential misuse, malformed account handling and absence of hardcoded login variables.

The seven known vulnerabilities have intentionally not been marked fixed. They cover two simultaneous bookings sharing a slot, deletion cascades on both customer and vehicle, reused generated identifiers after deletion, negative money/mileage, invalid booking dates/times and booking a sold vehicle through direct database access. The code is **not** cleared for real business records.

## Reproduce

From the repository root:

```bash
python -m pip install 'pytest>=8,<10'
python -m pytest -q -ra
python -m compileall -q main.py database.py auth.py
```

The GUI isn't imported by the test suite, allowing safe tests without a display server. Qt pages are structurally checked as XML; this **does not** validate real Windows GUI behaviour.

## Manual Windows acceptance not yet completed

- Windows Python 3.11/3.12 environment setup and PyQt5 installation.
- First-run password registration, login, wrong password, logout and guarded navigation.
- Create sample customers and vehicles, then book appointment; verify list and calendar.
- Refresh, delete (synthetic records only), form validations, every navigation button and exit.
- Test repeated launch, no dependencies or records mistakenly committed, and private account storage.

Record the Python version, Windows version, actual observed results and screenshots before claiming Windows release readiness.
