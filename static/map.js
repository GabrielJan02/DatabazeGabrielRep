const map = L.map('map').setView([-41.28, 174.77], 5); // Nový Zéland – výchozí

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

fetch("/locations")
    .then(res => res.json())
    .then(locations => {
        locations.forEach(loc => {
            // Pozor: tady musíš mít souřadnice, zatím tam dáme dummy, ale opravíme později
            const marker = L.marker([0, 0]).addTo(map).bindPopup(`Načítám data pro ${loc.name}...`);

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
    });


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
