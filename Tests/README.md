# LegalAI Test Suite

This directory contains comprehensive test scripts for the LegalAI application using Selenium IDE.

## Prerequisites

1. **Selenium IDE Browser Extension**
   - Install Selenium IDE extension for Chrome or Firefox
   - Download from: https://selenium.dev/selenium-ide/

2. **Application Setup**
   - Ensure the backend server is running on `http://localhost:8000`
   - Ensure the frontend application is running on `http://localhost:3000`
   - Have test user credentials ready

3. **Test Data**
   - Valid test user credentials
   - Invalid credentials for negative testing
   - Sample documents for search testing

## Test Structure

```
Tests/
├── SeleniumIDE/
│   ├── Authentication/     # Login, registration, logout tests
│   ├── Chat/              # Chat functionality tests
│   ├── Documents/         # Document search and view tests
│   ├── Navigation/        # Interface navigation tests
│   └── TestSuite.side     # Main test suite
├── README.md              # This file
└── TestData/              # Test data and configuration
```

## Running Tests

### Individual Tests
1. Open Selenium IDE
2. Open the desired `.side` test file
3. Click "Run all tests" or run individual test cases

### Complete Test Suite
1. Open Selenium IDE
2. Open `SeleniumIDE/TestSuite.side`
3. Run the complete test suite

## Test Categories

### Authentication Tests
- Valid login with correct credentials
- Invalid login with wrong credentials  
- User registration with valid data
- Sign out functionality

### Chat Functionality Tests
- Send chat message to chatbot
- Document summary chat interface
- View previous chat history

### Document Tests
- Document search functionality
- Summary view testing
- Document view and interaction

### Navigation Tests
- Recommendation system interface
- History interface navigation
- Interface switching and navigation flow

## Test Data Requirements

Create test users with the following characteristics:
- Valid user: email and password for successful login
- Invalid credentials for negative testing
- New user data for registration testing

## Element Selectors Used

The tests use a combination of selector strategies based on actual frontend implementation:

### HTML Form Elements (Primary)
- `id=email` - Email input fields
- `id=password` - Password input fields  
- `id=first_name`, `id=last_name` - Registration form fields
- `id=confirmPassword` - Password confirmation field
- `button[type="submit"]` - Form submission buttons

### CSS Class Selectors (Component-based)
- `.bg-red-50` - Error message containers
- `.bg-green-50` - Success message containers
- `.hover:shadow-md` - Document cards and interactive elements
- `.max-w-[70%].bg-muted` - Chat message bubbles
- `.pl-10` - Search input fields with left padding

### Placeholder-based Selectors (Context-aware)
- `input[placeholder*="Ask anything"]` - Main chat input on homepage
- `input[placeholder*="Search legal documents"]` - Document search input
- `input[placeholder*="Search your recent activity"]` - History search
- `input[placeholder*="Ask a question"]` - Document chat interface

### XPath Selectors (Text-based)
- `//button[contains(text(),'Sign In')]` - Login button
- `//button[contains(text(),'Ask AI')]` - Document AI interaction
- `//button[contains(text(),'View')]` - Document view buttons
- `//h1[contains(text(),'Break Legal jargon here.')]` - Homepage title
- `//h2[contains(text(),'Recommended for You')]` - Recommendations section
- `//span[contains(text(),'Chat')]` - Navigation menu items

### Component Structure Selectors
- `css=button[data-sidebar="trigger"]` - Sidebar toggle button
- `css=.grid.gap-4` - Document grid layouts
- `css=.animate-pulse` - Loading states
- `css=.absolute.right-2` - Positioned send buttons

## Notes

- Tests assume the application is running on localhost:3000
- Backend API should be available on localhost:8000
- Some tests may require specific documents to be available in the system
- Adjust wait times in tests based on your system performance
- **Updated**: All selectors now match the actual Next.js frontend implementation

## Troubleshooting

1. **Tests failing due to timing**
   - Increase wait times in test steps
   - Add explicit waits for elements to load

2. **Element not found errors**
   - Verify selectors match current UI implementation
   - Update selectors if UI has changed

3. **Login tests failing**
   - Verify test credentials are correct
   - Check if user accounts exist in the system