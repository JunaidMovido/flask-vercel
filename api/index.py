from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from functools import wraps
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
import os


from api.repository import SendAnalysisRequestToUberall
from api.decorators import authenticate_request, rate_limit, json_body_assertion
from api.dtos import WPACheckRequest
from api.logger import logger
from api.sendresult import send_email_with_link
from api.config import Config
from api.service import ProcessWPARequest

app = Flask(__name__)

# Sample route with schema validation, authentication, and rate limiting middleware
@app.route('/wpa-request', methods=['POST'])
@rate_limit(limit=5, ttl=timedelta(days=1))  # Allow 5 requests per day per email
@authenticate_request()
@json_body_assertion()
def CreateWPARequest():
    req_identifier = str(uuid4())
    logger.info(f'Request ID {req_identifier} - Received')
    
    # Parse and validate request data
    try:
        data = request.json  # Assuming JSON data is sent in the request body
        wpa_check_request = WPACheckRequest()
        validated_data = wpa_check_request.load(data)
        validated_data_object = SimpleNamespace(**validated_data)
        logger.info(f'Request ID {req_identifier} - Payload Validated')

    except ValidationError as err:
        logger.error(f'Request ID {req_identifier} - Payload Incorrect {err.normalized_messages()}')
        return jsonify({'error': err.normalized_messages()}), 400
    
    try:
        return ProcessWPARequest(validated_data_object, req_identifier)
    
    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/get-template', methods=['GET'])
def returnTemplateHtml():
    template_name = request.args.get('name')
    if not template_name:
        return jsonify({'error': 'Template name is missing in the request'}), 400

    template_path = os.path.join(Config.WORKING_DIR, '..', 'assets', template_name)
    print(template_path)
    if not os.path.isfile(template_path):
        return jsonify({'error': 'The requested template was not found'}), 404

    try:
        with open(template_path, 'r') as fp:
            email_template = fp.read()
        return email_template

    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Sample route with schema validation, authentication, and rate limiting middleware
@app.route('/webhook/perspective/v1', methods=['POST'])
@rate_limit(limit=5, ttl=timedelta(days=1))  # Allow 5 requests per day per email
@authenticate_request()
@json_body_assertion()
def HandlePerspectiveWebhook():
    pass

@app.route('/', methods=['GET','POST'])
def main():
    return jsonify({'success':True}), 200
