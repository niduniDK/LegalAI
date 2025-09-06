#!/usr/bin/env python3
"""
Test database connection script
"""
import sys
import os
import signal
import time
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine, DATABASE_URL
from sqlalchemy import text

@contextmanager
def timeout(duration):
    """Context manager for timeout operations"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {duration} seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)

def test_connection():
    """Test database connection"""
    print(f"🔗 Attempting to connect to database...")
    print(f"📍 Database URL: {DATABASE_URL}")
    print(f"⏱️  Connection timeout: 10 seconds")
    
    try:
        # Test basic connection with timeout
        start_time = time.time()
        
        # For Windows, we'll use engine timeout instead of signal
        test_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
        
        with test_engine.connect() as connection:
        with test_engine.connect() as connection:
            connection_time = time.time() - start_time
            print(f"✅ Database connection successful! ({connection_time:.2f}s)")
            
            # Test basic query
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"🐘 PostgreSQL version: {version}")
            
            # Test if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"\n📋 Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n📋 No tables found. Database is empty.")
                
        return True
        
    except TimeoutError as e:
        print(f"⏰ Connection timeout: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Database connection failed:")
        print(f"💥 Error: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide helpful suggestions based on common errors
        error_str = str(e).lower()
        if "timeout" in error_str or "timed out" in error_str:
            print("\n💡 Suggestions:")
            print("   - Check your internet connection")
            print("   - Verify the database server is running")
            print("   - Try increasing the connection timeout")
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
    print(f"\n{'✅ Test completed successfully!' if success else '❌ Test failed.'}")
