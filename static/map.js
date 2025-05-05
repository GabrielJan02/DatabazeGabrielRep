const map = L.map('map').setView([-41.28, 174.77], 5); // Nový Zéland – výchozí

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
                        const imageUrl = data.image_url || ""; // Ošetření, pokud obrázek není dostupný
                        let content = `
                            <strong style="font-size: 1.5em; font-weight: bold;">${loc.name}</strong><br>
                            <img src="${imageUrl}" alt="Fotografie ${loc.name}" width="200" /><br>
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
