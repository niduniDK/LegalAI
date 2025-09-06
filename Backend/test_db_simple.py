#!/usr/bin/env python3
"""
Simple database connection test script with timeout handling
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine, DATABASE_URL
from sqlalchemy import text

def test_connection():
    """Test database connection with timeout"""
    print(f"🔗 Attempting to connect to database...")
    print(f"📍 Database URL: {DATABASE_URL}")
    print(f"⏱️  Testing connection (max 15 seconds)...")
    
    try:
        start_time = time.time()
        
        # Create engine with shorter timeout for testing
        from sqlalchemy import create_engine
        test_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=15,  # Pool timeout
            echo=False
        )
        
        with test_engine.connect() as connection:
            connection_time = time.time() - start_time
            print(f"✅ Database connection successful! ({connection_time:.2f}s)")
            
            # Test basic query
            print("🔍 Testing basic query...")
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"🐘 PostgreSQL version: {version}")
            
            # Test if tables exist
            print("📋 Checking for existing tables...")
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"📊 Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("📝 No tables found. Database is empty.")
                
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"❌ Database connection failed after {connection_time:.2f}s")
        print(f"💥 Error: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide helpful suggestions based on common errors
        error_str = str(e).lower()
        if "timeout" in error_str or "timed out" in error_str:
            print("\n💡 Suggestions:")
            print("   - Check your internet connection")
            print("   - Verify the database server is running")
            print("   - The Neon database might be in sleep mode (takes time to wake up)")
        elif "authentication" in error_str or "password" in error_str:
            print("\n💡 Suggestions:")
            print("   - Check your database credentials in .env file")
            print("   - Verify username and password are correct")
        elif "host" in error_str or "resolve" in error_str:
            print("\n💡 Suggestions:")
            print("   - Check the database host URL")
            print("   - Verify DNS resolution")
        
        return False

if __name__ == "__main__":
    print("🚀 Starting database connection test...\n")
    success = test_connection()
    print(f"\n{'🎉 Test completed successfully!' if success else '💔 Test failed.'}")
