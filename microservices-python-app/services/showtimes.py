from typing import Dict, Any, List
from pathlib import Path
import json
from flask import Flask
from werkzeug.exceptions import NotFound
from services import root_dir, nice_json

app = Flask(__name__)

def load_showtimes() -> Dict[str, List[str]]:
    """Load showtimes data from JSON file"""
    showtimes_file = root_dir() / "database" / "showtimes.json"
    try:
        with open(showtimes_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.error(f"Showtimes database file not found at {showtimes_file}")
        return {}
    except json.JSONDecodeError:
        app.logger.error(f"Invalid JSON in showtimes database file {showtimes_file}")
        return {}

showtimes = load_showtimes()

@app.route("/", methods=['GET'])
def hello() -> Dict[str, Any]:
    """Root endpoint showing available routes"""
    return {
        "uri": "/",
        "subresource_uris": {
            "showtimes": "/showtimes",
            "showtime": "/showtimes/<date>"
        }
    }

@app.route("/showtimes/<date>", methods=['GET'])
def showtimes_by_date(date: str) -> List[str]:
    """Get movie IDs for shows on a specific date"""
    if date not in showtimes:
        app.logger.warning(f"No showtimes found for date {date}")
        raise NotFound(description=f"No showtimes found for date {date}")
    return showtimes[date]

@app.route("/showtimes", methods=['GET'])
def showtimes_list() -> Dict[str, List[str]]:
    """Get all showtimes"""
    return showtimes

def main() -> None:
    """Main entry point for the application"""
    app.run(host="0.0.0.0", port=5002, debug=True)

if __name__ == "__main__":
    main()
