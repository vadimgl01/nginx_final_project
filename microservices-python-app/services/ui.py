from flask import Flask, render_template, request, jsonify
import requests
from typing import Dict, Any, List
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Service URLs
SERVICES = {
    "users": "http://127.0.0.1:5000",
    "movies": "http://127.0.0.1:5001",
    "showtimes": "http://127.0.0.1:5002",
    "bookings": "http://127.0.0.1:5003"
}

def get_service_data(service_name: str, endpoint: str = "") -> Dict:
    """Generic function to get data from a service with error handling"""
    try:
        response = requests.get(f"{SERVICES[service_name]}/{endpoint}")
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.RequestException as e:
        app.logger.error(f"Error connecting to {service_name} service: {str(e)}")
        return {"success": False, "error": f"Service unavailable"}

@app.route("/")
def index():
    """Home page showing all services status"""
    services_status = {}
    for name, url in SERVICES.items():
        status = get_service_data(name)
        services_status[name.title()] = status["success"]
    return render_template("index.html", services=services_status)

@app.route("/movies")
def movies():
    """Show all movies"""
    result = get_service_data("movies", "movies")
    if result["success"]:
        return render_template("movies.html", movies=result["data"])
    return render_template("error.html", message="Movie service is currently unavailable")

@app.route("/showtimes")
def showtimes():
    """Show all showtimes"""
    try:
        response = requests.get(f"{SERVICES['showtimes']}/showtimes")
        showtimes_list = response.json()
        return render_template("showtimes.html", showtimes=showtimes_list)
    except requests.RequestException:
        return render_template("error.html", message="Could not fetch showtimes")

@app.route("/bookings/<username>")
def user_bookings(username: str):
    """Show bookings for a specific user"""
    try:
        response = requests.get(f"{SERVICES['bookings']}/bookings/{username}")
        bookings = response.json()
        return render_template("bookings.html", username=username, bookings=bookings)
    except requests.RequestException:
        return render_template("error.html", message=f"Could not fetch bookings for {username}")

@app.route("/users")
def users():
    """Show all users"""
    result = get_service_data("users", "users")
    if result["success"]:
        return render_template("users.html", users=result["data"])
    return render_template("error.html", message="User service is currently unavailable")

def _check_service(url: str) -> bool:
    """Check if a service is running"""
    try:
        requests.get(url)
        return True
    except requests.RequestException:
        return False

@app.template_filter('datetime')
def format_datetime(timestamp):
    """Format timestamp to readable date"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

def main() -> None:
    """Main entry point for the application"""
    app.run(host="0.0.0.0", port=5004, debug=True)

if __name__ == "__main__":
    main() 