# Selenium IDE Import Instructions

## Quick Start - Import Tests

### Option 1: Import Main Test Suite
1. Open Selenium IDE browser extension
2. Click "Open an existing project"
3. Navigate to: `f:\Semester 5\DSE Project\LegalAI\Tests\SeleniumIDE\TestSuite.side`
4. Click "Open"
5. You'll see all test suites ready to run!

### Option 2: Import Individual Test Categories

#### Authentication Tests
- File: `Tests\SeleniumIDE\Authentication\ValidLogin.side`
- File: `Tests\SeleniumIDE\Authentication\InvalidLogin.side`
- File: `Tests\SeleniumIDE\Authentication\UserRegistration.side`
- File: `Tests\SeleniumIDE\Authentication\SignOut.side`

#### Chat Tests
- File: `Tests\SeleniumIDE\Chat\SendChatMessage.side`
- File: `Tests\SeleniumIDE\Chat\DocumentSummaryChat.side`
- File: `Tests\SeleniumIDE\Chat\ViewPreviousChat.side`

#### Document Tests
- File: `Tests\SeleniumIDE\Documents\DocumentSearch.side`
- File: `Tests\SeleniumIDE\Documents\SummaryView.side`
- File: `Tests\SeleniumIDE\Documents\DocumentView.side`

#### Navigation Tests
- File: `Tests\SeleniumIDE\Navigation\RecommendationInterface.side`
- File: `Tests\SeleniumIDE\Navigation\HistoryInterface.side`

## Running Tests After Import

### Run Complete Suite
1. Open `TestSuite.side`
2. Select "Full Regression Test Suite" from dropdown
3. Click "Run all tests"

### Run Individual Tests
1. Open any individual `.side` file
2. Click "Run all tests" or select specific test cases
3. Monitor results in the log panel

### Run Specific Test Categories
1. Open `TestSuite.side`
2. Choose from available suites:
   - "Smoke Test Suite" (Quick verification)
   - "Authentication Test Suite" (Login/logout tests)
   - "Functional Test Suite" (Chat, documents, navigation)

## Test File Formats

All files are in Selenium IDE's native `.side` format (JSON-based):
- **Compatible** with Selenium IDE 3.x and later
- **Cross-platform** - works on Windows, Mac, Linux
- **Version controlled** - can be tracked in Git
- **Editable** - can be modified in Selenium IDE or text editor

## Troubleshooting Import

### If Import Fails:
1. **Check file path** - ensure files exist at specified locations
2. **Check Selenium IDE version** - use latest version
3. **Try individual files** - import one test at a time
4. **Check file format** - ensure `.side` extension

### If Tests Don't Run:
1. **Verify application URLs** - ensure frontend is on localhost:3000
2. **Check test data** - create test user as specified in documentation
3. **Update selectors** - modify data-testid attributes if needed

## Customizing Tests

### Modify Test Data:
1. Open any `.side` file in Selenium IDE
2. Edit the "type" commands to change input values
3. Save the file

### Add New Test Steps:
1. Open test in Selenium IDE
2. Use record feature to capture new actions
3. Insert new commands where needed
4. Save the updated test

### Export Modified Tests:
1. File → Export project
2. Choose location and filename
3. Share with team or save to version control