import openrouteservice
import opencage
from dotenv import load_dotenv
import os
from opencage.geocoder import OpenCageGeocode

from flask import Flask, request, render_template, jsonify
from db import create_event, add_participant, get_participants, get_event_by_code, get_event, get_drivers
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/events/create', methods=['POST'])
def create_event_route():
    data = request.get_json()
    event_code, host_code = create_event(data)
    
    return jsonify({'event_code': event_code, 'host_code': host_code}), 201

@app.route('/events/<int:event_id>/assign', methods=['POST'])
def assign_rides_route(event_id):

    event = get_event_by_code(event_id)

    drivers = get_drivers(event_id)
    participants = get_participants(event_id)
    riders = [p for p in participants if not p["can_drive"]]

    vehicles = []
    for i, driver in enumerate(drivers):
        coord = get_coords(driver["location"])
        vehicles.append({
            "id": i,
            "start": coord,
            "capacity": [driver["seats"]],
        })

    pickups = []
    for j, rider in enumerate(riders):
        coord = get_coords(rider["location"])
        pickups.append({
            "id": j,
            "location": coord,
            "amount": [1]
    })
    client = openrouteservice.Client(key=ORS_API_KEY)
    solution = client.optimization(
        jobs=pickups,
        vehicles=vehicles
    )
    
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

    return jsonify(assignments), 200

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
    event = get_event_by_code(event_code)
    if not event:
        return jsonify({'error': 'Invalid event code'}), 404

    event_id = event["id"]
    data = request.get_json()
    name = data.get('name')
    location = data.get("location")
    can_drive = data.get("can_drive")
    seats = data.get("seats", 0)
    sub_event = data.get("sub_event")

    add_participant(event_id, name, location, can_drive, seats, sub_event)
    return jsonify({'status': 'success'}), 200


def get_coords(address):
    geocoder = OpenCageGeocode(OPENCAGE_API_KEY)
    cords = geocoder.geocode(address)
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

if __name__ == '__main__':
    app.run(debug=True)
