"""
Database initialization script for LegalAI

This script creates the database tables and sets up initial data.
Run this script after setting up your environment variables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine, test_connection
from database.models import Base

def create_tables():
    """Create all database tables."""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        return True
    except SQLAlchemyError as e:
        print(f"✗ Error creating tables: {e}")
        return False

def setup_database():
    """Set up the database with initial configuration."""
    try:
        with engine.connect() as connection:
            # Enable UUID extension if using PostgreSQL
            try:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
                connection.commit()
                print("✓ UUID extension enabled")
            except Exception as e:
                print(f"Note: UUID extension setup skipped: {e}")
            
            # Set timezone
            try:
                connection.execute(text("SET TIME ZONE 'UTC';"))
                connection.commit()
                print("✓ Timezone set to UTC")
            except Exception as e:
                print(f"Note: Timezone setup skipped: {e}")
        
        return True
    except SQLAlchemyError as e:
        print(f"✗ Error setting up database: {e}")
        return False

def main():
    """Main function to initialize the database."""
    print("=== LegalAI Database Initialization ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check database connection
    print("1. Testing database connection...")
    if not test_connection():
        print("✗ Database connection failed. Please check your environment variables.")
        return False
    
    # Setup database
    print("\n2. Setting up database configuration...")
    if not setup_database():
        print("✗ Database setup failed.")
        return False
    
    # Create tables
    print("\n3. Creating database tables...")
    if not create_tables():
        print("✗ Table creation failed.")
        return False
    
    print("\n=== Database initialization completed successfully! ===")
    print("\nNext steps:")
    print("1. Update your .env file with the correct database credentials")
    print("2. Start the FastAPI server: python main.py")
    print("3. Start the frontend: npm run dev")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
