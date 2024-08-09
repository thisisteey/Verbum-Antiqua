#!/usr/bin/python3
"""Module for sending emails via Gmail API"""
import os
import base64
import email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
"""Scopes required for sending emails"""


def get_gmail_credentials():
    """Gets and returns credentials for Gmail API"""
    api_creds = None
    if os.path.exists('token.json'):
        api_creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not api_creds or not api_creds.valid:
        if api_creds and api_creds.expired and api_creds.refresh_token:
            api_creds.refresh(Request())
        else:
            oauth_flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            api_creds = oauth_flow.run_local_server(
                host=os.getenv('HOST', '0.0.0.0'),
                port=5050,
                open_browser=False
            )
        with open('token.json', 'w') as token:
            token.write(api_creds.to_json())
    return api_creds


def create_email_message(recipient, subject, body_html):
    """Constructs a MIME message for email"""
    message = MIMEText(body_html, 'html', 'utf-8')
    message['to'] = recipient
    message['from'] = os.getenv('GMAIL_SENDER')
    message['subject'] = subject
    encoded_message = {'raw': base64.urlsafe_b64encode(
        bytes(message.as_string(), 'utf-8')).decode('utf-8')
    }
    return encoded_message


def send_email(service, message):
    """Sends an email message using Gmail API"""
    try:
        gmail_creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=gmail_creds)
        message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        print(f'Message Id: {message['id']}')
        return message
    except HttpError as error:
        print(f'An error occured: {error}')


def deliver_message(dest, subject, body_html):
    """Deliver message to destination user"""
    try:
        api_creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=api_creds)
        message = create_email_message(dest, subject, body_html)
        send_email(service, message)
    except HttpError as error:
        print(f'An error occurred: {error}')
