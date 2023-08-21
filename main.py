import os
import time
import base64
import smtplib
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message sent successfully.')
        return message
    except Exception as e:
        print(f'An error occurred while sending the message: {e}')
        return None

def get_brightness():
    brightness_info = os.popen("/usr/libexec/corebrightnessdiag status-info | grep 'DisplayServicesBrightness '").read()
    brightness_value = float(brightness_info.split(';')[0].split('=')[-1].strip('" '))
    return brightness_value

previous_brightness = get_brightness()

while True:
    current_brightness = get_brightness()

    if current_brightness != previous_brightness:
        # Create the email message
        sender = 'joshua.landsman@gmail.com'  # Replace with your Gmail address
        recipient = 'contact@joshbl.dev'  # Replace with the recipient's email
        subject = 'Brightness Change Alert'
        message_text = f'Brightness has changed from {previous_brightness} to {current_brightness}'

        message = create_message(sender, recipient, subject, message_text)

        if message:
            # Send the email using Gmail API
            creds.refresh(Request())
            service = build('gmail', 'v1', credentials=creds)
            send_message(service, 'me', message)

    previous_brightness = current_brightness
    time.sleep(1)  # Adjust the frequency of checking as needed
    