# Windows smoke-test checklist

1. Install Python 3.11 or 3.12 and ensure `py -3 --version` works.
2. Clone or download the entire repository. Do not extract individual `.py` files without the `.ui` pages and `assets/` directory.
3. Run `setup_windows.bat` once (creates `.venv`; needs package access).
4. Run `run_project.bat`. The login window should appear. If no account exists, a dialog requests a new administrator username and password of 12+ characters.
5. Complete administrator setup, sign in, confirm the Customers window displays and login cannot be bypassed through navigation.
6. Test save/list customer; save/list vehicle; save/list booking and calendar selection. Use fictitious values only.
7. Confirm Logout returns to Login. Restart the app and sign in with your chosen password. Wrong passwords must fail.
8. Verify `shongwe_motors.db` was created next to source code and is not visible in `git status --short` due `.gitignore`.
9. Confirm `%APPDATA%\ShongweMotors\admin.json` exists and contains a hash, not your password.
10. Record results in `docs/TESTING.md`. Do not delete records with bookings except in a disposable database until archive/history fixes land.

## Troubleshooting

- `py` not found: reinstall Python with the launcher and ensure it is on PATH.
- `No module named PyQt5`: run `setup_windows.bat` and confirm its pip step succeeds.
- Qt platform plugin error: use a supported Python architecture and PyQt5 wheel; remove a broken environment and recreate `.venv`.
- Permission errors: extract to a writable folder, not Program Files.
- Forgotten admin password: no supported reset interface yet. Do **not** remove the credential record from a populated live installation without understanding the consequences. Save user data first.
