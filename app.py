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

@app.route("/data/<int:region_id>")
def get_top_vehicles(region_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Upravený SQL dotaz – přizpůsob tabulce!
        cursor.execute("""
            SELECT TOP 5 Znacka, COUNT(*) as Pocet
            FROM Vozidla
            WHERE RegionID = ?
            GROUP BY Znacka
            ORDER BY Pocet DESC
        """, region_id)

        rows = cursor.fetchall()
        conn.close()

        result = [{"znacka": row[0], "pocet": row[1]} for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    except Exception as e:
        print(f"❌ Chyba při získávání dat pro location_id={location_id}: {e}")
        return jsonify({"error": "Data se nepodařilo načíst"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
