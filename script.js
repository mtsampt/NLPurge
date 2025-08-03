// Global variables
let allEmails = [];
let currentEmailIndex = 0;
let classifiedEmails = [];

// Email classification categories
const CATEGORIES = {
    SPAM: 'spam',
    PROMOTIONAL: 'promotional',
    LEGITIMATE: 'legitimate',
    NOTIFICATION: 'notification',
    RECEIPT: 'receipt'
};

// State persistence functions
function saveState() {
    const state = {
        allEmails: allEmails,
        currentEmailIndex: currentEmailIndex,
        classifiedEmails: classifiedEmails,
        timestamp: Date.now()
    };
    localStorage.setItem('emailSorterState', JSON.stringify(state));
}

function loadState() {
    const savedState = localStorage.getItem('emailSorterState');
    if (savedState) {
        try {
            const state = JSON.parse(savedState);
            
            if (state.allEmails && state.allEmails.length > 0) {
                allEmails = state.allEmails;
                currentEmailIndex = state.currentEmailIndex;
                classifiedEmails = state.classifiedEmails;
                
                // Update UI
                updateStats();
                updateProgress();
                
                // Display current email if we have emails
                if (allEmails.length > 0 && currentEmailIndex < allEmails.length) {
                    displayEmail(currentEmailIndex);
                    showMessage(`Restored session with ${allEmails.length} emails and ${classifiedEmails.length} classifications`, 'success');
                }
                
                return true;
            }
        } catch (error) {
            console.error('Error loading state:', error);
        }
    }
    return false;
}

function clearState() {
    localStorage.removeItem('emailSorterState');
}

function confirmClearSession() {
    const confirmed = confirm('Are you sure you want to clear your session? This will remove all saved progress and you\'ll need to reload your emails.');
    if (confirmed) {
        clearState();
        showMessage('Session cleared. Refresh to start fresh.', 'info');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Try to load saved state
    const stateLoaded = loadState();
    
    if (!stateLoaded) {
        updateStats();
        updateProgress();
    }
});

// Load emails from CSV files
function loadEmails(category) {
    const fileInput = document.getElementById(category + 'File');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file first');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const csvData = e.target.result;
            const emails = parseCSV(csvData, category);
            
            // Add emails to the global array
            allEmails = allEmails.concat(emails);
            
            updateStats();
            updateProgress();
            
            // Show success message
            showMessage(`Loaded ${emails.length} emails from ${category} folder`, 'success');
            
            // Enable export button if we have emails
            if (allEmails.length > 0) {
                document.getElementById('exportBtn').disabled = false;
            }
            
            // Display first email if this is the first file loaded
            if (allEmails.length === emails.length) {
                displayEmail(0);
            }
            
        } catch (error) {
            showMessage('Error parsing CSV file: ' + error.message, 'error');
        }
    };
    
    reader.readAsText(file);
}

// Load all emails from all files
function loadAllEmails() {
    const spamFile = document.getElementById('spamFile').files[0];
    const promoFile = document.getElementById('promoFile').files[0];
    const inboxFile = document.getElementById('inboxFile').files[0];
    
    console.log('Files selected:', {
        spam: spamFile ? spamFile.name : 'none',
        promo: promoFile ? promoFile.name : 'none',
        inbox: inboxFile ? inboxFile.name : 'none'
    });
    
    if (!spamFile && !promoFile && !inboxFile) {
        showMessage('Please select at least one CSV file', 'error');
        return;
    }
    
    // Reset data
    allEmails = [];
    classifiedEmails = [];
    currentEmailIndex = 0;
    
    // Clear saved state when starting fresh
    clearState();
    
    let filesToLoad = 0;
    let filesLoaded = 0;
    let totalEmailsLoaded = 0;
    
    // Count files to load
    if (spamFile) filesToLoad++;
    if (promoFile) filesToLoad++;
    if (inboxFile) filesToLoad++;
    
    console.log(`Will load ${filesToLoad} files`);
    
    // Function to check if all files are loaded
    function checkAllLoaded(emailsLoaded) {
        filesLoaded++;
        totalEmailsLoaded += emailsLoaded;
        
        console.log(`File loaded. Files loaded: ${filesLoaded}/${filesToLoad}, Emails in this file: ${emailsLoaded}, Total emails: ${totalEmailsLoaded}, allEmails array length: ${allEmails.length}`);
        
        if (filesLoaded === filesToLoad) {
            // All files loaded, show first email
            console.log(`All files loaded! Final count - allEmails array: ${allEmails.length}, totalEmailsLoaded: ${totalEmailsLoaded}`);
            if (allEmails.length > 0) {
                displayEmail(0);
                showMessage(`Loaded ${totalEmailsLoaded} total emails from ${filesToLoad} files`, 'success');
            }
        }
    }
    
    // Load each file with proper callback
    if (spamFile) {
        console.log('Loading spam file...');
        loadEmailsWithCallback('spam', checkAllLoaded);
    }
    if (promoFile) {
        console.log('Loading promo file...');
        loadEmailsWithCallback('promo', checkAllLoaded);
    }
    if (inboxFile) {
        console.log('Loading inbox file...');
        loadEmailsWithCallback('inbox', checkAllLoaded);
    }
    
    // If no files are selected, show message
    if (filesToLoad === 0) {
        showMessage('Please select at least one CSV file', 'error');
    }
}

// Load emails with callback for completion
function loadEmailsWithCallback(category, callback) {
    // Map category to correct file input ID
    let fileInputId;
    let displayCategory;
    
    switch(category) {
        case 'spam':
            fileInputId = 'spamFile';
            displayCategory = 'spam';
            break;
        case 'promo':
            fileInputId = 'promoFile';
            displayCategory = 'promotional';
            break;
        case 'inbox':
            fileInputId = 'inboxFile';
            displayCategory = 'legitimate';
            break;
        default:
            console.error(`Unknown category: ${category}`);
            callback(0);
            return;
    }
    
    const fileInput = document.getElementById(fileInputId);
    const file = fileInput.files[0];
    
    console.log(`loadEmailsWithCallback called for category: ${category} (${displayCategory}), file:`, file);
    
    if (!file) {
        console.log(`No file selected for ${category}`);
        callback(0);
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const csvData = e.target.result;
            console.log(`Parsing CSV for ${category}, data length:`, csvData.length);
            const emails = parseCSV(csvData, displayCategory);
            console.log(`Parsed ${emails.length} emails for ${category}`);
            
            // Add emails to the global array
            allEmails = allEmails.concat(emails);
            
            console.log(`After adding ${emails.length} emails from ${category}, total emails array length: ${allEmails.length}`);
            
            updateStats();
            updateProgress();
            
            // Save state after loading emails
            saveState();
            
            // Show success message
            showMessage(`Loaded ${emails.length} emails from ${displayCategory} folder`, 'success');
            
            // Enable export button if we have emails
            if (allEmails.length > 0) {
                document.getElementById('exportBtn').disabled = false;
            }
            
            // Call the callback with number of emails loaded
            callback(emails.length);
            
        } catch (error) {
            console.error(`Error parsing CSV for ${category}:`, error);
            showMessage('Error parsing CSV file: ' + error.message, 'error');
            callback(0);
        }
    };
    
    reader.readAsText(file);
}

// Parse CSV data
function parseCSV(csvData, category) {
    const lines = csvData.split('\n');
    
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const emails = [];
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const values = parseCSVLine(line);
        
        if (values.length >= headers.length) {
            let subject = values[headers.indexOf('subject')] || values[headers.indexOf('Subject')] || '';
            let sender = values[headers.indexOf('sender')] || values[headers.indexOf('Sender')] || values[headers.indexOf('from')] || values[headers.indexOf('From')] || '';
            let body = values[headers.indexOf('body')] || values[headers.indexOf('Body')] || values[headers.indexOf('content')] || values[headers.indexOf('Content')] || '';
            let date = values[headers.indexOf('date')] || values[headers.indexOf('Date')] || '';
            
            // Clean up data
            subject = subject.replace(/[^\x20-\x7E]/g, '').trim(); // Remove non-printable characters
            sender = sender.replace(/[^\x20-\x7E]/g, '').trim(); // Remove non-printable characters
            
            // If sender looks like an address instead of email, try to extract email
            if (sender && !sender.includes('@') && sender.includes(' ')) {
                // Try to find email pattern in the sender
                const emailMatch = sender.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
                if (emailMatch) {
                    sender = emailMatch[0];
                }
            }
            
            const email = {
                subject: subject,
                sender: sender,
                body: body,
                date: date,
                originalCategory: category,
                userClassification: null
            };
            
            emails.push(email);
        }
    }
    
    return emails;
}

// Parse CSV line handling quoted fields
function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            values.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    values.push(current.trim());
    return values;
}

// Display email at given index
function displayEmail(index) {
    if (index < 0 || index >= allEmails.length) {
        document.getElementById('emailSubject').textContent = 'No more emails to classify';
        document.getElementById('emailSender').textContent = '';
        document.getElementById('emailDate').textContent = '';
        document.getElementById('emailBody').textContent = 'All emails have been classified!';
        
        // Update summary boxes
        document.getElementById('summarySubject').textContent = 'No more emails to classify';
        document.getElementById('summarySender').textContent = '';
        return;
    }
    
    const email = allEmails[index];
    
    document.getElementById('emailSubject').textContent = email.subject || 'No Subject';
    document.getElementById('emailSender').textContent = email.sender || 'Unknown Sender';
    document.getElementById('emailDate').textContent = email.date || '';
    document.getElementById('emailBody').textContent = email.body || 'No content available';
    
    // Update summary boxes
    document.getElementById('summarySubject').textContent = email.subject || 'No Subject';
    document.getElementById('summarySender').textContent = email.sender || 'Unknown Sender';
    
    currentEmailIndex = index;
    updateProgress();
}

// Classify current email
function classifyEmail(category) {
    if (currentEmailIndex >= allEmails.length) {
        showMessage('No more emails to classify', 'info');
        return;
    }
    
    const email = allEmails[currentEmailIndex];
    email.userClassification = category;
    
    // Add to classified emails
    classifiedEmails.push({
        subject: email.subject,
        sender: email.sender,
        body: email.body,
        date: email.date,
        originalCategory: email.originalCategory,
        userClassification: category
    });
    
    // Move to next email
    currentEmailIndex++;
    displayEmail(currentEmailIndex);
    updateStats();
    
    // Save state after classification
    saveState();
    
    // Show classification feedback
    const categoryNames = {
        'spam': 'Spam',
        'promotional': 'Promotional',
        'legitimate': 'Legitimate'
    };
    
    showMessage(`Classified as ${categoryNames[category]}`, 'success');
}

// Export classified data to CSV
function exportCSV() {
    if (classifiedEmails.length === 0) {
        showMessage('No classified emails to export', 'error');
        return;
    }
    
    // Create CSV content
    const headers = ['subject', 'sender', 'body', 'date', 'original_category', 'user_classification'];
    const csvContent = [
        headers.join(','),
        ...classifiedEmails.map(email => [
            `"${escapeCSVField(email.subject)}"`,
            `"${escapeCSVField(email.sender)}"`,
            `"${escapeCSVField(email.body)}"`,
            `"${escapeCSVField(email.date)}"`,
            `"${escapeCSVField(email.originalCategory)}"`,
            `"${escapeCSVField(email.userClassification)}"`
        ].join(','))
    ].join('\n');
    
    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `email_classifications_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showMessage(`Exported ${classifiedEmails.length} classified emails`, 'success');
}

// Escape CSV field content
function escapeCSVField(field) {
    if (!field) return '';
    return field.replace(/"/g, '""').replace(/\n/g, ' ').replace(/\r/g, ' ');
}

// Update statistics display
function updateStats() {
    const total = allEmails.length;
    const spam = classifiedEmails.filter(e => e.userClassification === 'spam').length;
    const promo = classifiedEmails.filter(e => e.userClassification === 'promotional').length;
    const legitimate = classifiedEmails.filter(e => e.userClassification === 'legitimate').length;
    const notification = classifiedEmails.filter(e => e.userClassification === 'notification').length;
    const receipt = classifiedEmails.filter(e => e.userClassification === 'receipt').length;
    
    console.log(`updateStats called - Total emails: ${total}, Spam: ${spam}, Promo: ${promo}, Legitimate: ${legitimate}, Notification: ${notification}, Receipt: ${receipt}`);
    
    document.getElementById('totalEmails').textContent = total;
    document.getElementById('spamCount').textContent = spam;
    document.getElementById('promoCount').textContent = promo;
    document.getElementById('legitimateCount').textContent = legitimate;
    document.getElementById('notificationCount').textContent = notification;
    document.getElementById('receiptCount').textContent = receipt;
}

// Update progress bar
function updateProgress() {
    const total = allEmails.length;
    const classified = classifiedEmails.length;
    
    if (total === 0) {
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressText').textContent = 'Ready to start sorting';
        return;
    }
    
    const percentage = (classified / total) * 100;
    document.getElementById('progressFill').style.width = percentage + '%';
    document.getElementById('progressText').textContent = 
        `${classified} of ${total} emails classified (${Math.round(percentage)}%)`;
}

// Reset all data
function resetData() {
    allEmails = [];
    classifiedEmails = [];
    currentEmailIndex = 0;
    
    // Clear saved state
    clearState();
    
    // Clear file inputs
    document.getElementById('spamFile').value = '';
    document.getElementById('promoFile').value = '';
    document.getElementById('inboxFile').value = '';
    
    // Reset display
    document.getElementById('emailSubject').textContent = 'No emails loaded';
    document.getElementById('emailSender').textContent = 'Click "Load Emails" to start';
    document.getElementById('emailDate').textContent = '';
    document.getElementById('emailBody').textContent = 'Load your emails to start sorting...';
    
    // Reset summary boxes
    document.getElementById('summarySubject').textContent = 'No emails loaded';
    document.getElementById('summarySender').textContent = 'Click "Load Emails" to start';
    
    // Disable export button
    document.getElementById('exportBtn').disabled = true;
    
    updateStats();
    updateProgress();
    
    showMessage('Data reset successfully', 'success');
}

// Show message to user
function showMessage(message, type = 'info') {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    // Style the message
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    messageDiv.style.backgroundColor = colors[type] || colors.info;
    
    // Add to page
    document.body.appendChild(messageDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        messageDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT') return; // Don't interfere with input fields
    
    switch(e.key) {
        case '1':
        case 's':
        case 'S':
            if (currentEmailIndex < allEmails.length) {
                classifyEmail('spam');
            }
            break;
        case '2':
        case 'p':
        case 'P':
            if (currentEmailIndex < allEmails.length) {
                classifyEmail('promotional');
            }
            break;
        case '3':
        case 'l':
        case 'L':
            if (currentEmailIndex < allEmails.length) {
                classifyEmail('legitimate');
            }
            break;
        case 'ArrowRight':
        case ' ':
            if (currentEmailIndex < allEmails.length) {
                classifyEmail('legitimate'); // Default to legitimate
            }
            break;
    }
});

// Add keyboard shortcuts help
document.addEventListener('DOMContentLoaded', function() {
    const helpText = document.createElement('div');
    helpText.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); color: white; padding: 15px; border-radius: 10px; font-size: 0.9rem; z-index: 1000;">
            <strong>Keyboard Shortcuts:</strong><br>
            1/S - Spam | 2/P - Promotional | 3/L - Legitimate<br>
            Space/→ - Mark as Legitimate
        </div>
    `;
    document.body.appendChild(helpText);
}); 