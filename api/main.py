from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from functools import wraps
from datetime import datetime, timedelta
from repository import SendAnalysisRequestToUberall
from types import SimpleNamespace
from uuid import uuid4
from logger import logger
from sendresult import send_email_with_link
from config import Config
from urllib.parse import urljoin, urlencode
from pprint import pprint

app = Flask(__name__)

# Define a Marshmallow schema for request validation
class WPACheckRequest(Schema):
    company = fields.Str(required=True)
    country = fields.Str(required=True, validate=validate.OneOf(['DE', 'AT', 'CH']))
    street = fields.Str(required=True)
    zip = fields.Str(required=True)
    email = fields.Email(required=True)

# Authentication middleware function
def authenticate_request():
    secret_key = 'my_secret_key'  # Replace with your actual secret key
    
    # Check if the 'X-Secret-Key' header is present and matches the secret key
    if 'X-Secret-Key' not in request.headers or request.headers['X-Secret-Key'] != secret_key:
        return False
    return True

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

# Sample route with schema validation, authentication, and rate limiting middleware
@app.route('/wpa-request', methods=['POST'])
@rate_limit(limit=5, ttl=timedelta(days=1))  # Allow 5 requests per day per email

def CreateWPARequest():
    req_identifier = str(uuid4())
    logger.info(f'Request ID {req_identifier} - Received')
    
    # Authenticate the request
    if not authenticate_request():
        logger.error(f'Request ID {req_identifier} - Not Authenticated')
        return jsonify({'error': 'Unauthorized'}), 401
    
    logger.debug(f'Request ID {req_identifier} - Authenticated')

    # Parse and validate request data
    try:
        data = request.json  # Assuming JSON data is sent in the request body
        wpa_check_request = WPACheckRequest()
        validated_data = wpa_check_request.load(data)
        validated_data_object = SimpleNamespace(**validated_data)
        logger.debug(f'Request ID {req_identifier} - Payload Validated')

    except ValidationError as err:
        logger.error(f'Request ID {req_identifier} - Payload Incorrect {err.normalized_messages()}')
        return jsonify({'error': err.normalized_messages()}), 400
    
    # Call external API with the validated data
    try:
        response_from_external_api = SendAnalysisRequestToUberall(
            company_name=validated_data_object.company,
            country_code=validated_data_object.country,
            street_address = validated_data_object.street,
            zip_code = validated_data_object.zip,
            request_identifier=req_identifier)
        
        pprint(response_from_external_api)
    
        if response_from_external_api is None:
            return jsonify({'error': 'There was a problem processing your request'}), 500
        
    except Exception as err:
        return jsonify({'error': f'{err}'}), 400
    
    # Construct the base URL
    base_url = Config.WEBSITE_WPA_BASE_URL

    # Construct the query parameters dictionary
    query_params = {
        'ubrecheckid': response_from_external_api['response']['searchData']['id'],
        'ubrechecktoken': response_from_external_api['response']['searchData']['token']
    }

    # Encode the query parameters
    encoded_query_params = urlencode(query_params)

    # Concatenate the base URL and encoded query parameters
    analyse_link = urljoin(base_url, '?' + encoded_query_params)
    
    # Send email with required data
    try:
        response_from_email_sender = send_email_with_link(
            validated_data_object.email,
            analyse_link,
            'en',
            req_identifier)
    
        if response_from_email_sender is None:
            return jsonify({'error': 'There was a problem in sending the email'}), 500
        
    except Exception as err:
        return jsonify({'error': f'{err}'}), 400

    return jsonify({'success': True}), 200

@app.route('/', methods=['GET','POST'])
def main():
    return jsonify({'success':True}), 200