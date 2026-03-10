# RideBuddy 🚗

A web application for organizing and optimizing ride-sharing events using route optimization algorithms.

## About This Project

This is my first full-stack project, built to learn how software engineers connect the different layers of an application - from the database, to the backend, to the frontend and user experience.

**What I built this to learn:**
- How the full stack connects end-to-end: database -> backend API -> frontend -> user
- REST API design with Flask (GET/POST routes, request validation, JSON responses)
- Relational database schema design with SQLite
- Integrating third-party APIs (OpenCage geocoding, OpenRouteService optimization)
- Basic auth flows and automated email delivery

**How it works:**
Given a group of drivers with limited seats and riders spread across different addresses, RideBuddy automatically assigns riders to drivers using route optimization to minimize total travel distance. Hosts create an event, participants join with their location and whether they can drive, and the app handles the rest.

It also supports sub-event preference matching - participants can indicate if they'd like to attend a secondary event after the main one, and the optimizer attempts to group riders with drivers heading the same direction. This feature is partially implemented and a candidate for future improvement.

## Features

- **Create Events** - Host can create events with specific dates, locations, and sub-events
- **Join Events** - Participants can join events with a unique event code
- **Driver Registration** - Participants can register as drivers with vehicle capacity
- **Route Optimization** - Automatically matches drivers with riders using OpenRouteService
- **Email Notifications** - Hosts receive event codes and ride assignments via email
- **Geocoding** - Address validation and coordinate lookup with OpenCage

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Routing:** OpenRouteService API
- **Geocoding:** OpenCage API
- **Frontend:** HTML, CSS, JavaScript
- **Email:** SMTP (Gmail)

## Installation

### Prerequisites
- Python 3.8+
- Git

### Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Hadrian1L/ride-app.git
   cd ride-app
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and email credentials
   ```

5. **Initialize database:**
   ```bash
   sqlite3 ridebuddy.db < schema.sql
   ```

6. **Run the app:**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000` in your browser

## Configuration

Required environment variables (see `.env.example`):

```bash
ORS_API_KEY=your_openrouteservice_key
OPENCAGE_API_KEY=your_opencage_key
EMAIL=your-email@gmail.com
APP_PASSWORD=your-16-char-app-password
```

**Get API Keys:**
- OpenRouteService: https://openrouteservice.org/dev/#/signup
- OpenCage: https://opencagedata.com/
- Gmail App Password: https://support.google.com/accounts/answer/185833

## Project Structure

```
ride-app/
├── app.py              # Flask application & routes
├── db.py               # Database functions
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── SECURITY.md         # Security guidelines
├── .env.example        # Environment configuration template
├── .gitignore          # Git ignore rules
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
└── templates/
    └── index.html
```

## API Endpoints

- `POST /events/create` - Create a new event
- `GET /events/exists/<event_code>` - Check if event exists
- `GET /events/details/<event_code>` - Get event details
- `POST /events/join/<event_code>` - Join an event
- `POST /events/validate-host` - Validate host access
- `POST /events/<event_id>/assign` - Assign rides to participants
- `GET /events/assign/<event_code>` - Assign by event code
- `GET /api/validate-address` - Validate address

## Usage

1. **Host creates an event** - Provides event name, location, dates, and contacts
2. **Participants join** - Use event code to join and provide their location
3. **Host triggers assignment** - App optimizes routes and emails assignments
4. **Participants receive trips** - Email contains driver and rider assignments
