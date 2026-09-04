from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

# Secret key is required for flash messages and sessions
app.secret_key = "disaster-management-secret-key"


# =========================
# HOME ROUTE
# =========================

@app.route("/")
def home():
    return render_template("dashboard.html")


# =========================
# LOGIN ROUTE
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Temporary login logic
        # Database authentication will be added later

        if email and password:
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Please enter email and password.", "danger")

    return render_template("login.html")


# =========================
# REGISTER ROUTE
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        role = request.form["role"]

        # Temporary registration logic
        # Database storage will be added later

        if name and email and phone and password and role:

            flash("Registration successful! Please login.", "success")

            return redirect(url_for("login"))

        flash("Please fill all required fields.", "danger")

    return render_template("register.html")


# =========================
# DASHBOARD ROUTE
# =========================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# =========================
# DISASTER REPORT ROUTE
# =========================

@app.route("/report-disaster", methods=["GET", "POST"])
def report_disaster():

    if request.method == "POST":

        disaster_type = request.form["type"]
        description = request.form["description"]
        location = request.form["location"]

        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        # Image will be handled later
        image = request.files.get("image")

        # Temporary logic
        # Database storage will be added later

        print("Disaster Type:", disaster_type)
        print("Description:", description)
        print("Location:", location)
        print("Latitude:", latitude)
        print("Longitude:", longitude)

        flash(
            "Disaster report submitted successfully!",
            "success"
        )

        return redirect(url_for("disasters"))

    return render_template("report_disaster.html")


# =========================
# DISASTERS ROUTE
# =========================

@app.route("/disasters")
def disasters():

    # Temporary empty list
    # Later this will come from SQLite

    disasters = []

    return render_template(
        "disasters.html",
        disasters=disasters
    )


# =========================
# LOGOUT ROUTE
# =========================

@app.route("/logout")
def logout():

    # Session logout will be implemented later

    flash("You have been logged out.", "info")

    return redirect(url_for("login"))


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)