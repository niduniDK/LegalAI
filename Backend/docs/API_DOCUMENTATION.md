# LegalAI Authentication API Documentation

## Overview

This document describes the authentication system for the LegalAI application, including user registration, login, email verification, password reset, and user management features.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication Endpoints

#### 1. Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "confirm_password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "message": "Registration successful. Please check your email for verification code.",
  "success": true
}
```

#### 2. Verify Email

**POST** `/auth/verify`

Verify user email with verification code.

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "success": true
}
```

#### 3. Login

**POST** `/auth/login`

Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 4. Forgot Password

**POST** `/auth/forgot-password`

Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent",
  "success": true
}
```

#### 5. Reset Password

**POST** `/auth/reset-password`

Reset password with reset token.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123",
  "confirm_password": "NewSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "success": true
}
```

#### 6. Resend Verification

**POST** `/auth/resend-verification`

Resend email verification code.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Verification code sent successfully",
  "success": true
}
```

### User Management Endpoints

#### 1. Get Current User

**GET** `/auth/me`

Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-01T12:00:00Z"
}
```

#### 2. Update User Profile

**PUT** `/auth/me`

Update user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-01T12:00:00Z"
}
```

#### 3. Change Password

**POST** `/auth/change-password`

Change user password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "CurrentPassword123",
  "new_password": "NewPassword123",
  "confirm_password": "NewPassword123"
}
```

**Response:**
```json
{
  "message": "Password changed successfully",
  "success": true
}
```

#### 4. Logout

**POST** `/auth/logout`

Logout user (for logging purposes).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Logged out successfully",
  "success": true
}
```

### User Preferences Endpoints

#### 1. Get User Preferences

**GET** `/auth/preferences`

Get all user preferences.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "preference_key": "theme",
    "preference_value": "dark",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

#### 2. Create/Update User Preference

**POST** `/auth/preferences`

Create or update a user preference.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "preference_key": "theme",
  "preference_value": "dark"
}
```

**Response:**
```json
{
  "id": 1,
  "preference_key": "theme",
  "preference_value": "dark",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### 3. Update Specific Preference

**PUT** `/auth/preferences/{preference_key}`

Update a specific user preference.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "preference_value": "light"
}
```

**Response:**
```json
{
  "id": 1,
  "preference_key": "theme",
  "preference_value": "light",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

#### 4. Delete User Preference

**DELETE** `/auth/preferences/{preference_key}`

Delete a specific user preference.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Preference deleted successfully",
  "success": true
}
```

### Chat History Endpoints

#### 1. Create Chat Session

**POST** `/chat-history/sessions`

Create a new chat session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "session_name": "Legal Consultation - Property Law"
}
```

**Response:**
```json
{
  "id": 1,
  "session_name": "Legal Consultation - Property Law",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### 2. Get User Chat Sessions

**GET** `/chat-history/sessions`

Get all chat sessions for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "session_name": "Legal Consultation - Property Law",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

#### 3. Get Chat Session with History

**GET** `/chat-history/sessions/{session_id}`

Get a specific chat session with its message history.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "session_name": "Legal Consultation - Property Law",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "messages": [
    {
      "id": 1,
      "message_role": "user",
      "message_content": "What are the property laws in Sri Lanka?",
      "message_metadata": null,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "message_role": "assistant",
      "message_content": "In Sri Lanka, property laws are governed by...",
      "message_metadata": null,
      "created_at": "2025-01-01T00:01:00Z"
    }
  ]
}
```

#### 4. Add Message to Session

**POST** `/chat-history/sessions/{session_id}/messages`

Add a message to a chat session.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "role": "user",
  "content": "What are the property laws in Sri Lanka?",
  "metadata": {
    "query_type": "legal_question"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "message_role": "user",
  "message_content": "What are the property laws in Sri Lanka?",
  "message_metadata": "{\"query_type\": \"legal_question\"}",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message",
  "success": false
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid or missing token)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Password Requirements

Passwords must meet the following criteria:
- At least 8 characters long
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Email Verification

- Verification codes are 6 digits long
- Codes expire after 15 minutes
- Codes can be resent if needed

## Password Reset

- Reset tokens are valid for 1 hour
- Reset links are sent via email
- Tokens can only be used once

## Rate Limiting

The API implements rate limiting:
- 60 requests per minute per IP
- 1000 requests per hour per IP

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes
- Email verification required for new accounts
- Password reset tokens are single-use
- User activity is logged for security auditing
