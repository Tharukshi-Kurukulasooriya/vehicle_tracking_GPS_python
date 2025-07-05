from flask import Flask, render_template, jsonify
from models import WialonAPI

app = Flask(__name__)

# Replace with your actual Wialon token
WIALON_TOKEN = ""
wialon_api = WialonAPI(WIALON_TOKEN)

@app.route('/')
def index():
    """Renders the main web page with the map."""
    if not wialon_api.sid:
        wialon_api.login()
    return render_template('index.html')

@app.route('/api/vehicles/locations')
def get_vehicle_locations():
    """Returns the latest GPS locations of all vehicles in JSON format."""
    if not wialon_api.sid:
        if not wialon_api.login():
            return jsonify({"error": "Failed to authenticate with Wialon"}), 500
    locations = wialon_api.get_all_vehicle_positions()
    return jsonify(locations)

if __name__ == '__main__':
    app.run(debug=True)

@app.teardown_appcontext
def teardown_wialon(error):
    """Logs out of the Wialon session when the application context ends."""
    if wialon_api.sid:
        wialon_api.logout()