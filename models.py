import requests
import json

class WialonAPI:
    def __init__(self, token):
        self.token = token
        self.sid = None
        self.api_url = "https://hst-api.wialon.com/wialon/ajax.html"

    def login(self):
        """Authenticates with Wialon and gets a session ID."""
        params = {"svc": "token/login", "params": json.dumps({"token": self.token})}
        try:
            response = requests.post(self.api_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            if data and 'eid' in data:
                self.sid = data['eid']
                return self.sid
            else:
                print(f"Login failed: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Login request failed: {e}")
            return None

    def get_unit_ids(self):
        """Retrieves a list of all AVL unit IDs."""
        if not self.sid:
            print("Session ID is not available. Please log in first.")
            return None

        params = {
            "svc": "core/search_items",
            "params": json.dumps({
                "spec": {"itemsType": "avl_unit", "propName": "sys_name", "propValueMask": "*", "sortType": "sys_name"},
                "force": 1,
                "flags": 1,
                "from": 0,
                "to": 0
            }),
            "sid": self.sid
        }
        try:
            response = requests.post(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and 'items' in data:
                return [item['id'] for item in data['items']]
            else:
                print(f"Failed to get unit IDs: {data}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching unit IDs: {e}")
            return []

    def get_device_position(self, unit_id):
        """Retrieves the latest position data for a specific unit ID."""
        if not self.sid:
            print("Session ID is not available. Please log in first.")
            return None

        params = {
            "svc": "core/search_item",
            "params": json.dumps({"id": unit_id, "flags": 4194304}),
            "sid": self.sid
        }
        try:
            response = requests.post(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and 'item' in data and 'pos' in data['item']:
                position = data['item']['pos']
                return {'latitude': position['y'], 'longitude': position['x'], 'speed': position.get('s', 0), 'timestamp': position['t']}
            else:
                print(f"Could not retrieve position for unit ID {unit_id}: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching position for unit ID {unit_id}: {e}")
            return None

    def get_all_vehicle_positions(self):
        """Retrieves the latest positions for all vehicles."""
        unit_ids = self.get_unit_ids()
        if unit_ids:
            all_positions = {}
            for unit_id in unit_ids:
                position = self.get_device_position(unit_id)
                if position:
                    # You might want to fetch the vehicle name as well and include it here
                    all_positions[unit_id] = position
            return all_positions
        return {}

    def logout(self):
        """Logs out of the Wialon session."""
        if self.sid:
            params = {"svc": "core/logout", "params": "{}", "sid": self.sid}
            try:
                response = requests.post(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()
                if data and data.get('result') == 1:
                    print("Logged out successfully.")
                    self.sid = None
                    return True
                else:
                    print(f"Logout failed: {data}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"Logout request failed: {e}")
                return False
        else:
            print("No active session to logout from.")
            return True