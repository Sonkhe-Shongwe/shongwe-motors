"""Shongwe Motors regression baseline.

All database tests run against fresh temporary SQLite files, never user data.
Known defects remain strict expected failures until fixed.
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from xml.etree import ElementTree

import pytest

SRC = Path(__file__).resolve().parents[1]


def customer(code='CUST-0001', identity='9001015009087'):
    return (code,'Test Customer',identity,'0820000000','test@example.org','Test address','Individual','Phone')


def vehicle(code='VEH-0001', vin='123456789ABCDEFGH', price=125000, mileage=10000, status='Available'):
    return (code,vin,'Toyota','Corolla',2020,'Silver',price,mileage,'Automatic','Petrol','Used',status)


def booking(code='BKG-0001', date='2027-01-05', time='11:00', car='VEH-0001', cust='CUST-0001'):
    return (code,cust,car,'Test Drive',date,time,'Sam','')


@pytest.fixture
def db(tmp_path):
    spec=importlib.util.spec_from_file_location('audit_shongwe_database',SRC/'database.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DB_PATH=tmp_path/'isolated.db'
    module.initialize_database()
    return module


def setup(db):
    db.add_customer(customer()); db.add_vehicle(vehicle())


def test_database_creates_all_tables(db):
    with db.connect() as conn:
        tables={r[0] for r in conn.execute("select name from sqlite_master where type='table'")}
        assert {'customers','vehicles','bookings'}<=tables


def test_foreign_keys_enabled(db):
    with db.connect() as conn: assert conn.execute('pragma foreign_keys').fetchone()[0]==1


def test_insert_and_list_customer(db):
    db.add_customer(customer())
    assert db.list_customers()[0][0]=='CUST-0001'


def test_insert_and_list_vehicle(db):
    db.add_vehicle(vehicle())
    assert db.list_vehicles()[0][0]=='VEH-0001'


def test_insert_and_list_booking(db):
    setup(db); db.add_booking(booking())
    rows=db.list_bookings()
    assert len(rows)==1 and rows[0][0]=='BKG-0001'


def test_duplicate_vin_rejected(db):
    db.add_vehicle(vehicle())
    with pytest.raises(sqlite3.IntegrityError):
        db.add_vehicle(vehicle('VEH-0002'))


def test_duplicate_customer_identifier_rejected(db):
    db.add_customer(customer())
    with pytest.raises(sqlite3.IntegrityError):
        db.add_customer(customer('CUST-0002'))


def test_booking_rejects_unknown_references(db):
    with pytest.raises(sqlite3.IntegrityError): db.add_booking(booking())


def test_booking_choices_exclude_sold(db):
    db.add_vehicle(vehicle(status='Sold'))
    assert db.vehicle_choices()==[]


def test_booking_choices_include_reserved(db):
    db.add_vehicle(vehicle(status='Reserved'))
    assert len(db.vehicle_choices())==1


def test_delete_booking_by_code(db):
    setup(db); db.add_booking(booking()); db.delete_booking('BKG-0001')
    assert db.list_bookings()==[]


def test_initial_code_generation(db):
    assert db.next_customer_code()=='CUST-0001'
    assert db.next_vehicle_code()=='VEH-0001'
    assert db.next_booking_code()=='BKG-0001'


def test_unsupported_table_name_rejected(db):
    with pytest.raises(ValueError): db._next_code('bookings; DROP TABLE customers','BKG')


def test_qt_designer_files_are_well_formed():
    for name in ('login.ui','customers.ui','vehicles.ui','bookings.ui'):
        root=ElementTree.parse(SRC/name).getroot()
        assert root.tag=='ui'


def test_gui_referenced_widgets_present():
    from ast import parse,walk,Attribute,Name
    tree=parse((SRC/'main.py').read_text())
    ui_objects={n.attrib.get('name') for f in SRC.glob('*.ui') for n in ElementTree.parse(f).iter('widget')}
    referenced={n.attr for n in walk(tree) if isinstance(n,Attribute) and isinstance(n.value,Name) and n.value.id=='self'}
    # Only GUI widgets and layouts, not Python class fields and methods.
    widget_like={n for n in referenced if (n.startswith(('line','combo','text','label','radio','table','check','calendar','date','time','spin','double','lcd')) or n.endswith('Button')) and n not in {'timer','calendar_date_changed','date_edit_changed'}}
    assert widget_like-ui_objects==set()


@pytest.mark.xfail(strict=True,reason='Booking uniqueness or overlap prevention is not implemented')
def test_same_vehicle_same_slot_must_be_rejected(db):
    setup(db)
    db.add_booking(booking())
    with pytest.raises(sqlite3.IntegrityError): db.add_booking(booking('BKG-0002'))


@pytest.mark.xfail(strict=True,reason='Customer deletion cascades and removes booking history')
def test_customer_delete_must_preserve_booking_history(db):
    setup(db); db.add_booking(booking())
    db.delete_customer('CUST-0001')
    with db.connect() as conn: assert conn.execute('select count(*) from bookings').fetchone()[0]==1


@pytest.mark.xfail(strict=True,reason='Vehicle deletion cascades and removes booking history')
def test_vehicle_delete_must_preserve_booking_history(db):
    setup(db); db.add_booking(booking())
    db.delete_vehicle('VEH-0001')
    with db.connect() as conn: assert conn.execute('select count(*) from bookings').fetchone()[0]==1


@pytest.mark.xfail(strict=True,reason='Codes use MAX(id)+1 and are reused after last-row deletion')
def test_customer_codes_must_not_be_reused(db):
    db.add_customer(customer())
    db.add_customer(customer('CUST-0002','9101015009084'))
    db.delete_customer('CUST-0002')
    assert db.next_customer_code()=='CUST-0003'


@pytest.mark.xfail(strict=True,reason='Database has no range CHECK constraints for price and mileage')
def test_negative_vehicle_values_must_be_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.add_vehicle(vehicle(price=-1,mileage=-5))


@pytest.mark.xfail(strict=True,reason='Database has no validation for date/time text and available status')
def test_invalid_booking_datetime_must_be_rejected(db):
    setup(db)
    with pytest.raises((sqlite3.IntegrityError,ValueError)):
        db.add_booking(booking(date='not-a-date',time='99:99'))


@pytest.mark.xfail(strict=True,reason='Bookings can be created directly against sold vehicles')
def test_sold_vehicle_cannot_be_booked_via_service(db):
    db.add_customer(customer()); db.add_vehicle(vehicle(status='Sold'))
    with pytest.raises((sqlite3.IntegrityError,ValueError)):
        db.add_booking(booking())
