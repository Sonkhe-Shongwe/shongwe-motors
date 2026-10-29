"""SQLite database layer for Shongwe Motors.

The database is created automatically in the project folder.
All SQL uses parameters to avoid unsafe string concatenation.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parent / "shongwe_motors.db"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    schema = """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        id_number TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        customer_type TEXT NOT NULL,
        preferred_contact TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_code TEXT UNIQUE NOT NULL,
        vin TEXT UNIQUE NOT NULL,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        model_year INTEGER NOT NULL,
        colour TEXT,
        price REAL NOT NULL,
        mileage INTEGER NOT NULL,
        transmission TEXT NOT NULL,
        fuel_type TEXT NOT NULL,
        vehicle_condition TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_code TEXT UNIQUE NOT NULL,
        customer_code TEXT NOT NULL,
        vehicle_code TEXT NOT NULL,
        booking_type TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        booking_time TEXT NOT NULL,
        consultant TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_code) REFERENCES customers(customer_code) ON DELETE CASCADE,
        FOREIGN KEY (vehicle_code) REFERENCES vehicles(vehicle_code) ON DELETE CASCADE
    );
    """
    with connect() as connection:
        connection.executescript(schema)
        connection.commit()


def _next_code(table: str, prefix: str) -> str:
    allowed = {"customers", "vehicles", "bookings"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    with connect() as connection:
        row = connection.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table}").fetchone()
    return f"{prefix}-{int(row[0]):04d}"


def next_customer_code() -> str:
    return _next_code("customers", "CUST")


def next_vehicle_code() -> str:
    return _next_code("vehicles", "VEH")


def next_booking_code() -> str:
    return _next_code("bookings", "BKG")


def add_customer(values: Iterable[object]) -> None:
    sql = """
    INSERT INTO customers
    (customer_code, full_name, id_number, phone, email, address, customer_type, preferred_contact)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with connect() as connection:
        connection.execute(sql, tuple(values))
        connection.commit()


def list_customers() -> list[tuple]:
    with connect() as connection:
        return connection.execute(
            "SELECT customer_code, full_name, phone, email, customer_type FROM customers ORDER BY id DESC"
        ).fetchall()


def customer_choices() -> list[tuple[str, str]]:
    with connect() as connection:
        return connection.execute(
            "SELECT customer_code, full_name FROM customers ORDER BY full_name"
        ).fetchall()


def delete_customer(customer_code: str) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM customers WHERE customer_code = ?", (customer_code,))
        connection.commit()


def add_vehicle(values: Iterable[object]) -> None:
    sql = """
    INSERT INTO vehicles
    (vehicle_code, vin, make, model, model_year, colour, price, mileage,
     transmission, fuel_type, vehicle_condition, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with connect() as connection:
        connection.execute(sql, tuple(values))
        connection.commit()


def list_vehicles() -> list[tuple]:
    with connect() as connection:
        return connection.execute(
            "SELECT vehicle_code, make, model, model_year, price, status FROM vehicles ORDER BY id DESC"
        ).fetchall()


def vehicle_choices() -> list[tuple[str, str]]:
    with connect() as connection:
        return connection.execute(
            """SELECT vehicle_code, make || ' ' || model
               FROM vehicles
               WHERE status IN ('Available', 'Reserved')
               ORDER BY make, model"""
        ).fetchall()


def delete_vehicle(vehicle_code: str) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM vehicles WHERE vehicle_code = ?", (vehicle_code,))
        connection.commit()


def add_booking(values: Iterable[object]) -> None:
    sql = """
    INSERT INTO bookings
    (booking_code, customer_code, vehicle_code, booking_type, booking_date,
     booking_time, consultant, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with connect() as connection:
        connection.execute(sql, tuple(values))
        connection.commit()


def list_bookings() -> list[tuple]:
    sql = """
    SELECT b.booking_code,
           c.full_name,
           v.make || ' ' || v.model,
           b.booking_type,
           b.booking_date,
           b.booking_time,
           b.consultant
    FROM bookings b
    JOIN customers c ON c.customer_code = b.customer_code
    JOIN vehicles v ON v.vehicle_code = b.vehicle_code
    ORDER BY b.booking_date DESC, b.booking_time DESC
    """
    with connect() as connection:
        return connection.execute(sql).fetchall()


def delete_booking(booking_code: str) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM bookings WHERE booking_code = ?", (booking_code,))
        connection.commit()
