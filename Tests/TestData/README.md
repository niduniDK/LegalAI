# Test Data Configuration

This directory contains test data and configuration files for the LegalAI test suite.

## Test Users

### Valid Test User
- **Email**: test@example.com
- **Password**: testpassword123
- **Name**: Test User
- **Purpose**: Used for valid login tests and functional testing

### Registration Test User
- **First Name**: Test
- **Last Name**: User
- **Email**: Dynamic (generated with timestamp)
- **Password**: TestPassword123!
- **Purpose**: Used for registration testing

## Test Credentials Setup

Before running tests, ensure you have created test users in your system:

1. **Create Valid Test User**:
   ```bash
   # Run this in your backend to create the test user
   # (Replace with your actual user creation method)
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpassword123",
       "firstName": "Test",
       "lastName": "User"
     }'
   ```

## Test Search Terms

### Document Search
- **Constitution**: Should return constitutional documents
- **Legal**: Should return legal documents
- **Empty search**: Should return all documents

### Chat Test Messages
- **General**: "What is the Constitution of India about?"
- **Document specific**: "Can you summarize the main points of this document?"
- **Legal query**: "What are the key legal provisions mentioned?"

## Expected Elements

### Data Test IDs
The following data-testid attributes should be present in your application:

#### Authentication
- `login-button`
- `register-button`
- `logout-button`
- `email-input`
- `password-input`
- `firstname-input`
- `lastname-input`
- `confirm-password-input`
- `login-submit`
- `register-submit`
- `terms-checkbox`
- `user-menu`

#### Navigation
- `dashboard`
- `discover-nav`
- `chat-nav`
- `recommendation-nav`
- `history-nav`

#### Interfaces
- `discover-interface`
- `chat-interface`
- `recommendation-interface`
- `history-interface`

#### Documents
- `document-card`
- `document-title`
- `document-summary`
- `document-content`
- `document-text`
- `document-metadata`
- `document-info`
- `view-document`
- `chat-with-document`
- `download-document`
- `share-document`

#### Chat
- `chat-input`
- `send-button`
- `user-message`
- `ai-message`
- `chat-message`
- `document-chat-interface`

#### Search and History
- `search-input`
- `search-button`
- `search-results`
- `history-item`
- `chat-history`
- `document-history`
- `no-history`
- `no-recommendations`

#### Modals and Dialogs
- `summary-modal`
- `summary-dialog`
- `full-summary`
- `read-more-button`
- `close-modal`
- `close-dialog`

#### Messages and Errors
- `success-message`
- `error-message`
- `no-history-message`
- `no-recommendations-message`

## Environment Setup

### Required URLs
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

### Browser Support
Tests are designed to work with:
- Chrome (with Selenium IDE extension)
- Firefox (with Selenium IDE extension)

## Test Data Files

Add any test documents or data files to this directory as needed for specific test scenarios.