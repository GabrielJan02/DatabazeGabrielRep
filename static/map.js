const map = L.map('map', {
    center: [-41.28, 174.77], // Nový Zéland – výchozí pozice
    zoom: 5,                  // Počáteční úroveň zoomu
    minZoom: 5                // Minimální úroveň zoomu (není možné odzoomovat pod tuto hodnotu)
});

// Původní hranice (jihozápadní a severovýchodní roh)
const southWest = L.latLng(-45.0, 167.0); // Jihozápadní roh mapy
const northEast = L.latLng(-35.0, 178.0); // Severovýchodní roh mapy

// Spočítání šířky a výšky oblasti (rozdíl mezi souřadnicemi)
const latDiff = northEast.lat - southWest.lat;
const lngDiff = northEast.lng - southWest.lng;

// Rozšíření hranic o 50 %
const expandedSouthWest = L.latLng(
    southWest.lat - latDiff * 0.25, // Posunutí o 25% na jih
    southWest.lng - lngDiff * 0.25  // Posunutí o 25% na západ
);

const expandedNorthEast = L.latLng(
    northEast.lat + latDiff * 0.25,  // Posunutí o 25% na sever
    northEast.lng + lngDiff * 0.25   // Posunutí o 25% na východ
);

// Vytvoření nových ohraničení mapy s rozšířením
const bounds = L.latLngBounds(expandedSouthWest, expandedNorthEast);

map.setMaxBounds(bounds);  // Omezí pohyb mapy na rozšířenou oblast

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

fetch("/locations")
    .then(res => res.json())
    .then(locations => {
        locations.forEach(loc => {
            const marker = L.marker([loc.lat, loc.lng]).addTo(map).bindPopup(`Načítám data pro ${loc.name}...`);

            marker.on('click', () => {
                fetch(`/city_stats/${loc.id}`)
                    .then(res => res.json())
                    .then(data => {
                        let content = `
                            <strong style="font-size: 1.5em; font-weight: bold;">${loc.name}</strong><br>
                            <h4>Statistiky:</h4>
                            <p><strong>Průměrný rok modelu: </strong>${data.avg_model_year || "Nedostatek dat"}</p>
                            <p><strong>Populace: </strong>${data.population || "Nedostatek dat"}</p>
                            <h5>5 Nejvíce kradených vozidel:</h5>
                            <ul class="popup-list">`;

                        if (data.vehicles && data.vehicles.length > 0) {
                            data.vehicles.forEach(vehicle => {
                                content += `<li>${vehicle.vehicle_name} - ${vehicle.make_name} (${vehicle.vehicle_type}) - ${vehicle.count}×</li>`;
                            });
                        } else {
                            content += "<li>Nedostatek dat</li>";
                        }

                        content += `</ul>
                            <h5>Nejvíce kradené barvy:</h5>
                            <ul class="popup-list">`;

                        if (data.colors && data.colors.length > 0) {
                            data.colors.forEach(color => {
                                content += `<li>${color.color} - ${color.count}×</li>`;
                            });
                        } else {
                            content += "<li>Nedostatek dat</li>";
                        }

                        content += `</ul>`;

                        marker.setPopupContent(content).openPopup();
                    })
                    .catch(err => {
                        marker.setPopupContent("Chyba při načítání dat.");
                        console.error(err);
                    });
            });
        });
    });
