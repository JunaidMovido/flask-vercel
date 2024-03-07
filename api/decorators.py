from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime

from api.config import Config


# Authentication middleware function
def authenticate_request():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the 'X-Secret-Key' header is present and matches the secret key
            if 'X-Secret-Key' not in request.headers or request.headers['X-Secret-Key'] != Config.AUTH_API_SECRET:
                return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting middleware with TTL (Time-to-Live)
def rate_limit(limit, ttl):
    email_requests = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            email = request.json.get('email')
            now = datetime.now()

            # Reset request count at the start of each day
            if email in email_requests:
                last_request_time = email_requests[email]['last_request_time']
                if (now - last_request_time).days >= 1:
                    email_requests[email] = {'count': 0, 'last_request_time': now}

            # Check request count and update timestamp
            if email in email_requests:
                if email_requests[email]['count'] >= limit:
                    return jsonify({'error': 'Rate limit exceeded for this email'}), 429
                else:
                    email_requests[email]['count'] += 1
                    email_requests[email]['last_request_time'] = now
            else:
                email_requests[email] = {'count': 1, 'last_request_time': now}

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# JSON Assertion middleware function
def json_body_assertion():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the 'X-Secret-Key' header is present and matches the secret key
            if not request.json:
                return jsonify({'error': 'The body does not contain valid JSON'}), 415
            return f(*args, **kwargs)
        return decorated_function
    return decorator

