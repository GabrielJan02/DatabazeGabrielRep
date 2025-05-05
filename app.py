from flask import Flask, render_template, jsonify
import pyodbc
from config import DB_CONFIG

app = Flask(__name__)

@app.route("/test-db")
def test_db_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM Vozidla")  # Změň podle své tabulky
        row = cursor.fetchone()
        conn.close()

        if row:
            return jsonify({"status": "success", "sample_row": str(row)})
        else:
            return jsonify({"status": "success", "message": "No data found."})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


@app.route('/city_stats/<int:location_id>')
def get_city_stats(location_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Získání základních statistických údajů pro město
    cursor.execute("""
        SELECT
            l.population,
            AVG(c.model_year) AS avg_model_year
        FROM CarsStolenNZ c
        JOIN location_id l ON c.location_id = l.location_id
        WHERE c.location_id = ?
        GROUP BY l.population
    """, (location_id,))

    city_data = cursor.fetchone()

    if not city_data:
        return jsonify({
            "avg_model_year": None,
            "population": None,
            "vehicles": [],
            "colors": []
        })

    avg_model_year = city_data[1]
    population = city_data[0]

    # Získání top 5 nejvíce kradených vozidel
    cursor.execute("""
        SELECT TOP 5
            c.vehicle_desc AS vehicle_name,
            m.make_name,
            c.vehicle_type,
            COUNT(*) AS vehicle_count
        FROM CarsStolenNZ c
        JOIN make_ID m ON c.make_id = m.make_id
        WHERE c.location_id = ?
        GROUP BY c.vehicle_desc, m.make_name, c.vehicle_type
        ORDER BY vehicle_count DESC
    """, (location_id,))

    vehicles = cursor.fetchall()

    # Získání top 5 nejvíce kradených barev
    cursor.execute("""
        SELECT TOP 5
            c.color,
            COUNT(*) AS color_count
        FROM CarsStolenNZ c
        WHERE c.location_id = ?
        GROUP BY c.color
        ORDER BY color_count DESC
    """, (location_id,))

    colors = cursor.fetchall()

    return jsonify({
        "avg_model_year": avg_model_year,
        "population": population,
        "vehicles": [{"vehicle_name": row[0], "make_name": row[1], "vehicle_type": row[2], "count": row[3]} for row in vehicles],
        "colors": [{"color": row[0], "count": row[1]} for row in colors]
    })


def get_connection():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server=tcp:{DB_CONFIG['server']},1433;"
        f"Database={DB_CONFIG['database']};"
        f"Uid={DB_CONFIG['username']};"
        f"Pwd={DB_CONFIG['password']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/locations')
def get_locations():
    conn = get_connection()
    cursor = conn.cursor()

    # Seznam ID a souřadnic, můžeš je později přesunout do tabulky v DB
    coordinates = {
        101: (-35.4136, 173.9321),
        102: (-36.8485, 174.7633),
        103: (-37.6191, 175.0233),
        104: (-37.4234, 176.7416),
        105: (-38.6533, 178.0042),
        106: (-39.6017, 176.5804),
        107: (-39.3538, 174.4383),
        108: (-39.7273, 175.4376),
        109: (-41.2865, 174.7762),
        110: (-41.4571, 172.8210),
        111: (-41.2706, 173.2840),
        112: (-41.5917, 173.7624),
        113: (-42.4064, 171.6912),
        114: (-43.7542, 171.1637),
        115: (-45.4791, 170.1548),
        116: (-45.8489, 167.6755),
        117: (-45.0000, 170.0000),
    }

    cursor.execute("SELECT location_id, region FROM location_id")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        loc_id = row.location_id
        lat, lng = coordinates.get(loc_id, (0, 0))  # fallback [0,0] pokud chybí
        result.append({
            "id": loc_id,
            "name": row.region,
            "lat": lat,
            "lng": lng
        })

    conn.close()
    return jsonify(result)


@app.route('/data/<int:region_id>')
def get_top_vehicles(region_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 5 m.make_name, COUNT(*) AS pocet
        FROM CarsStolenNZ c
        JOIN location_id l ON c.location_id = l.location_id
        JOIN make_ID m ON c.make_id = m.make_id
        WHERE l.location_id = ?
        GROUP BY m.make_name
        ORDER BY pocet DESC;
    """, region_id)

    rows = cursor.fetchall()
    result = [
        {"znacka": row.make_name, "pocet": row.pocet}
        for row in rows
    ]
    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
