const map = L.map('map').setView([-41.28, 174.77], 5); // Nový Zéland – výchozí

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

const locations = [
    { id: 1, name: "Auckland", lat: -36.8485, lng: 174.7633 },
    { id: 2, name: "Wellington", lat: -41.2865, lng: 174.7762 },
    { id: 3, name: "Christchurch", lat: -43.5321, lng: 172.6362 }
];

locations.forEach(region => {
    const marker = L.marker([region.lat, region.lng])
        .addTo(map)
        .bindPopup(`Načítám data pro ${region.name}...`);

    marker.on('click', () => {
        fetch(`/data/${region.id}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    marker.setPopupContent(`<strong>${region.name}</strong><br>Chyba: ${data.error}`).openPopup();
                } else if (data.length === 0) {
                    marker.setPopupContent(`<strong>${region.name}</strong><br>Žádná data o krádežích.`).openPopup();
                } else {
                    let content = `<strong>${region.name}</strong><br><ul>`;
                    data.forEach((item) => {
                        content += `<li>${item.make} (${item.type}): ${item.count}×</li>`;
                    });
                    content += `</ul>`;
                    marker.setPopupContent(content).openPopup();
                }
            })
            .catch((error) => {
                marker.setPopupContent(`<strong>${region.name}</strong><br>Chyba při načítání dat.`).openPopup();
                console.error(error);
            });
    });
});
