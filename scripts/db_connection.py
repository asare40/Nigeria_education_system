# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:35:20 2025

@author: kings
"""

# scripts/db_connection.py
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('database.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create SQLAlchemy engine
def get_engine():
    """Create SQLAlchemy engine"""
    try:
        # Override config with environment variables if available
        host = os.getenv('DB_HOST', DB_CONFIG['host'])
        port = os.getenv('DB_PORT', str(DB_CONFIG['port']))
        database = os.getenv('DB_NAME', DB_CONFIG['database'])
        user = os.getenv('DB_USER', DB_CONFIG['user'])
        password = os.getenv('DB_PASSWORD', DB_CONFIG['password'])
        
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info(f"Successfully connected to database {database} on {host}:{port}")
        
        return engine
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Create session maker
def get_session():
    """Create a session"""
    engine = get_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    return None

# Base class for database models
Base = declarative_base()

# Test connection when script is run directly
if __name__ == "__main__":
    engine = get_engine()
    if engine:
        print("Database connection successful!")
    else:
        print("Failed to connect to database.")