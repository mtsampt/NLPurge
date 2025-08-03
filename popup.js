// Get DOM elements
const clickButton = document.getElementById('clickButton');
const counter = document.getElementById('counter');

// Initialize click count from storage or default to 0
let clickCount = 0;

// Load saved click count when popup opens
chrome.storage.local.get(['clickCount'], function(result) {
  clickCount = result.clickCount || 0;
  updateCounter();
});

// Add click event listener
clickButton.addEventListener('click', function() {
  clickCount++;
  updateCounter();
  
  // Save to Chrome storage
  chrome.storage.local.set({clickCount: clickCount});
  
  // Add a fun animation effect
  clickButton.style.transform = 'scale(0.95)';
  setTimeout(() => {
    clickButton.style.transform = 'scale(1)';
  }, 100);
});

// Update the counter display
function updateCounter() {
  counter.textContent = `Clicks: ${clickCount}`;
}

// Add some console logging for debugging
console.log('Hello World Extension loaded!'); 