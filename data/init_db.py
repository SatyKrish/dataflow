#!/usr/bin/env python3
"""
Database initialization script for Multi-Agent Research System
"""

import os
import asyncio
import asyncpg
from pathlib import Path
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'dataflow_agents'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

async def init_database():
    """Initialize the database with schema and basic data"""
    
    # First connect to default postgres database to create our database if needed
    default_config = DB_CONFIG.copy()
    default_config['database'] = 'postgres'
    
    try:
        conn = await asyncpg.connect(**default_config)
        
        # Check if database exists
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            DB_CONFIG['database']
        )
        
        if not db_exists:
            print(f"Creating database {DB_CONFIG['database']}...")
            await conn.execute(f'CREATE DATABASE "{DB_CONFIG["database"]}"')
            print(f"Database {DB_CONFIG['database']} created successfully")
        else:
            print(f"Database {DB_CONFIG['database']} already exists")
            
        await conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
    # Now connect to our target database and run schema
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # Read and execute schema
        schema_path = Path(__file__).parent / 'schema.sql'
        if schema_path.exists():
            print("Executing schema.sql...")
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            await conn.execute(schema_sql)
            print("Schema executed successfully")
        else:
            print(f"Warning: schema.sql not found at {schema_path}")
        
        # Insert basic test data
        print("Inserting test data...")
        test_user_id = await conn.fetchval("""
            INSERT INTO users (email, name) 
            VALUES ('test@example.com', 'Test User')
            ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
            RETURNING user_id
        """)
        
        print(f"Test user created/updated with ID: {test_user_id}")
        
        await conn.close()
        print("Database initialization completed successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

async def check_connection() -> bool:
    """Check if database connection is working"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        return result == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Multi-Agent Research System - Database Initialization")
    print("=" * 50)
    print(f"Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    success = asyncio.run(init_database())
    
    if success:
        print("\n✓ Database initialization completed successfully")
        
        # Test connection
        if asyncio.run(check_connection()):
            print("✓ Database connection test passed")
        else:
            print("✗ Database connection test failed")
    else:
        print("\n✗ Database initialization failed")
        exit(1) 