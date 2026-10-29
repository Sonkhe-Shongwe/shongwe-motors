@echo off
pyuic5 login.ui -o login_ui.py
pyuic5 customers.ui -o customers_ui.py
pyuic5 vehicles.ui -o vehicles_ui.py
pyuic5 bookings.ui -o bookings_ui.py
echo UI conversion complete.
pause
