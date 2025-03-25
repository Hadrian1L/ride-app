import openrouteservice
from dotenv import load_dotenv
import os

from flask import Flask, request, render_template, jsonify
# from db import create_event, add_participant, get_participants

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/events/create', methods=['POST'])
def create_event_route():
    NotImplemented

@app.route('/events/<int:event_id>/assign', methods=['POST'])
def assign_rides_route(event_id):
    NotImplemented

def get_distance(origin, destination):
    NotImplemented

def generate_event_code():
    NotImplemented

def generate_host_code():
    NotImplemented

if __name__ == '__main__':
    app.run(debug=True)
