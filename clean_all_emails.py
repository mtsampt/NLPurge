#!/usr/bin/env python3
"""
Batch Email Cleaner for NLP Training

This script cleans all email CSV files in the current directory.
It processes spam_emails.csv, promotions_emails.csv, and inbox_emails.csv
and creates cleaned versions for better NLP training.

Usage:
python clean_all_emails.py
"""

import os
import glob
from email_cleaner import process_csv_file

def clean_all_email_files():
    """Clean all email CSV files in the current directory."""
    
    # Files to clean
    files_to_clean = [
        'spam_emails.csv',
        'promotions_emails.csv', 
        'inbox_emails.csv'
    ]
    
    print("🧹 Email Cleaning Process Started")
    print("=" * 50)
    
    total_processed = 0
    
    for input_file in files_to_clean:
        if os.path.exists(input_file):
            # Create output filename
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_cleaned{ext}"
            
            print(f"\n📧 Cleaning {input_file}...")
            
            try:
                process_csv_file(input_file, output_file)
                total_processed += 1
                
                # Show file sizes
                input_size = os.path.getsize(input_file) / 1024  # KB
                output_size = os.path.getsize(output_file) / 1024  # KB
                
                print(f"   📊 File size: {input_size:.1f}KB → {output_size:.1f}KB")
                
            except Exception as e:
                print(f"   ❌ Error cleaning {input_file}: {e}")
        else:
            print(f"⚠️  {input_file} not found, skipping...")
    
    print(f"\n✅ Cleaning complete! Processed {total_processed} files.")
    print("\n📋 Cleaned files created:")
    
    # List all cleaned files
    cleaned_files = glob.glob("*_cleaned.csv")
    for file in cleaned_files:
        size = os.path.getsize(file) / 1024  # KB
        print(f"   📄 {file} ({size:.1f}KB)")
    
    print("\n🎯 Next steps:")
    print("1. Use the cleaned CSV files in the web app")
    print("2. The cleaned text will be much better for NLP training")
    print("3. All links are now just 'link' text")
    print("4. HTML and styling have been removed")

if __name__ == '__main__':
    clean_all_email_files() 