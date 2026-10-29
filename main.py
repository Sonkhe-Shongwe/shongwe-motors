"""Shongwe Motors desktop administration application.

The existing Qt Designer screens are loaded at runtime for easy maintenance.
"""

from __future__ import annotations

import re
import time
import sqlite3
import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import (
    QApplication,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QTableWidgetItem,
)

import database
import auth

BASE_DIR = Path(__file__).resolve().parent


def ui_path(filename: str) -> str:
    return str(BASE_DIR / filename)


def set_logo(label) -> None:
    pixmap = QtGui.QPixmap(str(BASE_DIR / "assets" / "shongwe_motors_logo.png"))
    if not pixmap.isNull():
        label.setPixmap(pixmap)
        label.setScaledContents(True)


def fill_table(table, rows: list[tuple]) -> None:
    table.setRowCount(len(rows))
    for row_index, row_values in enumerate(rows):
        for column_index, value in enumerate(row_values):
            text = "" if value is None else str(value)
            if isinstance(value, float):
                text = f"R {value:,.2f}"
            table.setItem(row_index, column_index, QTableWidgetItem(text))
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.resizeRowsToContents()


class AppController:
    def __init__(self) -> None:
        self.current_user: str | None = None
        self.login_window = LoginWindow(self)
        self.customer_window = CustomerWindow(self)
        self.vehicle_window = VehicleWindow(self)
        self.booking_window = BookingWindow(self)
        self.windows = [
            self.login_window,
            self.customer_window,
            self.vehicle_window,
            self.booking_window,
        ]

    def _show_only(self, target: QMainWindow) -> None:
        for window in self.windows:
            if window is not target:
                window.hide()
        target.show()
        target.raise_()
        target.activateWindow()

    def show_login(self) -> None:
        # Log out before showing the login form, even after another window.
        self.current_user = None
        self.login_window.reset_form()
        self._show_only(self.login_window)
        if not auth.has_admin():
            self.login_window.first_run_setup()

    def _require_login(self) -> bool:
        if self.current_user is None:
            self.show_login()
            return False
        return True

    def show_customers(self) -> None:
        if not self._require_login():
            return
        self.customer_window.prepare()
        self._show_only(self.customer_window)

    def show_vehicles(self) -> None:
        if not self._require_login():
            return
        self.vehicle_window.prepare()
        self._show_only(self.vehicle_window)

    def show_bookings(self) -> None:
        if not self._require_login():
            return
        self.booking_window.prepare()
        self._show_only(self.booking_window)


class LoginWindow(QMainWindow):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        uic.loadUi(ui_path("login.ui"), self)
        self.controller = controller
        self.failed_attempts = 0
        self.lock_until = 0.0
        set_logo(self.labelLogo)

        self.LoginButton.clicked.connect(self.attempt_login)
        self.CancelButton.clicked.connect(self.cancel_application)
        self.checkShowPassword.toggled.connect(self.toggle_password)
        self.linePassword.returnPressed.connect(self.attempt_login)
        self.lineUsername.returnPressed.connect(self.linePassword.setFocus)

    def toggle_password(self, checked: bool) -> None:
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.linePassword.setEchoMode(mode)

    def first_run_setup(self) -> None:
        """Create the first administrator without shipping a shared password."""
        QMessageBox.information(
            self, "First-run setup",
            "Create an administrator account for this Windows user. "
            "The password will be stored as a salted hash, outside the source directory.",
        )
        while True:
            username, ok = QInputDialog.getText(
                self, "Create administrator", "Administrator username (3-64 letters, digits, ._-):"
            )
            if not ok:
                QtCore.QTimer.singleShot(0, QApplication.quit)
                return
            password, ok = QInputDialog.getText(
                self, "Create administrator", "Password (minimum 12 characters):",
                QLineEdit.Password,
            )
            if not ok:
                QtCore.QTimer.singleShot(0, QApplication.quit)
                return
            confirm, ok = QInputDialog.getText(
                self, "Create administrator", "Confirm password:", QLineEdit.Password
            )
            if not ok:
                QtCore.QTimer.singleShot(0, QApplication.quit)
                return
            if password != confirm:
                QMessageBox.warning(self, "Passwords differ", "Enter the same password twice.")
                continue
            try:
                auth.create_admin(username, password)
            except ValueError as error:
                QMessageBox.warning(self, "Invalid account", str(error))
                continue
            except (OSError, auth.AuthStoreError) as error:
                QMessageBox.critical(self, "Account setup failed", f"Cannot save administrator account: {error}")
                QtCore.QTimer.singleShot(0, QApplication.quit)
                return
            self.lineUsername.setText(username.strip())
            self.linePassword.setFocus()
            QMessageBox.information(self, "Account created", "Your account is ready. Sign in to continue.")
            return

    def attempt_login(self) -> None:
        username = self.lineUsername.text().strip()
        password = self.linePassword.text()
        if time.monotonic() < self.lock_until:
            QMessageBox.warning(self, "Please retry later", "Too many attempts. Try again in 30 seconds.")
            return
        if not username or not password:
            QMessageBox.warning(self, "Missing details", "Enter both the username and password.")
            return
        try:
            matched = auth.verify_admin(username, password)
        except (OSError, auth.AuthStoreError) as error:
            QMessageBox.critical(self, "Authentication unavailable", f"The administrator account cannot be read: {error}")
            return
        if matched:
            self.failed_attempts = 0
            self.linePassword.clear()
            self.controller.current_user = username
            QMessageBox.information(self, "Login successful", "Welcome to Shongwe Motors.")
            self.controller.show_customers()
            return
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.failed_attempts = 0
            self.lock_until = time.monotonic() + 30
        QMessageBox.warning(self, "Login failed", "The username or password is incorrect.")
        self.linePassword.clear()
        self.linePassword.setFocus()

    def cancel_application(self) -> None:
        answer = QMessageBox.question(
            self,
            "Exit system",
            "Are you sure you want to close Shongwe Motors?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            QApplication.quit()

    def reset_form(self) -> None:
        self.lineUsername.clear()
        self.linePassword.clear()
        self.checkShowPassword.setChecked(False)
        self.lineUsername.setFocus()


class CustomerWindow(QMainWindow):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        uic.loadUi(ui_path("customers.ui"), self)
        self.controller = controller
        set_logo(self.labelLogo)

        self.SaveButton.clicked.connect(self.save_customer)
        self.ClearButton.clicked.connect(self.clear_fields)
        self.DeleteButton.clicked.connect(self.delete_selected)
        self.RefreshButton.clicked.connect(self.refresh_table)
        self.NextButton.clicked.connect(self.controller.show_vehicles)
        self.LogoutButton.clicked.connect(self.logout)

    def prepare(self) -> None:
        self.labelLoggedUser.setText(f"Logged in as: {self.controller.current_user} | Administrator")
        self.lineCustomerCode.setText(database.next_customer_code())
        self.refresh_table()

    def preferred_contact(self) -> str:
        if self.radioEmail.isChecked():
            return "Email"
        if self.radioSMS.isChecked():
            return "SMS"
        return "Phone"

    def validate(self) -> tuple[bool, str]:
        required = [
            self.lineFullName.text().strip(),
            self.lineIdNumber.text().strip(),
            self.linePhone.text().strip(),
            self.lineEmail.text().strip(),
            self.textAddress.toPlainText().strip(),
        ]
        if not all(required):
            return False, "Complete all fields marked with an asterisk."
        if not (self.lineIdNumber.text().isdigit() and len(self.lineIdNumber.text()) == 13):
            return False, "The South African ID number must contain exactly 13 digits."
        phone = self.linePhone.text().strip()
        if not (phone.isdigit() and len(phone) == 10):
            return False, "The phone number must contain exactly 10 digits."
        email = self.lineEmail.text().strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return False, "Enter a valid email address."
        return True, ""

    def save_customer(self) -> None:
        valid, message = self.validate()
        if not valid:
            QMessageBox.warning(self, "Invalid customer details", message)
            return

        values = (
            self.lineCustomerCode.text(),
            self.lineFullName.text().strip(),
            self.lineIdNumber.text().strip(),
            self.linePhone.text().strip(),
            self.lineEmail.text().strip(),
            self.textAddress.toPlainText().strip(),
            self.comboCustomerType.currentText(),
            self.preferred_contact(),
        )
        try:
            database.add_customer(values)
        except sqlite3.IntegrityError as error:
            QMessageBox.warning(self, "Customer not saved", f"A duplicate ID number or record exists.\n\n{error}")
            return

        QMessageBox.information(self, "Customer saved", "The customer record was saved successfully.")
        self.clear_fields()
        self.refresh_table()

    def clear_fields(self) -> None:
        self.lineCustomerCode.setText(database.next_customer_code())
        self.lineFullName.clear()
        self.lineIdNumber.clear()
        self.linePhone.clear()
        self.lineEmail.clear()
        self.textAddress.clear()
        self.comboCustomerType.setCurrentIndex(0)
        self.radioPhone.setChecked(True)
        self.lineFullName.setFocus()

    def refresh_table(self) -> None:
        fill_table(self.tableCustomers, database.list_customers())

    def delete_selected(self) -> None:
        row = self.tableCustomers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a customer row first.")
            return
        code = self.tableCustomers.item(row, 0).text()
        answer = QMessageBox.question(self, "Delete customer", f"Delete customer {code}?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            database.delete_customer(code)
            self.refresh_table()
            self.lineCustomerCode.setText(database.next_customer_code())

    def logout(self) -> None:
        answer = QMessageBox.question(self, "Logout", "Return to the Login page?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.controller.show_login()


class VehicleWindow(QMainWindow):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        uic.loadUi(ui_path("vehicles.ui"), self)
        self.controller = controller
        set_logo(self.labelLogo)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.show_clock)
        self.timer.start(1000)
        self.show_clock()

        self.SaveButton.clicked.connect(self.save_vehicle)
        self.ClearButton.clicked.connect(self.clear_fields)
        self.DeleteButton.clicked.connect(self.delete_selected)
        self.RefreshButton.clicked.connect(self.refresh_table)
        self.BackButton.clicked.connect(self.controller.show_customers)
        self.NextButton.clicked.connect(self.controller.show_bookings)

    def prepare(self) -> None:
        self.lineVehicleCode.setText(database.next_vehicle_code())
        self.refresh_table()

    def show_clock(self) -> None:
        self.lcdClock.display(QTime.currentTime().toString("HH:mm:ss"))

    def condition(self) -> str:
        return "Used" if self.radioUsed.isChecked() else "New"

    def validate(self) -> tuple[bool, str]:
        if not self.lineVIN.text().strip() or not self.lineMake.text().strip() or not self.lineModel.text().strip():
            return False, "VIN, make and model are required."
        vin = self.lineVIN.text().strip()
        if len(vin) < 8:
            return False, "Enter a valid VIN with at least 8 characters."
        if self.doublePrice.value() <= 0:
            return False, "The vehicle price must be greater than zero."
        return True, ""

    def save_vehicle(self) -> None:
        valid, message = self.validate()
        if not valid:
            QMessageBox.warning(self, "Invalid vehicle details", message)
            return
        values = (
            self.lineVehicleCode.text(),
            self.lineVIN.text().strip().upper(),
            self.lineMake.text().strip(),
            self.lineModel.text().strip(),
            self.spinYear.value(),
            self.lineColour.text().strip(),
            self.doublePrice.value(),
            self.spinMileage.value(),
            self.comboTransmission.currentText(),
            self.comboFuel.currentText(),
            self.condition(),
            self.comboStatus.currentText(),
        )
        try:
            database.add_vehicle(values)
        except sqlite3.IntegrityError as error:
            QMessageBox.warning(self, "Vehicle not saved", f"The VIN or vehicle record already exists.\n\n{error}")
            return
        QMessageBox.information(self, "Vehicle saved", "The vehicle was added to the inventory.")
        self.clear_fields()
        self.refresh_table()

    def clear_fields(self) -> None:
        self.lineVehicleCode.setText(database.next_vehicle_code())
        self.lineVIN.clear()
        self.lineMake.clear()
        self.lineModel.clear()
        self.spinYear.setValue(2026)
        self.lineColour.clear()
        self.doublePrice.setValue(0)
        self.spinMileage.setValue(0)
        self.comboTransmission.setCurrentIndex(0)
        self.comboFuel.setCurrentIndex(0)
        self.radioNew.setChecked(True)
        self.comboStatus.setCurrentIndex(0)
        self.lineVIN.setFocus()

    def refresh_table(self) -> None:
        fill_table(self.tableVehicles, database.list_vehicles())

    def delete_selected(self) -> None:
        row = self.tableVehicles.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a vehicle row first.")
            return
        code = self.tableVehicles.item(row, 0).text()
        answer = QMessageBox.question(self, "Delete vehicle", f"Delete vehicle {code}?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            database.delete_vehicle(code)
            self.refresh_table()
            self.lineVehicleCode.setText(database.next_vehicle_code())


class BookingWindow(QMainWindow):
    def __init__(self, controller: AppController) -> None:
        super().__init__()
        uic.loadUi(ui_path("bookings.ui"), self)
        self.controller = controller
        set_logo(self.labelLogo)

        self.calendarWidget.selectionChanged.connect(self.calendar_date_changed)
        self.dateBooking.dateChanged.connect(self.date_edit_changed)
        self.SaveButton.clicked.connect(self.save_booking)
        self.ClearButton.clicked.connect(self.clear_fields)
        self.DeleteButton.clicked.connect(self.delete_selected)
        self.RefreshButton.clicked.connect(self.prepare)
        self.BackButton.clicked.connect(self.controller.show_vehicles)
        self.ExitButton.clicked.connect(self.exit_system)

        self.dateBooking.setCalendarPopup(True)
        self.dateBooking.setDate(QDate.currentDate())
        self.dateBooking.setMinimumDate(QDate.currentDate())
        self.calendarWidget.setMinimumDate(QDate.currentDate())
        self.timeBooking.setTime(QTime.currentTime())

    def prepare(self) -> None:
        self.lineBookingCode.setText(database.next_booking_code())
        self.populate_choices()
        self.refresh_table()

    def populate_choices(self) -> None:
        current_customer = self.comboCustomer.currentData()
        current_vehicle = self.comboVehicle.currentData()

        self.comboCustomer.clear()
        for code, name in database.customer_choices():
            self.comboCustomer.addItem(f"{name} ({code})", code)

        self.comboVehicle.clear()
        for code, description in database.vehicle_choices():
            self.comboVehicle.addItem(f"{description} ({code})", code)

        if current_customer:
            index = self.comboCustomer.findData(current_customer)
            if index >= 0:
                self.comboCustomer.setCurrentIndex(index)
        if current_vehicle:
            index = self.comboVehicle.findData(current_vehicle)
            if index >= 0:
                self.comboVehicle.setCurrentIndex(index)

    def calendar_date_changed(self) -> None:
        self.dateBooking.blockSignals(True)
        self.dateBooking.setDate(self.calendarWidget.selectedDate())
        self.dateBooking.blockSignals(False)

    def date_edit_changed(self, selected_date: QDate) -> None:
        self.calendarWidget.blockSignals(True)
        self.calendarWidget.setSelectedDate(selected_date)
        self.calendarWidget.blockSignals(False)

    def validate(self) -> tuple[bool, str]:
        if self.comboCustomer.count() == 0:
            return False, "Create at least one customer before saving a booking."
        if self.comboVehicle.count() == 0:
            return False, "Create at least one available vehicle before saving a booking."
        if self.dateBooking.date() < QDate.currentDate():
            return False, "The booking date cannot be in the past."
        return True, ""

    def save_booking(self) -> None:
        valid, message = self.validate()
        if not valid:
            QMessageBox.warning(self, "Booking not saved", message)
            return
        values = (
            self.lineBookingCode.text(),
            self.comboCustomer.currentData(),
            self.comboVehicle.currentData(),
            self.comboBookingType.currentText(),
            self.dateBooking.date().toString("yyyy-MM-dd"),
            self.timeBooking.time().toString("HH:mm"),
            self.lineConsultant.text().strip(),
            self.textNotes.toPlainText().strip(),
        )
        try:
            database.add_booking(values)
        except sqlite3.IntegrityError as error:
            QMessageBox.warning(self, "Booking not saved", f"The booking could not be saved.\n\n{error}")
            return
        QMessageBox.information(self, "Booking saved", "The appointment was scheduled successfully.")
        self.clear_fields()
        self.refresh_table()

    def clear_fields(self) -> None:
        self.lineBookingCode.setText(database.next_booking_code())
        if self.comboCustomer.count():
            self.comboCustomer.setCurrentIndex(0)
        if self.comboVehicle.count():
            self.comboVehicle.setCurrentIndex(0)
        self.comboBookingType.setCurrentIndex(0)
        today = QDate.currentDate()
        self.dateBooking.setDate(today)
        self.calendarWidget.setSelectedDate(today)
        self.timeBooking.setTime(QTime.currentTime())
        self.lineConsultant.clear()
        self.textNotes.clear()

    def refresh_table(self) -> None:
        fill_table(self.tableBookings, database.list_bookings())

    def delete_selected(self) -> None:
        row = self.tableBookings.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a booking row first.")
            return
        code = self.tableBookings.item(row, 0).text()
        answer = QMessageBox.question(self, "Delete booking", f"Delete booking {code}?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            database.delete_booking(code)
            self.refresh_table()
            self.lineBookingCode.setText(database.next_booking_code())

    def exit_system(self) -> None:
        answer = QMessageBox.question(
            self,
            "Exit system",
            "Are you sure you want to exit Shongwe Motors?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            QApplication.quit()


def main() -> int:
    database.initialize_database()
    app = QApplication(sys.argv)
    app.setApplicationName("Shongwe Motors Administration System")
    app.setStyle("Fusion")
    controller = AppController()
    controller.show_login()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
