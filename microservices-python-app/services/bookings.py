from typing import Dict, Any, List
from pathlib import Path
import json
from flask import Flask
from werkzeug.exceptions import NotFound
from services import root_dir, nice_json

app = Flask(__name__)

def load_bookings() -> Dict[str, Dict[str, List[str]]]:
    """Load bookings data from JSON file"""
    bookings_file = root_dir() / "database" / "bookings.json"
    try:
        with open(bookings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.error(f"Bookings database file not found at {bookings_file}")
        return {}
    except json.JSONDecodeError:
        app.logger.error(f"Invalid JSON in bookings database file {bookings_file}")
        return {}

bookings = load_bookings()

@app.route("/", methods=['GET'])
def hello() -> Dict[str, Any]:
    """Root endpoint showing available routes"""
    return {
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<username>"
        }
    }

@app.route("/bookings/<username>", methods=['GET'])
def booking_record(username: str) -> Dict[str, List[str]]:
    """Get bookings for a specific user"""
    if username not in bookings:
        app.logger.warning(f"No bookings found for user {username}")
        raise NotFound(description=f"No bookings found for user {username}")
    return bookings[username]

@app.route("/bookings", methods=['GET'])
def booking_list() -> Dict[str, Dict[str, List[str]]]:
    """Get all bookings"""
    return bookings

def main() -> None:
    """Main entry point for the application"""
    app.run(host="0.0.0.0", port=5003, debug=True)

if __name__ == "__main__":
    main()

