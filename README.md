# Email Sorter - NLP Training Tool

A web application for sorting emails into categories (Spam, Promotional, Legitimate) to create training data for NLP models.

## Features

- **Easy Email Classification**: Sort emails with one-click buttons
- **Keyboard Shortcuts**: Fast classification with keyboard (1/S for Spam, 2/P for Promotional, 3/L for Legitimate)
- **Progress Tracking**: Real-time progress bar and statistics
- **CSV Export**: Export classified data for machine learning training
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Multiple File Support**: Load emails from different Gmail folders

## How to Use

### 1. Get Your Gmail Data

You'll need to export your emails from Gmail as CSV files. Here's how:

#### Option A: Using Gmail's Export Feature
1. Go to [Google Takeout](https://takeout.google.com/)
2. Select "Mail" and choose your Gmail account
3. Download the data and extract the MBOX files
4. Convert MBOX to CSV using a tool like [mbox2csv](https://github.com/jeffkaufman/mbox2csv)

#### Option B: Using Gmail API (Recommended)
1. Set up a Google Cloud Project
2. Enable Gmail API
3. Use a script to export emails to CSV format
4. Filter emails by folder (Spam, Promotions, Inbox)

#### Option C: Manual Export
1. In Gmail, search for emails in each folder
2. Use Gmail's export feature or a browser extension
3. Convert to CSV format with columns: subject, sender, body, date

### 2. Prepare Your CSV Files

Your CSV files should have these columns:
- `subject` - Email subject line
- `sender` - Email sender address
- `body` - Email content
- `date` - Email date

Example format (see `sample_data.csv`):
```csv
subject,sender,body,date
"Welcome to our newsletter","newsletter@example.com","Dear subscriber...","2024-01-15"
```

### 3. Use the Web App

1. **Open the web app** by opening `index.html` in your browser
2. **Load your CSV files**:
   - Spam folder CSV (all spam emails)
   - Promotions folder CSV (300 most recent)
   - Inbox CSV (500 most recent)
3. **Classify emails** using the buttons or keyboard shortcuts
4. **Export your data** when finished

## Keyboard Shortcuts

- **1** or **S** - Mark as Spam
- **2** or **P** - Mark as Promotional  
- **3** or **L** - Mark as Legitimate
- **Space** or **→** - Mark as Legitimate (default)

## Data Collection Strategy

For optimal training data:

### Spam Folder
- Export ALL emails from your spam folder
- These will be pre-classified as spam by Gmail

### Promotions Folder  
- Export the 300 most recent emails
- These are typically promotional content
- You'll re-classify them as spam, promotional, or legitimate

### Inbox Folder
- Export the 500 most recent emails
- These are typically legitimate emails
- You'll re-classify them as spam, promotional, or legitimate

## Output Format

The exported CSV will contain:
- `subject` - Original email subject
- `sender` - Original email sender
- `body` - Original email content
- `date` - Original email date
- `original_category` - Where the email came from (spam/promotional/legitimate)
- `user_classification` - Your classification (spam/promotional/legitimate)

## Tips for Better Training Data

1. **Be Consistent**: Use the same criteria for classification
2. **Take Breaks**: Don't classify too many emails at once
3. **Review Periodically**: Check your classifications for consistency
4. **Include Variety**: Make sure you have diverse examples in each category

## Technical Details

- **Frontend**: Pure HTML/CSS/JavaScript (no dependencies)
- **File Format**: CSV with UTF-8 encoding
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Data Storage**: All processing happens in the browser (no server needed)

## Files

- `index.html` - Main application interface
- `styles.css` - Styling and responsive design
- `script.js` - Application logic and functionality
- `sample_data.csv` - Example CSV format
- `README.md` - This documentation

## Next Steps

After exporting your classified data:

1. **Clean the data** - Remove duplicates, handle missing values
2. **Split into train/test sets** - 80% training, 20% testing
3. **Train your NLP model** - Use libraries like scikit-learn, spaCy, or transformers
4. **Evaluate performance** - Test on unseen data
5. **Deploy your model** - Integrate with Gmail or create a Chrome extension

## Troubleshooting

- **CSV parsing errors**: Make sure your CSV has the correct headers
- **Large files**: The app works best with files under 10MB
- **Browser issues**: Try refreshing the page or clearing browser cache
- **Export problems**: Check that you have classified at least one email

## Privacy

- All data processing happens locally in your browser
- No data is sent to any server
- Your email data never leaves your computer
- The app works completely offline 