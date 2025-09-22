#!/usr/bin/env python3
"""
Database connection test with proper timeout handling
"""
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connection_worker():
    """Worker function to test database connection"""
    from database.connection import DATABASE_URL
    from sqlalchemy import create_engine, text
    
    # Create engine with minimal configuration
    engine = create_engine(DATABASE_URL, echo=False)
    
    with engine.connect() as connection:
        # Test basic query
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        return {
            'success': True,
            'version': version,
            'error': None
        }

def test_tables_worker():
    """Worker function to check tables"""
    from database.connection import DATABASE_URL
    from sqlalchemy import create_engine, text
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = result.fetchall()
        return [table[0] for table in tables]

def main():
    """Main test function with timeout"""
    from database.connection import DATABASE_URL
    
    print("🚀 Starting database connection test...\n")
    print("🔗 Attempting to connect to database...")
    print(f"📍 Database URL: {DATABASE_URL}")
    print("⏱️  Testing connection (timeout: 30 seconds)...")
    
    start_time = time.time()
    
    try:
        # Test connection with timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(test_connection_worker)
            
            # Show progress while waiting
            dots = 0
            while not future.done():
                elapsed = time.time() - start_time
                if elapsed > 30:  # 30 second timeout
                    print(f"\n⏰ Connection timeout after {elapsed:.1f} seconds")
                    future.cancel()
                    break
                
                # Show progress dots
                print(f"\r⏳ Connecting{'.' * (dots % 4):<4} ({elapsed:.1f}s)", end='', flush=True)
                dots += 1
                time.sleep(0.5)
            
            if future.done() and not future.cancelled():
                result = future.result(timeout=1)
                connection_time = time.time() - start_time
                print(f"\n✅ Database connection successful! ({connection_time:.2f}s)")
                print(f"🐘 PostgreSQL version: {result['version']}")
                
                # Test tables
                print("📋 Checking for existing tables...")
                try:
                    with ThreadPoolExecutor(max_workers=1) as table_executor:
                        table_future = table_executor.submit(test_tables_worker)
                        tables = table_future.result(timeout=10)
                        
                        if tables:
                            print(f"📊 Found {len(tables)} tables:")
                            for table in tables:
                                print(f"  - {table}")
                        else:
                            print("📝 No tables found. Database is empty.")
                except Exception as e:
                    print(f"⚠️  Could not check tables: {str(e)}")
                
                print("✅ All tests completed successfully!")
                return True
            else:
                print(f"\n❌ Connection failed or timed out")
                return False
                
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"\n❌ Database connection failed after {connection_time:.2f}s")
        print(f"💥 Error: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide helpful suggestions
        error_str = str(e).lower()
        if "timeout" in error_str or "timed out" in error_str:
            print("\n💡 Suggestions:")
            print("   - The Neon database might be in sleep mode (can take 30+ seconds to wake up)")
            print("   - Check your internet connection")
            print("   - Try again in a few minutes")
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
    try:
        success = main()
        print(f"\n{'🎉 Test completed successfully!' if success else '💔 Test failed.'}")
    except KeyboardInterrupt:
        print(f"\n🛑 Test interrupted by user")
        sys.exit(1)
