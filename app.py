from flask import Flask, render_template, redirect, request, session, url_for
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
cluster = MongoClient(MONGO_URI)
db = cluster['agrilink']
users = db["users"]
bookings = db['bookings']

# Flask setup
app = Flask(__name__)
app.secret_key = 'agrilink_2025_secret'

# -------------------- ROUTES --------------------

# Main Navigation
@app.route('/')
@app.route('/Main')
def home():
    return render_template('MainNavigation.html')

# Login page
@app.route('/Loginpage', methods=['GET', 'POST'])
def loginpage():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.find_one({"User_name": username})
        if user and user.get("Password") == password:
            session['username'] = username
            session['role'] = user.get("Role")
            return redirect(f"/{session['role']}_dashboard")
        return render_template("Loginpage.html", data="Invalid username or password.")
    return render_template("Loginpage.html")

# Registration page
@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        data = {
            "User_name": request.form.get("username"),
            "Password": request.form.get("password"),
            "Role": request.form.get("role"),
            "Work_Type": request.form.get("worktype"),
            "Mobile_Number": request.form.get("mobile_number"),
            "Address": request.form.get("Address"),
            "Village_Name": request.form.get("village_name"),
            "State_Name": request.form.get("state_name"),
            "District_Name": request.form.get("district_name")
        }
        if users.find_one({"User_name": data["User_name"]}):
            return render_template("Registation.html", data="Username already exists.")
        users.insert_one(data)
        return render_template("Loginpage.html", data="Registration successful!")
    return render_template("Registation.html")

# Feedback page
@app.route("/Feedback")
def feedback():
    return render_template("Feedback.html")

# Farmer Dashboard
@app.route("/farmer_dashboard")
def farmer_dashboard():
    if 'username' not in session or session.get('role') != 'farmer':
        return redirect("/Loginpage")
    workers = users.find({"Role": "worker"})
    return render_template("Farmers.html", workers=workers)

# Worker Dashboard
@app.route("/worker_dashboard")
def worker_dashboard():
    if 'username' not in session or session.get('role') != 'worker':
        return redirect("/Loginpage")
    bookings_list = bookings.find({"worker": session['username']})
    return render_template("Workers.html", bookings=bookings_list)

# Book Worker
@app.route("/bookworker")
def book_worker():
    if 'username' not in session or session.get('role') != 'farmer':
        return redirect("/Loginpage")
    worker_id = request.args.get("id")
    worker = users.find_one({"_id": ObjectId(worker_id)})
    farmer = users.find_one({"User_name": session['username']})
    existing_booking = bookings.find_one({"booked_by": farmer["User_name"], "worker": worker["User_name"]})
    workers = users.find({"Role": "worker"})
    if existing_booking:
        return render_template("Farmers.html", data="Request already sent", workers=workers)
    bookings.insert_one({
        "booked_by": farmer["User_name"],
        "worker": worker['User_name'],
        "Address": farmer["Address"],
        "Village_name": farmer["Village_Name"],
        "Mobile_number": farmer['Mobile_Number'],
        "status": "pending"
    })
    return render_template("Farmers.html", data="Request sent successfully", workers=workers)

# Accept Booking
@app.route("/accept")
def accept_worker():
    booking_id = request.args.get("id")
    bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": "accepted"}})
    return redirect("/worker_dashboard")

# Reject Booking
@app.route("/reject")
def reject_worker():
    booking_id = request.args.get("id")
    bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": "rejected"}})
    return redirect("/worker_dashboard")

# My Bookings (Farmer)
@app.route("/mybookings")
def mybookings():
    if 'username' not in session or session.get('role') != 'farmer':
        return redirect("/Loginpage")
    booking_list = bookings.find({"booked_by": session['username']})
    return render_template("bookings.html", bookings=booking_list)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/Loginpage")

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=True, port=5050)