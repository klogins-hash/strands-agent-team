#!/usr/bin/env python3
"""
Setup Scaleway Serverless SQL Database for Agent System
Creates tables for agent decisions, projects, and deployments
"""

import psycopg2
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://d1e1b218-20fe-4a7c-b7eb-1fb2c72f1b00.pg.sdb.fr-par.scw.cloud:5432/agent-db?sslmode=require&user=d1e1b218-20fe-4a7c-b7eb-1fb2c72f1b00&password=")

def setup_database():
    """Create tables for agent system"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔧 Setting up agent database schema...")
        
        # Agent decisions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(50) NOT NULL,
                decision TEXT NOT NULL,
                reasoning TEXT,
                outcome TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_id VARCHAR(255)
            )
        """)
        
        # Projects table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_projects (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(255) UNIQUE NOT NULL,
                created_by VARCHAR(50) NOT NULL,
                description TEXT,
                metadata JSONB,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Deployments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES agent_projects(id),
                snapshot_id VARCHAR(50),
                environment VARCHAR(50) DEFAULT 'production',
                deployed_by VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                deployment_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent metrics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(50) NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                labels JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_decisions_agent ON agent_decisions(agent_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_decisions_timestamp ON agent_decisions(timestamp)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_projects_name ON agent_projects(project_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_deployments_project ON deployments(project_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_metrics_name ON agent_metrics(agent_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp)")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Database schema created successfully!")
        print("\n📊 Tables created:")
        print("   - agent_decisions (log agent reasoning)")
        print("   - agent_projects (track projects)")
        print("   - deployments (deployment history)")
        print("   - agent_metrics (performance data)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        print(f"✅ Connected to Scaleway Serverless SQL")
        print(f"📋 Version: {version.split(',')[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Scaleway Serverless SQL Database Setup")
    print("=" * 50)
    
    if test_connection():
        setup_database()
        print("\n🎉 Your agent system is now serverless-ready!")
    else:
        print("\n⚠️  Please wait for database to finish creating (2-3 minutes)")
        print("   Then run: python3 setup_serverless_db.py")
