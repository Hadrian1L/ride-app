import os
import sqlite3
import random
import string
import json
import logging
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()
logger = logging.getLogger(__name__)

def add_participant(event_id, name, location, can_drive, seats, sub_event):
    try:
        conn = sqlite3.connect("ridebuddy.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO participants (event_id, name, location, can_drive, seats, sub_event)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, name, location, can_drive, seats, sub_event))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error in add_participant: {str(e)}")
        return False

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
    location = data.get("location")
    event_code = generate_event_code()

    cur.execute("""
        INSERT INTO events (email, event_name, start_date, end_date, location, sub_events, host_code, event_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, name, start_date, end_date, location, sub_events, host_code, event_code))

    conn.commit()
    event_id = cur.lastrowid
    conn.close()

    email_host(email, event_code, host_code)
    return event_code, host_code

def get_event_by_code(event_code):
    conn = sqlite3.connect("ridebuddy.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE event_code = ?", (event_code,))
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
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
    
    if row is None:
        return None
    
    event = dict(row)
    event['sub_events'] = json.loads(event['sub_events']) if event['sub_events'] else []
    return event


def email_host(to_email, event_code, host_code):
    try:
        EMAIL = os.getenv("EMAIL")
        APP_PASSWORD = os.getenv("APP_PASSWORD")
        
        if not EMAIL or not APP_PASSWORD:
            logger.error("Email credentials not configured")
            return False
        
        subject = "Your RideBuddy Event Info"
        body = f"""Welcome to RideBuddy!

Event Code: {event_code}
Host Code: {host_code}

Use these codes to manage and start your event.

Important: Keep these codes safe. Anyone with the event code can join your ride.
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())
        
        logger.info(f"Email sent to {to_email}")
        return True
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False
    
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
    
def email_rides(to_email, event_name, assignments):
    """Send ride assignments to event host"""
    try:
        EMAIL = os.getenv("EMAIL")
        APP_PASSWORD = os.getenv("APP_PASSWORD")
        
        if not EMAIL or not APP_PASSWORD:
            logger.error("Email credentials not configured")
            return False
        
        # Format assignments for email
        assignments_text = ""
        for i, assignment in enumerate(assignments, 1):
            driver = assignment.get('driver', {})
            riders = assignment.get('riders', [])
            assignments_text += f"\n\nTrip {i}:\n"
            assignments_text += f"Driver: {driver.get('name', 'Unknown')} ({driver.get('location', 'Unknown')})\n"
            assignments_text += f"Passengers ({len(riders)}):\n"
            for rider in riders:
                assignments_text += f"  - {rider.get('name', 'Unknown')} ({rider.get('location', 'Unknown')})\n"
        
        subject = f"RideBuddy Assignments: {event_name}"
        body = f"""Your ride assignments for {event_name} are ready:
{assignments_text}

Please share these assignments with your participants.
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())
        
        logger.info(f"Ride assignments sent to {to_email}")
        return True
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending assignments: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error sending assignments: {str(e)}")
        return False

