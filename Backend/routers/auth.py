import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.connection import get_db
from database.models import User, UserActivityLog, ChatSession, ChatHistory, UserPreference
from schemas.auth import (
    UserCreate, UserLogin, UserVerify, UserResponse, UserUpdate,
    PasswordReset, PasswordResetConfirm, ChangePassword, Token, MessageResponse,
    ChatSessionCreate, ChatSessionResponse, ChatSessionWithHistory,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
)
from utils.auth import (
    verify_password, get_password_hash, create_access_token, verify_token,
    generate_verification_code, generate_reset_token, send_email,
    create_verification_email, create_password_reset_email
)

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    token = credentials.credentials
    email = verify_token(token)
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def log_user_activity(db: Session, user_email: str, activity_type: str, description: str, request: Request):
    """Log user activity."""
    try:
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        activity_log = UserActivityLog(
            user_email=user_email,
            activity_type=activity_type,
            activity_description=description,
            ip_address=client_ip,
            user_agent=user_agent
        )
        db.add(activity_log)
        db.commit()
    except Exception as e:
        print(f"Failed to log user activity: {e}")

@router.post("/register", response_model=MessageResponse)
async def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification code
    verification_code = generate_verification_code()
    verification_expires = datetime.utcnow() + timedelta(minutes=15)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        verification_code=verification_code,
        verification_code_expires=verification_expires
    )
    
    db.add(db_user)
    db.commit()
    
    # Send verification email
    subject, email_body = create_verification_email(user_data.email, verification_code)
    await send_email(user_data.email, subject, email_body, is_html=True)
    
    # Log activity
    log_user_activity(db, user_data.email, "register", "User registered", request)
    
    return MessageResponse(message="Registration successful. Please check your email for verification code.")

@router.post("/verify", response_model=MessageResponse)
async def verify_user(verify_data: UserVerify, request: Request, db: Session = Depends(get_db)):
    """Verify user email with verification code."""
    user = db.query(User).filter(User.email == verify_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    if not user.verification_code or user.verification_code != verify_data.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    if user.verification_code_expires and user.verification_code_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired"
        )
    
    # Verify user
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires = None
    db.commit()
    
    # Log activity
    log_user_activity(db, user.email, "verify", "Email verified", request)
    
    return MessageResponse(message="Email verified successfully")

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        # Log failed login attempt
        log_user_activity(db, login_data.email, "login_failed", "Failed login attempt", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please verify your email first."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Log successful login
    log_user_activity(db, user.email, "login", "Successful login", request)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(email_data: PasswordReset, request: Request, db: Session = Depends(get_db)):
    """Resend verification code."""
    user = db.query(User).filter(User.email == email_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    # Generate new verification code
    verification_code = generate_verification_code()
    verification_expires = datetime.utcnow() + timedelta(minutes=15)
    
    user.verification_code = verification_code
    user.verification_code_expires = verification_expires
    db.commit()
    
    # Send verification email
    subject, email_body = create_verification_email(user.email, verification_code)
    await send_email(user.email, subject, email_body, is_html=True)
    
    # Log activity
    log_user_activity(db, user.email, "resend_verification", "Verification code resent", request)
    
    return MessageResponse(message="Verification code sent successfully")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(reset_data: PasswordReset, request: Request, db: Session = Depends(get_db)):
    """Send password reset email."""
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    if not user:
        # Don't reveal that email doesn't exist
        return MessageResponse(message="If the email exists, a password reset link has been sent")
    
    # Generate reset token
    reset_token = generate_reset_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_password_token = reset_token
    user.reset_password_expires = reset_expires
    db.commit()
    
    # Send reset email
    subject, email_body = create_password_reset_email(user.email, reset_token)
    await send_email(user.email, subject, email_body, is_html=True)
    
    # Log activity
    log_user_activity(db, user.email, "password_reset_request", "Password reset requested", request)
    
    return MessageResponse(message="If the email exists, a password reset link has been sent")

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: PasswordResetConfirm, request: Request, db: Session = Depends(get_db)):
    """Reset password with reset token."""
    user = db.query(User).filter(
        User.reset_password_token == reset_data.token,
        User.reset_password_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()
    
    # Log activity
    log_user_activity(db, user.email, "password_reset", "Password reset successfully", request)
    
    return MessageResponse(message="Password reset successfully")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information."""
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    db.commit()
    
    # Log activity
    log_user_activity(db, current_user.email, "profile_update", "Profile updated", request)
    
    return current_user

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log activity
    log_user_activity(db, current_user.email, "password_change", "Password changed", request)
    
    return MessageResponse(message="Password changed successfully")

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (mainly for logging purposes)."""
    # Log activity
    log_user_activity(db, current_user.email, "logout", "User logged out", request)
    
    return MessageResponse(message="Logged out successfully")

# User preferences endpoints
@router.get("/preferences", response_model=list[UserPreferenceResponse])
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_email == current_user.email).all()
    return preferences


@router.put("/preferences/{preference_key}", response_model=UserPreferenceResponse)
async def update_user_preference(
    preference_key: str,
    preference_data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preference."""
    preference = db.query(UserPreference).filter(
        UserPreference.user_email == current_user.email,
        UserPreference.preference_key == preference_key
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    preference.preference_value = preference_data.preference_value
    db.commit()
    return preference

@router.delete("/preferences/{preference_key}", response_model=MessageResponse)
async def delete_user_preference(
    preference_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user preference."""
    preference = db.query(UserPreference).filter(
        UserPreference.user_email == current_user.email,
        UserPreference.preference_key == preference_key
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    db.delete(preference)
    db.commit()
    return MessageResponse(message="Preference deleted successfully")
