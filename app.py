import openrouteservice
import opencage
from dotenv import load_dotenv
import os
from opencage.geocoder import OpenCageGeocode

from flask import Flask, request, render_template, jsonify
from db import create_event, add_participant, get_participants, get_event_by_code
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
    event_code = create_event(data)
    return jsonify({'event_code': event_code}), 201

@app.route('/events/<int:event_id>/assign', methods=['POST'])
def assign_rides_route(event_id):
    NotImplemented
    
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

    distance = route['features'][0]['properties']['segments'][0]['distance']  # in meters
    return distance

def generate_event_code():
    NotImplemented

def generate_host_code():
    NotImplemented

if __name__ == '__main__':
    app.run(debug=True)
