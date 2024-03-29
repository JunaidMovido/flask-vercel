from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid import SendGridAPIClient
from flask import jsonify
from api.config import Config
from api.logger import logger
import ssl
import css_inline
from os.path import join

ssl._create_default_https_context = ssl._create_unverified_context

# Function to send email with link to analysis
def send_email_with_link(recipient_email, analyse_link, language, request_identifier):

    logger.info(f'Request ID {request_identifier} - Command received to generate SendGrid payload')

    sg = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
    
    with open(join(Config.WORKING_DIR, '..', 'assets', 'aadvanto.html'), 'r') as fp:    
        email_template = (fp.read())    

    # Substitute values into the template
    content = email_template.replace('{wpa_url}',analyse_link)
    content = css_inline.inline(content)

    logger.debug('FORMATTED EMAIL IS READY')
    logger.debug(content)

    message = Mail(
        from_email=Config.SENDER_EMAIL_WPA,
        to_emails=recipient_email,
        subject=f"Your Download is ready {request_identifier}",
        html_content=content)

    response = sg.send(message)

    logger.debug(f'Request ID {request_identifier} - SendGrid payload')
    logger.debug(f'Request ID {request_identifier} - {response}')

    if response.status_code == 202:
        return True
    else:
        return False