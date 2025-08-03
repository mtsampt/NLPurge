#!/usr/bin/env python3
"""
Fixed Email Text Cleaner for NLP Training

This version handles large CSV fields and processes all emails correctly.
It increases the CSV field size limit and adds better error handling.

Usage:
python email_cleaner_fixed.py input.csv output.csv
"""

import csv
import re
import sys
import html
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import unicodedata

# Increase CSV field size limit
import sys
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

class EmailCleaner:
    def __init__(self):
        # Common email signatures and footers to remove
        self.signature_patterns = [
            r'--\s*\n',  # Email signature separator
            r'Sent from my iPhone',
            r'Sent from my Android',
            r'Get Outlook for iOS',
            r'Get Outlook for Android',
            r'This email was sent from a notification-only address',
            r'Please do not reply to this email',
            r'To unsubscribe',
            r'Click here to unsubscribe',
            r'If you received this email in error',
            r'This is an automated message',
            r'Powered by',
            r'© \d{4}',
            r'All rights reserved',
            r'Confidentiality Notice',
            r'This message is intended only for',
            r'If you are not the intended recipient',
        ]
        
        # HTML entities to decode
        self.html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'",
        }
    
    def clean_email_text(self, text):
        """Main cleaning function for email text."""
        if not text:
            return ""
        
        try:
            # Step 1: Decode HTML entities
            text = self.decode_html_entities(text)
            
            # Step 2: Remove HTML tags
            text = self.remove_html_tags(text)
            
            # Step 3: Convert links to "link"
            text = self.convert_links_to_text(text)
            
            # Step 4: Remove email signatures and footers
            text = self.remove_signatures(text)
            
            # Step 5: Clean whitespace and normalize
            text = self.normalize_whitespace(text)
            
            # Step 6: Remove excessive punctuation
            text = self.clean_punctuation(text)
            
            # Step 7: Normalize unicode characters
            text = self.normalize_unicode(text)
            
            return text.strip()
        except Exception as e:
            print(f"Warning: Error cleaning text: {e}")
            return text.strip() if text else ""
    
    def decode_html_entities(self, text):
        """Decode common HTML entities."""
        # Use BeautifulSoup for comprehensive HTML entity decoding
        try:
            # Check if text looks like HTML
            if '<' in text and '>' in text:
                soup = BeautifulSoup(text, 'html.parser')
                text = soup.get_text()
            else:
                # Manual decoding for non-HTML text
                for entity, replacement in self.html_entities.items():
                    text = text.replace(entity, replacement)
        except Exception as e:
            # Fallback: manual decoding
            for entity, replacement in self.html_entities.items():
                text = text.replace(entity, replacement)
        
        return text
    
    def remove_html_tags(self, text):
        """Remove HTML tags while preserving text content."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove script and style content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove CSS comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        return text
    
    def convert_links_to_text(self, text):
        """Convert URLs and links to 'link' text."""
        # Convert HTTP/HTTPS URLs
        text = re.sub(r'https?://[^\s<>"{}|\\^`\[\]]+', 'link', text)
        
        # Convert www URLs
        text = re.sub(r'www\.[^\s<>"{}|\\^`\[\]]+', 'link', text)
        
        # Convert email addresses to 'email'
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email', text)
        
        # Convert phone numbers to 'phone'
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone', text)
        
        # Convert common link patterns
        text = re.sub(r'\[link\].*?\[/link\]', 'link', text, flags=re.IGNORECASE)
        text = re.sub(r'<a[^>]*>.*?</a>', 'link', text, flags=re.IGNORECASE)
        
        return text
    
    def remove_signatures(self, text):
        """Remove common email signatures and footers."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Check if line matches signature patterns
            is_signature = False
            for pattern in self.signature_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_signature = True
                    break
            
            if not is_signature:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def normalize_whitespace(self, text):
        """Normalize whitespace and remove excessive spacing."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def clean_punctuation(self, text):
        """Clean excessive punctuation."""
        # Remove multiple consecutive punctuation marks
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        # Remove excessive commas
        text = re.sub(r',{2,}', ',', text)
        
        return text
    
    def normalize_unicode(self, text):
        """Normalize unicode characters."""
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Replace em dashes and en dashes
        text = text.replace('—', '-').replace('–', '-')
        
        return text
    
    def clean_subject(self, subject):
        """Clean email subject line."""
        if not subject:
            return "No Subject"
        
        # Remove common prefixes
        subject = re.sub(r'^(RE|FWD|FW|FWD|RE:)\s*:?\s*', '', subject, flags=re.IGNORECASE)
        
        # Clean the subject
        subject = self.clean_email_text(subject)
        
        return subject if subject else "No Subject"
    
    def clean_sender(self, sender):
        """Clean sender information."""
        if not sender:
            return "Unknown Sender"
        
        # Extract just the email address if it's in "Name <email>" format
        email_match = re.search(r'<([^>]+)>', sender)
        if email_match:
            return email_match.group(1)
        
        # If it's just an email address, return as is
        if '@' in sender:
            return sender
        
        return sender

def process_csv_file(input_file, output_file):
    """Process a CSV file and clean all email content."""
    cleaner = EmailCleaner()
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=['subject', 'sender', 'body', 'date'])
            
            writer.writeheader()
            
            processed = 0
            skipped = 0
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Clean each field
                    cleaned_row = {
                        'subject': cleaner.clean_subject(row.get('subject', '')),
                        'sender': cleaner.clean_sender(row.get('sender', '')),
                        'body': cleaner.clean_email_text(row.get('body', '')),
                        'date': row.get('date', '')
                    }
                    
                    writer.writerow(cleaned_row)
                    processed += 1
                    
                    if processed % 100 == 0:
                        print(f"Processed {processed} emails...")
                        
                except Exception as e:
                    print(f"Warning: Skipping row {row_num} due to error: {e}")
                    skipped += 1
                    continue
            
            print(f"✅ Successfully cleaned {processed} emails")
            if skipped > 0:
                print(f"⚠️  Skipped {skipped} emails due to errors")
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")

def main():
    """Main function."""
    if len(sys.argv) != 3:
        print("Usage: python email_cleaner_fixed.py input.csv output.csv")
        print("\nExample:")
        print("  python email_cleaner_fixed.py spam_emails.csv spam_emails_cleaned.csv")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not input_file.endswith('.csv'):
        print("❌ Input file must be a CSV file")
        return
    
    print(f"Cleaning emails from {input_file}...")
    process_csv_file(input_file, output_file)
    print(f"✅ Cleaned emails saved to {output_file}")

if __name__ == '__main__':
    main() 