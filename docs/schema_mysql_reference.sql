-- Historical assignment reference only. The application uses SQLite, not MySQL.
-- This script is not used at runtime and must not be treated as migration code.
CREATE DATABASE IF NOT EXISTS shongwe_motors;
USE shongwe_motors;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    id_number VARCHAR(13) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    address TEXT NOT NULL,
    customer_type VARCHAR(30) NOT NULL,
    preferred_contact VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_code VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(17) UNIQUE NOT NULL,
    make VARCHAR(80) NOT NULL,
    model VARCHAR(80) NOT NULL,
    model_year INT NOT NULL,
    colour VARCHAR(40),
    price DECIMAL(12,2) NOT NULL,
    mileage INT NOT NULL,
    transmission VARCHAR(30) NOT NULL,
    fuel_type VARCHAR(30) NOT NULL,
    vehicle_condition VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_code VARCHAR(20) UNIQUE NOT NULL,
    customer_code VARCHAR(20) NOT NULL,
    vehicle_code VARCHAR(20) NOT NULL,
    booking_type VARCHAR(50) NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    consultant VARCHAR(120),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_code) REFERENCES customers(customer_code) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_code) REFERENCES vehicles(vehicle_code) ON DELETE CASCADE
);
