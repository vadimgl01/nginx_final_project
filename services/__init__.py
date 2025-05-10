from pathlib import Path
import json
from typing import Any
from flask import make_response, Response


def root_dir() -> Path:
    """Returns root directory for this project"""
    return Path(__file__).parent.parent


def nice_json(arg: Any) -> Response:
    """Create a nice JSON response with proper headers"""
    response = make_response(json.dumps(arg, sort_keys=True, indent=4))
    response.headers['Content-Type'] = 'application/json'
    return response