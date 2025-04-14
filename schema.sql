CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    can_drive BOOLEAN NOT NULL,
    seats INTEGER DEFAULT 0,
    sub_event TEXT,
    FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    event_name TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    sub_events TEXT,
    host_code TEXT NOT NULL,
    event_code TEXT UNIQUE NOT NULL
);
