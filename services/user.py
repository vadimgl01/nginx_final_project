from typing import Dict, Any, List
from pathlib import Path
import json
import requests
from flask import Flask
from werkzeug.exceptions import NotFound, ServiceUnavailable
from services import root_dir, nice_json


app = Flask(__name__)

def load_users() -> Dict[str, Dict[str, Any]]:
    """Load users data from JSON file"""
    users_file = root_dir() / "database" / "users.json"
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.error(f"Users database file not found at {users_file}")
        return {}
    except json.JSONDecodeError:
        app.logger.error(f"Invalid JSON in users database file {users_file}")
        return {}

users = load_users()

def get_user_movies(user_id: str) -> List[Dict[str, Any]]:
    """Get all movies seen by a user"""
    try:
        # Get user bookings
        bookings_resp = requests.get(f"http://127.0.0.1:5003/bookings/{user_id}")
        bookings_resp.raise_for_status()
        movies_by_date = bookings_resp.json()

        # Get all unique movie IDs
        movie_ids = {movie_id 
                    for dates in movies_by_date.values() 
                    for movie_id in dates}

        # Get movie details for each movie
        movies = []
        for movie_id in movie_ids:
            movie_resp = requests.get(f"http://127.0.0.1:5001/movies/{movie_id}")
            movie_resp.raise_for_status()
            movies.append(movie_resp.json())

        return movies

    except requests.RequestException as e:
        app.logger.error(f"Error fetching movie data: {str(e)}")
        return []

@app.route("/", methods=['GET'])
def hello() -> Dict[str, Any]:
    """Root endpoint showing available routes"""
    return {
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    }


@app.route("/users", methods=['GET'])
def users_list() -> Dict[str, Dict[str, Any]]:
    """Get all users"""
    return users


@app.route("/users/<username>", methods=['GET'])
def user_record(username: str) -> Dict[str, Any]:
    """Get user details"""
    if username not in users:
        app.logger.warning(f"User {username} not found")
        raise NotFound(description=f"User {username} not found")
    return users[username]


@app.route("/users/<username>/bookings", methods=['GET'])
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    if username not in users:
        raise NotFound("User '{}' not found.".format(username))

    try:
        users_bookings = requests.get("http://127.0.0.1:5003/bookings/{}".format(username))
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Bookings service is unavailable.")

    if users_bookings.status_code == 404:
        raise NotFound("No bookings were found for {}".format(username))

    users_bookings = users_bookings.json()

    # For each booking, get the rating and the movie title
    result = {}
    for date, movies in users_bookings.items():
        result[date] = []
        for movieid in movies:
            try:
                movies_resp = requests.get("http://127.0.0.1:5001/movies/{}".format(movieid))
            except requests.exceptions.ConnectionError:
                raise ServiceUnavailable("The Movie service is unavailable.")
            movies_resp = movies_resp.json()
            result[date].append({
                "title": movies_resp["title"],
                "rating": movies_resp["rating"],
                "uri": movies_resp["uri"]
            })

    return nice_json(result)


@app.route("/users/<username>/suggested", methods=['GET'])
def user_suggested(username: str) -> Dict[str, Any]:
    """Get movie suggestions for a user"""
    if username not in users:
        app.logger.warning(f"User {username} not found")
        raise NotFound(description=f"User {username} not found")

    # Get movies the user has watched
    seen_movies = get_user_movies(username)
    
    # Get all movies
    try:
        movies_resp = requests.get("http://127.0.0.1:5001/movies")
        movies_resp.raise_for_status()
        movies = movies_resp.json()
    except requests.RequestException as e:
        app.logger.error(f"Error fetching movies: {str(e)}")
        return {"suggested_movies": []}

    # Find movies the user hasn't seen with rating >= 8.0
    seen_movie_ids = {movie["id"] for movie in seen_movies}
    suggestions = [
        movie for movie_id, movie in movies.items()
        if movie_id not in seen_movie_ids and movie.get("rating", 0) >= 8.0
    ]

    return {"suggested_movies": suggestions}


def main() -> None:
    """Main entry point for the application"""
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
