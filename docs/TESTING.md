# Baseline test evidence | 29 October 2026

Source: owner-provided original ZIP (SHA-256 in AUDIT), tested locally, not yet committed here.

**Observed:** 15 pytest tests passed, 7 strict expected failures (xfail) in approximately 0.55 seconds. Valid Python syntax for main.py/database.py, all four .ui documents well formed, referenced GUI widgets present in UI definitions.

**Confirmed xfail:** missing duplicate time-slot rejection; deletion cascade from customer; deletion cascade from vehicle; previously used code reused after last-row deletion; negative vehicle price/mileage accepted; invalid booking date/time accepted; sold vehicle bookable directly through database API.

**Existing passing checks:** schema created; FK enabled; basic customer/vehicle/booking CRUD; duplicate VIN and customer ID rejected; unknown references rejected; Sold excluded from UI choices; Reserved included; delete booking; initial code allocation; table-name injection guard; valid UI XML and widget references.

Additional direct probes ran on new disposable SQLite files, never the original project database.

**Not tested:** live Qt GUI (PyQt5 unavailable and dependency installation blocked), multi-process concurrency, Windows packaging, database migrations, secure account creation, performance, true MySQL integration.

The private reproducible audit package contains tests/test_database_baseline.py, probe_results.json and audit_probe.py. Run from a directory containing the original assignment source folder as its sibling: python -m pytest -q tests/test_database_baseline.py -r a. The 7 tests marked xfail(strict=True) must become normal passing tests as safeguards are implemented. A green baseline with expected failures is **not** release readiness.