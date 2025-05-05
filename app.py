# app.py
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
    cursor.execute("""
        SELECT location_id, region
        FROM location_id
    """)
    rows = cursor.fetchall()
    result = [
        {"id": row.location_id, "name": row.region}
        for row in rows
    ]
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


    except Exception as e:
        print(f"❌ Chyba při získávání dat pro location_id={location_id}: {e}")
        return jsonify({"error": "Data se nepodařilo načíst"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
