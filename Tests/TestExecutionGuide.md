# LegalAI Test Execution Guide

This guide provides step-by-step instructions for running the LegalAI test suite using Selenium IDE.

## Quick Start

1. **Install Selenium IDE**: Install the browser extension for Chrome or Firefox
2. **Start Applications**: Ensure backend (port 8000) and frontend (port 3000) are running
3. **Open Test Suite**: Open `SeleniumIDE/TestSuite.side` in Selenium IDE
4. **Run Tests**: Click "Run all tests" to execute the complete suite

## Detailed Instructions

### Prerequisites Checklist

- [ ] Selenium IDE browser extension installed
- [ ] Backend server running on http://localhost:8000
- [ ] Frontend application running on http://localhost:3000
- [ ] Test user created with credentials: test@example.com / testpassword123
- [ ] Documents available in the system for testing

### Test Execution Options

#### 1. Complete Regression Suite
**File**: `SeleniumIDE/TestSuite.side` → "Full Regression Test Suite"
**Duration**: ~10-15 minutes
**Includes**: All authentication, chat, document, and navigation tests

#### 2. Quick Smoke Test
**File**: `SeleniumIDE/TestSuite.side` → "Smoke Test Suite"
**Duration**: ~2-3 minutes
**Includes**: Basic functionality verification

#### 3. Individual Test Categories

##### Authentication Tests
**Location**: `SeleniumIDE/Authentication/`
- `ValidLogin.side` - Test successful login
- `InvalidLogin.side` - Test failed login attempts
- `UserRegistration.side` - Test new user registration
- `SignOut.side` - Test logout functionality

##### Chat Tests
**Location**: `SeleniumIDE/Chat/`
- `SendChatMessage.side` - Test basic chat functionality
- `DocumentSummaryChat.side` - Test document-specific chat
- `ViewPreviousChat.side` - Test chat history viewing

##### Document Tests
**Location**: `SeleniumIDE/Documents/`
- `DocumentSearch.side` - Test document search functionality
- `SummaryView.side` - Test document summary display
- `DocumentView.side` - Test document viewing and interaction

##### Navigation Tests
**Location**: `SeleniumIDE/Navigation/`
- `RecommendationInterface.side` - Test recommendation system
- `HistoryInterface.side` - Test history interface

### Running Individual Tests

1. Open Selenium IDE
2. Click "Open an existing project"
3. Navigate to the specific `.side` file
4. Click "Run all tests" or select specific test cases

### Running Test Suites

1. Open Selenium IDE
2. Open `SeleniumIDE/TestSuite.side`
3. Select desired test suite from the dropdown
4. Click "Run all tests in suite"

## Test Results and Debugging

### Interpreting Results

- **Green checkmarks**: Tests passed successfully
- **Red X marks**: Tests failed - check the log for details
- **Yellow warnings**: Tests passed with warnings

### Common Issues and Solutions

#### Login Tests Failing
- **Issue**: Test user doesn't exist
- **Solution**: Create test user in your system with email: test@example.com, password: testpassword123

#### Element Not Found Errors
- **Issue**: UI elements have different data-testid attributes
- **Solution**: Update the test selectors to match your actual implementation

#### Timeout Errors
- **Issue**: Tests are running too fast for your system
- **Solution**: Increase wait times in the test steps (default: 5000ms)

#### Navigation Failures
- **Issue**: Wrong URLs or navigation paths
- **Solution**: Verify your application is running on localhost:3000

### Adjusting Tests for Your Implementation

If your application uses different element selectors:

1. Open the failing test in Selenium IDE
2. Use the record feature to capture correct selectors
3. Update the test commands with new selectors
4. Save the modified test

## Test Maintenance

### Adding New Tests

1. Create new `.side` file in appropriate category folder
2. Follow the existing test structure and naming conventions
3. Update `TestSuite.side` to include new tests if needed

### Updating Existing Tests

1. Open the test file in Selenium IDE
2. Modify commands as needed
3. Test the changes by running the updated test
4. Save the file

### Best Practices

- Keep tests independent - each test should work on its own
- Use descriptive comments for test steps
- Maintain consistent wait times across tests
- Use data-testid attributes for reliable element selection
- Regular test maintenance as UI changes

## Continuous Integration

To run these tests in CI/CD:

1. Install Selenium WebDriver
2. Use selenium-side-runner to execute .side files
3. Set up test data and environment in CI pipeline
4. Configure appropriate browser drivers

Example CI command:
```bash
selenium-side-runner SeleniumIDE/TestSuite.side
```

## Reporting Issues

When reporting test failures:

1. Include the test name and file
2. Provide error messages from Selenium IDE
3. Note browser version and OS
4. Include screenshots if helpful
5. Describe expected vs actual behavior