import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to individual components
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_SSL = os.getenv("POSTGRES_SSL", "require")
    
    DATABASE_URL = f"postgresql+pg8000://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Ensure the URL uses the pg8000 driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

# Remove SSL parameters as pg8000 handles SSL automatically for most providers
if "?sslmode=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?sslmode=")[0]

# Create SQLAlchemy engine with improved connection pooling and error handling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Verify connections before using them
    pool_recycle=300,          # Recycle connections after 5 minutes
    pool_size=5,               # Number of connections to maintain
    max_overflow=10,           # Maximum overflow connections
    pool_timeout=30,           # Timeout for getting connection from pool
    connect_args={
        "timeout": 10,         # Connection timeout in seconds
    },
    echo=False                 # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_url():
    """Get the database URL for testing purposes"""
    return DATABASE_URL

def get_engine():
    """Get database engine for testing with stress-test optimized settings"""
    from sqlalchemy.pool import QueuePool
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=30,
        max_overflow=50,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )

# Create Base class
Base = declarative_base()

# Metadata instance
metadata = MetaData()

# Dependency to get database session with error handling
def get_db():
    db = SessionLocal()
    try:
        # Test the connection before yielding
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"⚠️  Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Test database connection
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()