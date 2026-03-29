from flask import Flask, render_template, request, redirect
import os
import psycopg2
import qrcode

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- DB CONNECTION ----------------
def get_db_connection():
    conn = psycopg2.connect(
        "postgresql://student_db_w7uj_user:LYpcNBZuQPSVDFh8JWQpZVWouhKtfJ9E@dpg-d72qfi75r7bs73bo7bgg-a.oregon-postgres.render.com/student_db_w7uj"
    )
    return conn


# ---------------- CREATE TABLE ----------------
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name TEXT,
        student_id TEXT UNIQUE,
        level TEXT,
        vehicle TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


create_table()


# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("register.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    student_id = request.form["student_id"]
    level = request.form["level"]
    vehicle = request.form["vehicle"]

    photo = request.files["photo"]

    # Save image
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], photo.filename)
    photo.save(filepath)

    # Save to DB
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO students (name, student_id, level, vehicle, photo) VALUES (%s, %s, %s, %s, %s)",
        (name, student_id, level, vehicle, photo.filename)
    )

    conn.commit()
    cur.close()
    conn.close()

    # Create QR
    qr_data = f"https://student-qr-system.onrender.com/student/{student_id}"
    qr = qrcode.make(qr_data)

    qr_filename = f"{student_id}_qr.png"
    qr_path = os.path.join("static", qr_filename)
    qr.save(qr_path)

    return f"""
    <h2>Registration Successful</h2>
    Name: {name} <br>
    ID: {student_id} <br>
    Level: {level} <br>
    Vehicle: {vehicle} <br><br>

    <img src="/static/uploads/{photo.filename}" width="200"><br><br>

    <h3>QR Code:</h3>
    <img src="/static/{qr_filename}" width="200">
    """


# ---------------- STUDENT PROFILE ----------------
@app.route("/student/<student_id>")
def student_profile(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cur.fetchone()

    cur.close()
    conn.close()

    if student:
        return f"""
        <h2>Student Profile</h2>
        Name: {student[1]} <br>
        ID: {student[2]} <br>
        Level: {student[3]} <br>
        Vehicle: {student[4]} <br><br>

        <img src="/static/uploads/{student[5]}" width="200">
        """
    else:
        return "Student not found"


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
