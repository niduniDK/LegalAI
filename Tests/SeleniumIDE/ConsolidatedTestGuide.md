# LegalAI Consolidated Test Suite

## Overview

The `AllTestsConsolidated.side` file contains all LegalAI test scenarios in a single Selenium IDE project file, updated with real frontend element selectors based on the actual Next.js implementation.

## Key Updates

### 🔄 Element Selector Updates

**Previous (Generic)**: Used placeholder `data-testid` attributes
```
css=[data-testid="login-button"]
css=[data-testid="email-input"]
```

**Current (Real Frontend)**: Uses actual HTML and CSS selectors
```
id=email                                    // Real form input IDs
css=button[type="submit"]                   // Actual button types
css=input[placeholder*="Ask anything"]      // Real placeholder text
```

### 🎯 Selector Strategy

1. **HTML Form Elements** (Primary)
   - Uses standard HTML attributes (`id`, `name`, `type`)
   - Based on actual form implementation in login/register pages

2. **CSS Component Selectors**
   - Utilizes Tailwind CSS classes from real components
   - Targets specific UI states (`.bg-red-50` for errors, `.hover:shadow-md` for cards)

3. **Placeholder-based Selection**
   - Matches actual placeholder text from input components
   - Context-aware selection for different interfaces

4. **XPath Text Matching**
   - Uses real button text and heading content
   - Navigates based on actual UI text content

## Test Coverage

### Authentication (4 tests)
- ✅ Valid Login - Uses real email/password inputs (`id=email`, `id=password`)
- ✅ Invalid Login - Tests error message display (`.bg-red-50`)
- ✅ User Registration - Real form fields (`id=first_name`, `id=last_name`)
- ✅ Sign Out - Sidebar dropdown interaction

### Chat Functionality (3 tests)
- ✅ Send Chat Message - Main chat input (`input[placeholder*="Ask anything"]`)
- ✅ Document Summary Chat - Follow-up questions interface
- ✅ View Previous Chat - Chat sessions page navigation

### Document Management (3 tests)
- ✅ Document Search - Discover page search (`input[placeholder*="Search legal documents"]`)
- ✅ Summary View - Ask AI button interaction
- ✅ Document View - External document viewing

### Navigation & Interface (3 tests)
- ✅ Recommendation Interface - Recommendations page interaction
- ✅ History Interface - Activity history and search
- ✅ Navigation Sidebar - Menu navigation testing

## Frontend Integration Points

### Login/Register Pages
```javascript
// Real selectors from login/register components
id=email                    // Email input field
id=password                // Password input field
id=first_name              // Registration first name
id=last_name               // Registration last name
button[type="submit"]      // Form submission
```

### Chat Interface
```javascript
// Main chat (ChatBox component)
input[placeholder*="Ask anything"]           // Main chat input
css=button[class*="absolute right-2"]       // Send button

// Chat messages (ChatInterface component)
css=.max-w-[70%].bg-muted                  // AI response bubbles
css=.max-w-[70%].bg-primary                // User message bubbles
```

### Document Discovery
```javascript
// Search and document cards
input[placeholder*="Search legal documents"] // Search input
css=.hover:shadow-md                        // Document cards
xpath=//button[contains(text(),'Ask AI')]   // AI interaction
xpath=//button[contains(text(),'View')]     // View document
```

### Navigation Components
```javascript
// Sidebar navigation (AppSidebarNew component)
css=button[data-sidebar="trigger"]          // Sidebar toggle
xpath=//span[contains(text(),'Chat')]       // Navigation items
xpath=//span[contains(text(),'Discover')]
xpath=//span[contains(text(),'History')]
```

## Test Execution

### Prerequisites
1. Frontend running on `http://localhost:3000`
2. Backend API running on `http://localhost:8000`
3. Valid test user credentials
4. Selenium IDE browser extension installed

### Running the Tests
1. Open Selenium IDE
2. Open `AllTestsConsolidated.side`
3. Select test suite or individual tests
4. Click "Run all tests" or "Run current test"

### Test Data Requirements
```javascript
// Valid login credentials
Email: test@example.com
Password: Test123!@#

// Registration data
First Name: John
Last Name: Doe
Email: john.doe@example.com
Password: SecurePass123!@#
```

## Debugging Tips

### Common Issues
1. **Element Not Found**: Verify frontend is running and element selectors match current implementation
2. **Timing Issues**: Increase wait times for slow-loading components
3. **Authentication**: Ensure test user exists in database

### Selector Verification
```bash
# Open browser dev tools and test selectors:
document.querySelector('id=email')                    // Should find email input
document.querySelector('input[placeholder*="Ask anything"]') // Should find chat input
```

## Maintenance

When frontend components change:
1. Update corresponding selectors in test file
2. Test selector changes in browser dev tools first
3. Update this documentation with new patterns
4. Run tests to verify functionality

This consolidated approach ensures all tests use real, reliable selectors that match the actual LegalAI frontend implementation.