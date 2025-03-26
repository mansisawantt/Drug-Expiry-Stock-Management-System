from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine_stock")
    medicines = cursor.fetchall()
    conn.close()
    return render_template("index.html", medicines=medicines)

if __name__ == "__main__":
    app.run(debug=True)
