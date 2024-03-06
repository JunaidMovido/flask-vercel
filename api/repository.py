import requests
from pprint import pprint
from api.config import Config
from api.logger import logger

def SendAnalysisRequestToUberall(company_name, country_code, street_address, zip_code, request_identifier):

    headers = {
        'authority': 'uberall.com',
        'accept': 'application/json',
        'accept-language': 'en-GB,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://movido-media.de',
        'referer': 'https://movido-media.de/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    logger.debug(f'Uberall API keay loaded: {Config.UBERALL_API_KEY}')

    json_data = {
        'public_key': Config.UBERALL_API_KEY,
        'name': company_name,
        'country': country_code,
        'street': street_address,
        'city': '',
        'zip': zip_code,
    }

    logger.info(f'Request ID {request_identifier} - Uberall Payload Prepared')
    logger.debug(f'Request ID {request_identifier} - Uberall Payload Prepared - {json_data}')

    response = requests.post('https://uberall.com/api/search', headers=headers, json=json_data)
    logger.info(f'Request ID {request_identifier} - Sent to uberall')
    logger.info(f'Request ID {request_identifier} - Response from Uberall {response}')
    logger.info(f'Request ID {request_identifier} - Response from Uberall {response.json()}')
    if response.status_code == 200:
        return response.json()
    else:
        return None