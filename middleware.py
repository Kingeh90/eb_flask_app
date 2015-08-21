#!/usr/bin/env python
__author__ = 'sudipta'
from functools import wraps
from flask import request, jsonify
from werkzeug.exceptions import BadRequest


def validate_json(f):
    """
    just a json checker
    """
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except BadRequest:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        return f(*args, **kw)
    return wrapper
