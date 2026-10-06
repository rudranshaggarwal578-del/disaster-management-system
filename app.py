from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from analytics.disaster_analysis import (
    get_disaster_data,
    get_summary,
    get_disaster_type_counts,
    get_severity_counts
)

app = Flask(__name__)

# Secret key is required for flash messages and sessions
app.secret_key = "dev-secret-key-change-later"

def role_required(role):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return False

    if session.get("user_role") != role:
        flash("You do not have permission to access this page.", "danger")
        return False
    return True

# HOME ROUTE

@app.route("/")
def home():
    return render_template("dashboard.html")

# LOGIN ROUTE

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password.", "danger")
            return redirect(url_for("login"))

        db = get_db()

        user = db.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        db.close()

        # User doesn't exist
        if user is None:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        # Check password
        if not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        # Create session
        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_role"] = user["role"]

        flash("Login successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")

# REGISTER ROUTE

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip().lower()

        # Validate required fields
        if not name or not email or not password or not role:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("register"))

        # Validate role
        allowed_roles = ["citizen", "volunteer"]

        if role not in allowed_roles:
            flash("Invalid role selected.", "danger")
            return redirect(url_for("register"))

        # Connect to database
        db = get_db()

        # Check whether email already exists
        existing_user = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            db.close()
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("register"))

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert user
        cursor =  db.execute("""
            INSERT INTO users (
                name,
                email,
                phone,
                password,
                role
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            password_hash,
            role
        ))
        user_id = cursor.lastrowid

        if role == "volunteer":
            cursor.execute(""" 
                INSERT INTO volunteers(
                    user_id,
                    skills,
                    availability
                )
                VALUES (?, ?, ?)
            """, (
                user_id,
                "",
                "Available"
            ))

        db.commit()
        db.close()

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

# DASHBOARD ROUTE

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login to access the dashboard.", "warning")
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# DISASTER REPORT ROUTE

@app.route("/report-disaster", methods=["GET", "POST"])
def report_disaster():
    if "user_id" not in session:
        flash("Please login before reporting a disaster.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        # Get form data
        disaster_type = request.form.get("type")
        description = request.form.get("description")
        location = request.form.get("location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        # Basic validation
        if not disaster_type or not location:
            flash("Disaster type and location are required.", "danger")
            return redirect(url_for("report_disaster"))

        # Convert coordinates to numbers
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None

        except ValueError:
            flash("Invalid latitude or longitude.", "danger")
            return redirect(url_for("report_disaster"))

        # Connect to database
        db = get_db()

        # Insert disaster report
        db.execute("""
            INSERT INTO disasters (
                reported_by,
                disaster_type,
                description,
                location,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            disaster_type,
            description,
            location,
            latitude,
            longitude
        ))

        # Save changes
        db.commit()

        # Close database connection
        db.close()

        flash("Disaster report submitted successfully!", "success")

        return redirect(url_for("disasters"))

    return render_template("report_disaster.html")

# DISASTERS ROUTE

@app.route("/disasters")
def disasters():
    db = get_db()

    cursor = db.cursor()

    cursor.execute("""
        SELECT *
        FROM disasters
        ORDER BY created_at DESC
    """)

    disasters = cursor.fetchall()

    db.close()

    return render_template("disasters.html", disasters=disasters)

@app.route("/verify-disasters")
def verify_disasters():

    if not role_required("authority"):
        return redirect(url_for("dashboard"))

    db = get_db()

    disasters = db.execute("""
        SELECT *
        FROM disasters
        WHERE status = 'Reported'
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return render_template(
        "verify_disasters.html",
        disasters=disasters
    )


@app.route("/verify-disaster/<int:disaster_id>", methods=["POST"])
def verify_disaster(disaster_id):

    if not role_required("authority"):
        return redirect(url_for("dashboard"))

    action = request.form.get("action")

    if action not in ["verify", "reject"]:
        flash("Invalid action.", "danger")
        return redirect(url_for("verify_disasters"))

    if action == "verify":
        new_status = "Verified"
        message = "Disaster report verified successfully."

    else:
        new_status = "Rejected"
        message = "Disaster report rejected."

    db = get_db()

    db.execute("""
        UPDATE disasters
        SET status = ?,
            verified_at = CURRENT_TIMESTAMP
        WHERE id = ?
          AND status = 'Reported'
    """, (
        new_status,
        disaster_id
    ))

    db.commit()
    db.close()

    flash(message, "success")

    return redirect(url_for("verify_disasters"))

@app.route("/assign-volunteer")
def assign_volunteer_page():

    if not role_required("authority"):
        return redirect(url_for("dashboard"))

    db = get_db()

    disasters = db.execute("""
        SELECT *
        FROM disasters
        WHERE status = 'Verified'
        ORDER BY created_at DESC
    """).fetchall()

    volunteers = db.execute("""
        SELECT
            v.id,
            u.name,
            u.email
        FROM volunteers v
        JOIN users u
            ON v.user_id = u.id
        WHERE u.role = 'volunteer'
            AND v.availability = 'Available'
    """).fetchall()

    db.close()

    return render_template(
        "assign_volunteer.html",
        disasters=disasters,
        volunteers=volunteers
    )

@app.route(
    "/assign-volunteer/<int:disaster_id>",
    methods=["POST"]
)
def assign_volunteer(disaster_id):

    if not role_required("authority"):
        return redirect(url_for("dashboard"))

    volunteer_id = request.form.get("volunteer_id")

    if not volunteer_id:
        flash("Please select a volunteer.", "danger")
        return redirect(url_for("assign_volunteer_page"))

    db = get_db()

    disaster = db.execute("""
        SELECT id, status
        FROM disasters
        WHERE id = ?
    """, (disaster_id,)).fetchone()

    if disaster is None:
        db.close()
        flash("Disaster not found.", "danger")
        return redirect(url_for("assign_volunteer_page"))

    if disaster["status"] != "Verified":
        db.close()
        flash(
            "Only verified disasters can be assigned.",
            "danger"
        )
        return redirect(url_for("assign_volunteer_page"))

    volunteer = db.execute("""
        SELECT id
        FROM volunteers
        WHERE id = ?
          AND availability = 'Available'
    """, (volunteer_id,)).fetchone()

    if volunteer is None:
        db.close()
        flash("Invalid volunteer selected.", "danger")
        return redirect(url_for("assign_volunteer_page"))

    db.execute("""
        INSERT INTO disaster_assignments (
            disaster_id,
            volunteer_id
        )
        VALUES (?, ?)
    """, (
        disaster_id,
        volunteer_id
    ))

    db.execute("""
        UPDATE disasters
        SET status = 'Assigned'
        WHERE id = ?
    """, (disaster_id,))

    db.commit()
    db.close()

    flash(
        "Volunteer assigned successfully.",
        "success"
    )

    return redirect(url_for("assign_volunteer_page"))

@app.route("/volunteer-dashboard")
def volunteer_dashboard():

    if not role_required("volunteer"):
        return redirect(url_for("dashboard"))

    db = get_db()

    assignments = db.execute("""
        SELECT
            da.id AS assignment_id,
            da.assigned_at,
            da.arrived_at,
            da.completed_at,

            d.id AS disaster_id,
            d.disaster_type,
            d.description,
            d.location,
            d.severity,
            d.status

        FROM disaster_assignments da

        JOIN disasters d
            ON da.disaster_id = d.id

        JOIN volunteers v
            ON da.volunteer_id = v.id

        WHERE v.user_id = ?

        ORDER BY da.assigned_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    db.close()

    return render_template(
        "volunteer_dashboard.html",
        assignments=assignments
    )

@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    df = get_disaster_data(db)

    summary = get_summary(df)

    type_counts = get_disaster_type_counts(df)

    severity_counts = get_severity_counts(df)

    db.close()

    return render_template(
        "analytics.html",
        summary=summary,
        type_counts=type_counts.to_dict("records"),
        severity_counts=severity_counts.to_dict("records")
    )

# LOGOUT ROUTE

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "info")

    return redirect(url_for("login"))

# RUN APPLICATION

if __name__ == "__main__":
    app.run(debug=True)