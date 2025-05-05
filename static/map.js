const map = L.map('map').setView([-41.28, 174.77], 5); // Nový Zéland – výchozí

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

// Lokace podle ID regionu z databáze
const locations = [
    { id: 1, name: "Auckland", lat: -36.8485, lng: 174.7633 },
    { id: 2, name: "Wellington", lat: -41.2865, lng: 174.7762 },
    { id: 3, name: "Christchurch", lat: -43.5321, lng: 172.6362 }
];

locations.forEach(loc => {
    const marker = L.marker([loc.lat, loc.lng]).addTo(map).bindPopup(`Načítám data pro ${loc.name}...`);

    marker.on('click', () => {
        fetch(`/data/${loc.id}`)
            .then(res => res.json())
            .then(data => {
                if (data.length === 0) {
                    marker.setPopupContent(`<strong>${loc.name}</strong><br>Žádná data o krádežích.`);
                } else {
                    let content = `<strong>${loc.name}</strong><br><ul class="popup-list">`;
                    data.forEach(row => {
                        content += `<li>${row.znacka}: ${row.pocet}×</li>`;
                    });
                    content += '</ul>';
                    marker.setPopupContent(content).openPopup();
                }
            })
            .catch(err => {
                marker.setPopupContent("Chyba při načítání dat.");
                console.error(err);
            });
    });
});
