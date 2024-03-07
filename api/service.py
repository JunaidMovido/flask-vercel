from api.repository import SendAnalysisRequestToUberall
from api.config import Config
from api.logger import logger
from flask import Flask, jsonify
from urllib.parse import urljoin, urlencode
from api.sendresult import send_email_with_link


def ProcessWPARequest(validated_data_object, req_identifier):
    # Call external API with the validated data
    try:
        response_from_external_api = SendAnalysisRequestToUberall(
            company_name=validated_data_object.company,
            country_code=validated_data_object.country,
            street_address = validated_data_object.street,
            zip_code = validated_data_object.zip,
            request_identifier=req_identifier)
        
        logger.debug(f'Received response from api - {response_from_external_api}')
    
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
