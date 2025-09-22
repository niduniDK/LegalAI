from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    email = Column(String(255), primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(6), index=True)
    verification_code_expires = Column(DateTime)
    reset_password_token = Column(String(255), index=True)
    reset_password_expires = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("UserActivityLog", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    __table_args__ = (
        {"extend_existing": True}
    )

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    session_name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    message_role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    message_content = Column(Text, nullable=False)
    message_metadata = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    session = relationship("ChatSession", back_populates="messages")

class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(100), nullable=False)
    activity_description = Column(Text)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
