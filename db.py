import sqlite3
import random
import string
import json

def add_participant(event_id, name, location, can_drive, seats, sub_event):
    conn = sqlite3.connect("ridebuddy.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO participants (event_id, name, location, can_drive, seats, sub_event)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event_id, name, location, can_drive, seats, sub_event))

    conn.commit()
    conn.close()

def generate_event_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_event(data):
    conn = sqlite3.connect("ridebuddy.db")
    cur = conn.cursor()

    email = data.get("email")
    name = data.get("event_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    sub_events = json.dumps(data.get("sub_events", [])) 
    host_code = generate_host_code()
    description = data.get("description","")
    event_code = generate_event_code()

    cur.execute("""
        INSERT INTO events (email, event_name, start_date, end_date, sub_events, host_code, event_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, name, start_date, end_date, sub_events, host_code, event_code))

    conn.commit()
    event_id = cur.lastrowid
    conn.close()

    return event_code

def get_event_by_code(event_code):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE event_code = ?", (event_code,))
    row = cur.fetchone()
    conn.close()
    
    event = dict(row)
    event['sub_events'] = json.loads(event['sub_events']) if event['sub_events'] else []
    return event


def get_participants(event_id):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM participants WHERE event_id = ?", (event_id,))
    rows = cur.fetchall()
    participants = [dict(row) for row in rows]

    conn.close()
    return participants

def get_drivers(event_id):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(""" SELECT * FROM participants WHERE event_id = ? AND can_drive = 1 """, (event_id,))
    rows = cur.fetchall()
    drivers = [dict(row) for row in rows]

    conn.close()
    return drivers

def generate_host_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def delete_event(event_id):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()

    return None

def get_event(event_id):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()
    event = dict(row)

    event['sub_events'] = json.loads(event['sub_events']) if event['sub_events'] else []
    return event
    
def validate_host(event_id, host_code):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT host_code FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()

    if row and row["host_code"] == host_code:
        return True
    return False
    
