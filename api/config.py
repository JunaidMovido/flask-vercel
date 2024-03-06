import os
from dotenv import load_dotenv
import certifi

load_dotenv()  # Default to .env file in the project root

class Config:
    load_dotenv()  # Default to .env file in the project root

    UBERALL_API_KEY = os.getenv("UBERALL_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY2")
    FLASK_ENVIRONMENT = os.getenv("FLASK_ENV")
    SENDER_EMAIL_WPA = os.getenv("SENDER_EMAIL_WPA")
    TLS_CA_FILE = None if FLASK_ENVIRONMENT == 'development' else certifi.where()
    ALLOWED_ORIGINS = [
        'https://localhost:300',
        'https://localhost:300'
    ]
    WEBSITE_WPA_BASE_URL = os.getenv("WEBSITE_WPA_BASE_URL")

    # Add other configuration variables as needed
