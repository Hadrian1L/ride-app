import openrouteservice
import opencage
from dotenv import load_dotenv
import os
import logging
from opencage.geocoder import OpenCageGeocode
from openrouteservice.optimization import Vehicle, Job

from flask import Flask, request, render_template, jsonify
from werkzeug.exceptions import BadRequest
from db import create_event, add_participant, get_participants, get_event_by_code, get_event, get_drivers, validate_host, email_rides

# Load environment variables
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

# Validate required environment variables
if not ORS_API_KEY or not OPENCAGE_API_KEY:
    raise ValueError("Missing required environment variables: ORS_API_KEY, OPENCAGE_API_KEY")

app = Flask(__name__)
# Security headers
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/events/create', methods=['POST'])
def create_event_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Validate required fields
        required_fields = ['email', 'event_name', 'location']
        for field in required_fields:
            if not data.get(field) or not isinstance(data.get(field), str):
                return jsonify({'error': f'Missing or invalid field: {field}'}), 400
        
        event_code, host_code = create_event(data)
        return jsonify({'event_code': event_code, 'host_code': host_code}), 201
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        return jsonify({'error': 'Failed to create event'}), 500

#helper intial skill map 
def create_skill_map(drivers, riders):
    driver_labels = set()
    for d in drivers:
        label = d.get("sub_event", "")
        driver_labels.add(label.strip())

    rider_labels = set()
    for r in riders:
        label = r.get("sub_event", "")
        rider_labels.add(label.strip())
    labels = driver_labels.union(rider_labels)
    labels.discard("")
    labels.discard("indifferent")

    sorted_labels = sorted(labels)
    label_to_number = {}
    i = 1
    for label in sorted_labels:
        label_to_number[label] = i
        i += 1
    return label_to_number

#helper for assigning subevents
def skill_assign(label, skill_map):
    if not label or label.lower() == "indifferent":
        return 0
    return skill_map[label]

@app.route('/events/<int:event_id>/assign', methods=['POST'])
def assign_rides_route(event_id):

    event = get_event(event_id)

    drivers = get_drivers(event_id)
    participants = get_participants(event_id)
    riders = [p for p in participants if not p["can_drive"]]

    local_skill_map = create_skill_map(drivers, riders)

    vehicles = []
    
    for i, drv in enumerate(drivers):
        coord = get_coords(drv["location"])
        seats = int(drv["seats"])

        v_skill = skill_assign(drv["sub_event"], local_skill_map)  # 0, 1, 2 …
        v_skills = [v_skill]     

        vehicles.append(
            Vehicle(
                id=i,
                profile='driving-car',
                start=coord,
                capacity=[seats],
                skills=v_skills
            )
        )

    pickups = []
    for j, rid in enumerate(riders):
        coord = get_coords(rid["location"])

        j_skill = skill_assign(rid["sub_event"], local_skill_map)
        j_skills = [] if j_skill is None else [j_skill]

        pickups.append(
            Job(
                id=j,
                location=coord,
                amount=[1],
                skills=j_skills 
            )
        )

    client = openrouteservice.Client(key=ORS_API_KEY)
    solution = client.optimization(
        jobs=pickups,
        vehicles=vehicles
    )
    app.logger.warning("UNASSIGNED: %s", solution.get("unassigned"))
    app.logger.warning("ROUTES RAW: %s", solution["routes"])
    
    driver_map = {i: driver for i, driver in enumerate(drivers)}
    rider_map = {j: rider for j, rider in enumerate(riders)}

    assignments = []

    for route in solution.get("routes", []):
        driver_id = route["vehicle"]
        driver = driver_map.get(driver_id)

        rider_ids = [step["id"] for step in route["steps"] if step["type"] == "job"]
        assigned_riders = [rider_map[rid] for rid in rider_ids]

        assignments.append({
            "driver": {
                "name": driver["name"],
                "location": driver["location"]
            },
            "riders": [
                {
                    "name": rider["name"],
                    "location": rider["location"]
                } for rider in assigned_riders
            ]
        })
    if(event):
        email_rides(event['email'], event['event_name'], assignments)

    return jsonify(assignments), 200

@app.route('/events/assign/<event_code>', methods=['GET'])
def assign_by_code(event_code):
    event = get_event_by_code(event_code)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    return assign_rides_route(event["id"])

def get_event_detail(event_code):
    event = get_event_by_code(event_code)
    if event == None:
        return jsonify({'error': 'Event not found'}), 404
    event_data = {
        'event_name': event['event_name'],
        'description': event.get('description', ''),
        'location': event['location'],
        'sub_events': event['sub_events']
    }

    return jsonify(event_data), 200

@app.route('/events/details/<event_code>')
def event_detail_route(event_code):
    return get_event_detail(event_code)

@app.route('/events/exists/<event_code>')
def check_event_exists(event_code):
    event = get_event_by_code(event_code)
    if event:
        return jsonify({
            'exists': True,
            'event_name': event['event_name']
        }), 200
    return jsonify({'exists': False}), 404
    
@app.route('/events/join/<event_code>', methods=['POST'])
def join_event(event_code):
    try:
        # Validate event code format (alphanumeric only)
        if not event_code or not event_code.isalnum() or len(event_code) > 10:
            return jsonify({'error': 'Invalid event code'}), 400
        
        logger.info(f"Join request for event code: {event_code}")
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Invalid event code'}), 404

        event_id = event["id"]
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        can_drive = data.get('can_drive')
        seats = data.get('seats', 0)
        sub_event = data.get('sub_event', '').strip()

        if not name or len(name) > 100:
            return jsonify({'error': 'Invalid name'}), 400
        if not location or len(location) > 255:
            return jsonify({'error': 'Invalid location'}), 400
        if not isinstance(can_drive, bool):
            return jsonify({'error': 'can_drive must be boolean'}), 400
        if not isinstance(seats, int) or seats < 0 or seats > 10:
            return jsonify({'error': 'seats must be 0-10'}), 400

        add_participant(event_id, name, location, can_drive, seats, sub_event)
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        logger.error(f"Error joining event: {str(e)}")
        return jsonify({'error': 'Failed to join event'}), 500


def get_coords(address):
    if not address:
        raise ValueError("Empty Address")
    
    geocoder = OpenCageGeocode(OPENCAGE_API_KEY)
    cords = geocoder.geocode(address, no_annotations=1, limit=1)

    if not cords:
        raise ValueError(f"Could not geocode: {address}")

    lat = cords[0]['geometry']['lat']
    lon = cords[0]['geometry']['lng']
    return [lon, lat]

def get_distance(origin, destination):
    client = openrouteservice.Client(key=ORS_API_KEY)

    origin_coords = get_coords(origin)
    destination_coords = get_coords(destination)

    route = client.directions(
        coordinates=[origin_coords, destination_coords],
        profile='driving-car',
        format='geojson'
    )

    distance = route['features'][0]['properties']['segments'][0]['distance']
    return distance

@app.route('/events/validate-host', methods=['POST'])
def validate_host_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        event_code = data.get('event_code', '').strip()
        host_code = data.get('host_code', '').strip()
        email = data.get('email', '').strip()

        if not event_code or not host_code or not email:
            return jsonify({'error': 'Missing required fields'}), 400

        event = get_event_by_code(event_code)
        if not event:
            return jsonify({"valid": False}), 404
        
        if event['email'] != email:
            return jsonify({"valid": False}), 403
        
        is_valid = validate_host(event['id'], host_code)
        return jsonify({"valid": is_valid}), 200
    except Exception as e:
        logger.error(f"Error validating host: {str(e)}")
        return jsonify({'error': 'Validation failed'}), 500

@app.route('/api/validate-address')
def validate_address():
    address = request.args.get("location", "").strip()
    if not address:
        return jsonify({"valid": False, "reason": "Empty address"}), 400

    try:
        _ = get_coords(address)
        return jsonify({"valid": True}), 200
    except ValueError:
        return jsonify({"valid": False}), 200
    

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Never use debug=True in production
    app.run(debug=False, host='127.0.0.1', port=5000)
