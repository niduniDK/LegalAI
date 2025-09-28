import os
import secrets
import asyncio
import aiosmtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "3000"))

# Email settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "LegalAI")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_verification_code() -> str:
    """Generate a 6-digit verification code."""
    return f"{secrets.randbelow(1000000):06d}"

def generate_reset_token() -> str:
    """Generate a secure reset token."""
    return secrets.token_urlsafe(32)

async def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    """Send an email using aiosmtplib."""
    if not all([SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        print("Email configuration not complete. Email not sent.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email using aiosmtplib
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
        )
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def create_verification_email(email: str, code: str) -> tuple[str, str]:
    """Create verification email content."""
    subject = "Verify Your LegalAI Account"
    
    body = f"""
    Welcome to LegalAI!
    
    Please use the following verification code to complete your registration:
    
    Verification Code: {code}
    
    This code will expire in 15 minutes.
    
    If you didn't create an account with LegalAI, please ignore this email.
    
    Best regards,
    The LegalAI Team
    """
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
            .code {{ font-size: 24px; font-weight: bold; color: #007bff; text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 5px; margin: 20px 0; }}
            .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Welcome to LegalAI!</h2>
            </div>
            
            <p>Thank you for registering with LegalAI. Please use the following verification code to complete your registration:</p>
            
            <div class="code">{code}</div>
            
            <p>This code will expire in 15 minutes for security reasons.</p>
            
            <p>If you didn't create an account with LegalAI, please ignore this email.</p>
            
            <div class="footer">
                <p>Best regards,<br>The LegalAI Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body

def create_password_reset_email(email: str, reset_token: str) -> tuple[str, str]:
    """Create password reset email content."""
    reset_link = f"{os.getenv('APP_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
    
    subject = "Reset Your LegalAI Password"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Password Reset Request</h2>
            </div>
            
            <p>We received a request to reset your LegalAI password. Click the button below to reset your password:</p>
            
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{reset_link}</p>
            
            <p>This link will expire in 1 hour for security reasons.</p>
            
            <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
            
            <div class="footer">
                <p>Best regards,<br>The LegalAI Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_body
