# app.py
from flask import Flask, render_template, jsonify
import pyodbc
from config import DB_CONFIG

app = Flask(__name__)

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

@app.route('/data/<int:location_id>')
def get_top_vehicles(location_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT TOP 5 M.make_name, C.vehicle_type, COUNT(*) AS count
        FROM CarsStolenNZ C
        JOIN make_ID M ON C.make_id = M.make_id
        WHERE C.location_id = ?
        GROUP BY M.make_name, C.vehicle_type
        ORDER BY count DESC;
        """
        cursor.execute(query, location_id)
        results = cursor.fetchall()

        data = [
            {"make": row[0], "type": row[1], "count": row[2]}
            for row in results
        ]
        conn.close()
        return jsonify(data)

    except Exception as e:
        print(f"❌ Chyba při získávání dat pro location_id={location_id}: {e}")
        return jsonify({"error": "Data se nepodařilo načíst"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
