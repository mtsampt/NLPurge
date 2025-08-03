#!/usr/bin/env python3
"""
Gmail Export Script for Email Sorter NLP Training Tool

This script helps export emails from Gmail folders (Spam, Promotions, Inbox)
and saves them as CSV files for use with the email sorting web app.

Requirements:
- Python 3.6+
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

Install dependencies:
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import csv
import base64
import email
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email separator for easy parsing
EMAIL_SEPARATOR = "===EMAIL_START==="
EMAIL_END_SEPARATOR = "===EMAIL_END==="

def authenticate_gmail():
    """Authenticate with Gmail API."""
    creds = None
    
    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def clean_text(text):
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    text = text.strip()
    
    return text

def get_email_content(service, message_id):
    """Extract email content from Gmail message."""
    try:
        message = service.users().messages().get(
            userId='me', id=message_id, format='full').execute()
        
        # Extract headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Clean headers
        subject = clean_text(subject)
        sender = clean_text(sender)
        date = clean_text(date)
        
        # Extract body
        body = extract_body(message['payload'])
        body = clean_text(body)
        
        return {
            'subject': subject,
            'sender': sender,
            'body': body,
            'date': date
        }
    except Exception as e:
        print(f"Error extracting email {message_id}: {e}")
        return None

def extract_body(payload):
    """Recursively extract email body from payload."""
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(
            payload['body']['data']).decode('utf-8', errors='ignore')
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if part['body'].get('data'):
                    return base64.urlsafe_b64decode(
                        part['body']['data']).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                if part['body'].get('data'):
                    return base64.urlsafe_b64decode(
                        part['body']['data']).decode('utf-8', errors='ignore')
    
    return 'No content available'

def search_emails(service, query, max_results=100):
    """Search for emails using Gmail query syntax."""
    try:
        results = service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        return results.get('messages', [])
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def export_folder_emails(service, folder_name, query, max_results, output_file):
    """Export emails from a specific folder."""
    print(f"Exporting {max_results} emails from {folder_name}...")
    
    messages = search_emails(service, query, max_results)
    
    if not messages:
        print(f"No emails found in {folder_name}")
        return
    
    emails = []
    for i, message in enumerate(messages):
        print(f"Processing email {i+1}/{len(messages)}")
        email_data = get_email_content(service, message['id'])
        if email_data:
            emails.append(email_data)
    
    # Save to CSV with simple format
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['subject', 'sender', 'body', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        
        for email in emails:
            writer.writerow({
                'subject': email['subject'],
                'sender': email['sender'],
                'body': email['body'],
                'date': email['date']
            })
    
    print(f"Exported {len(emails)} emails to {output_file}")

def main():
    """Main function to export emails from different Gmail folders."""
    print("Gmail Export Script for Email Sorter")
    print("=" * 40)
    
    # Authenticate
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nMake sure you have:")
        print("1. Created a Google Cloud Project")
        print("2. Enabled Gmail API")
        print("3. Downloaded credentials.json")
        return
    
    # Define folder exports with correct counts
    exports = [
        {
            'name': 'Spam',
            'query': 'in:spam',
            'max_results': 209,  # 209 spam emails
            'output_file': 'spam_emails.csv'
        },
        {
            'name': 'Promotions',
            'query': 'category:promotions',
            'max_results': 300,  # 300 most recent promotions
            'output_file': 'promotions_emails.csv'
        },
        {
            'name': 'Inbox',
            'query': 'in:inbox',
            'max_results': 500,  # 500 most recent inbox emails
            'output_file': 'inbox_emails.csv'
        }
    ]
    
    # Export each folder
    for export in exports:
        print(f"\n📧 Exporting {export['name']} folder...")
        export_folder_emails(
            service,
            export['name'],
            export['query'],
            export['max_results'],
            export['output_file']
        )
    
    print("\n✅ Export complete!")
    print("\nNext steps:")
    print("1. Open index.html in your browser")
    print("2. Load the CSV files you just created")
    print("3. Start classifying your emails")

if __name__ == '__main__':
    main() 