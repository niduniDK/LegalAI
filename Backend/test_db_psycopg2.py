#!/usr/bin/env python3
"""
Test database connection with psycopg2 driver
"""
import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_with_psycopg2():
    """Test connection using psycopg2"""
    print("🔧 Testing with psycopg2 driver...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the URL to extract components
        parsed = urlparse(DATABASE_URL)
        
        connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:],  # Remove leading slash
            'sslmode': 'require',
            'connect_timeout': 15
        }
        
        print(f"🔗 Connecting to {parsed.hostname}:{parsed.port}...")
        print(f"👤 User: {parsed.username}")
        print(f"🗄️  Database: {parsed.path[1:]}")
        
        start_time = time.time()
        
        # Attempt connection
        conn = psycopg2.connect(**connection_params)
        connection_time = time.time() - start_time
        
        print(f"✅ Connection successful! ({connection_time:.2f}s)")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"🐘 PostgreSQL version: {version}")
        
        # Check for tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("📝 No tables found. Database is empty.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"❌ psycopg2 connection failed after {connection_time:.2f}s")
        print(f"💥 Error: {str(e)}")
        return False

def test_with_sqlalchemy_psycopg2():
    """Test with SQLAlchemy using psycopg2"""
    print("\n🔧 Testing with SQLAlchemy + psycopg2...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Convert URL to use psycopg2
        if DATABASE_URL.startswith("postgresql://"):
            psycopg2_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        else:
            psycopg2_url = DATABASE_URL.replace("postgresql+pg8000://", "postgresql+psycopg2://", 1)
        
        print(f"🔗 Using URL: {psycopg2_url}")
        
        engine = create_engine(
            psycopg2_url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 15}
        )
        
        start_time = time.time()
        
        with engine.connect() as connection:
            connection_time = time.time() - start_time
            print(f"✅ SQLAlchemy connection successful! ({connection_time:.2f}s)")
            
            # Test query
            result = connection.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"🗄️  Connected to database: {db_info[0]}")
            print(f"👤 Connected as user: {db_info[1]}")
            
        return True
        
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"❌ SQLAlchemy connection failed after {connection_time:.2f}s")
        print(f"💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing database connection with different drivers...\n")
    print(f"📍 Database URL: {DATABASE_URL}\n")
    
    # Test with direct psycopg2
    success1 = test_with_psycopg2()
    
    # Test with SQLAlchemy + psycopg2
    success2 = test_with_sqlalchemy_psycopg2()
    
    if success1 or success2:
        print("\n🎉 At least one connection method worked!")
        if success2:
            print("💡 Consider switching to psycopg2 driver in your connection.py")
    else:
        print("\n💔 All connection attempts failed.")
        print("💡 Please check:")
        print("   - Database credentials")
        print("   - Network connectivity")
        print("   - Neon database status")
