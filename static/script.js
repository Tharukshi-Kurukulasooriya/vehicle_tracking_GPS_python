var map = L.map('mapid').setView([7.8731, 80.7718], 7); // Sri Lanka center

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var vehicleMarkers = {};

function updateVehicleLocations() {
    fetch('/api/vehicles/locations')
        .then(response => response.json())
        .then(data => {
            for (const vehicleId in data) {
                const location = data[vehicleId];
                if (location && location.latitude && location.longitude) {
                    const latLng = [location.latitude, location.longitude];
                    if (vehicleMarkers[vehicleId]) {
                        vehicleMarkers[vehicleId].setLatLng(latLng);
                        vehicleMarkers[vehicleId].bindPopup(`Vehicle ID: ${vehicleId}<br>Latitude: ${location.latitude.toFixed(6)}<br>Longitude: ${location.longitude.toFixed(6)}<br>Speed: ${location.speed} km/h`);
                    } else {
                        const marker = L.marker(latLng).addTo(map);
                        marker.bindPopup(`Vehicle ID: ${vehicleId}<br>Latitude: ${location.latitude.toFixed(6)}<br>Longitude: ${location.longitude.toFixed(6)}<br>Speed: ${location.speed} km/h`);
                        vehicleMarkers[vehicleId] = marker;
                    }
                } else {
                    if (vehicleMarkers[vehicleId]) {
                        map.removeLayer(vehicleMarkers[vehicleId]);
                        delete vehicleMarkers[vehicleId];
                        console.warn(`Invalid location data for vehicle ID: ${vehicleId}`);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error fetching vehicle locations:', error);
        });
}

// Update vehicle locations every 5 seconds (adjust as needed)
setInterval(updateVehicleLocations, 5000);

// Initial load of vehicle locations
updateVehicleLocations();