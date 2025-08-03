#!/usr/bin/env python3
"""
Clean Email Content Script

This script cleans up email content by:
- Removing HTML tags and styling
- Converting links to the word 'link'
- Removing unnecessary whitespace and formatting
- Making content more readable for classification
"""

import csv
import re
import html
import sys
from bs4 import BeautifulSoup

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

def clean_email_content(text):
    """Clean email content by removing HTML and formatting."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Parse HTML and extract text
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text content
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Convert URLs to 'link'
    text = re.sub(r'https?://[^\s]+', 'link', text)
    text = re.sub(r'www\.[^\s]+', 'link', text)
    
    # Remove email addresses (replace with 'email')
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email', text)
    
    # Remove phone numbers (replace with 'phone')
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{2,}', '.', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def clean_csv_file(input_file, output_file):
    """Clean all email content in a CSV file."""
    print(f"Cleaning {input_file}...")
    
    cleaned_emails = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Clean each field
            cleaned_row = {
                'subject': clean_email_content(row.get('subject', '')),
                'sender': clean_email_content(row.get('sender', '')),
                'body': clean_email_content(row.get('body', '')),
                'date': row.get('date', '')
            }
            
            cleaned_emails.append(cleaned_row)
    
    # Write cleaned data
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['subject', 'sender', 'body', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        for email in cleaned_emails:
            writer.writerow(email)
    
    print(f"Cleaned {len(cleaned_emails)} emails saved to {output_file}")

def main():
    """Clean all email CSV files."""
    files_to_clean = [
        'spam_emails.csv',
        'promotions_emails.csv', 
        'inbox_emails.csv'
    ]
    
    for file in files_to_clean:
        try:
            clean_csv_file(file, f"{file.replace('.csv', '_cleaned.csv')}")
        except FileNotFoundError:
            print(f"File {file} not found, skipping...")
        except Exception as e:
            print(f"Error cleaning {file}: {e}")
    
    print("\nCleaning complete!")
    print("Cleaned files:")
    print("- spam_emails_cleaned.csv")
    print("- promotions_emails_cleaned.csv") 
    print("- inbox_emails_cleaned.csv")

if __name__ == '__main__':
    main() 