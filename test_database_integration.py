#!/usr/bin/env python3
"""
Test Scaleway Database Integration with Agent System
"""

import psycopg2
import json
from datetime import datetime

# Database connection
DATABASE_URL = 'postgresql://agent_user:Agent_Password_123@51.159.25.151:16563/agent_db?sslmode=require'

class AgentDatabase:
    """Database integration for agent system"""
    
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
    
    def log_decision(self, agent_name, decision, reasoning, outcome=None):
        """Log an agent decision"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO agent_decisions (agent_name, decision, reasoning, outcome)
            VALUES (%s, %s, %s, %s)
        """, (agent_name, decision, reasoning, outcome))
        self.conn.commit()
    
    def save_project(self, project_name, created_by, description=None, metadata=None):
        """Save project metadata"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO agent_projects (project_name, created_by, description, metadata)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (project_name) DO UPDATE SET
                description = EXCLUDED.description,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (project_name, created_by, description, json.dumps(metadata or {})))
        self.conn.commit()
    
    def log_deployment(self, project_name, snapshot_id, environment, deployed_by, status='active'):
        """Log deployment"""
        cur = self.conn.cursor()
        # Get project ID
        cur.execute("SELECT id FROM agent_projects WHERE project_name = %s", (project_name,))
        result = cur.fetchone()
        if result:
            project_id = result[0]
            cur.execute("""
                INSERT INTO deployments (project_id, snapshot_id, environment, deployed_by, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (project_id, snapshot_id, environment, deployed_by, status))
            self.conn.commit()
    
    def log_metric(self, agent_name, metric_name, value, labels=None):
        """Log agent metric"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO agent_metrics (agent_name, metric_name, metric_value, labels)
            VALUES (%s, %s, %s, %s)
        """, (agent_name, metric_name, value, json.dumps(labels or {})))
        self.conn.commit()
    
    def get_recent_decisions(self, limit=10):
        """Get recent agent decisions"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT agent_name, decision, reasoning, timestamp 
            FROM agent_decisions 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    
    def get_project_stats(self):
        """Get project statistics"""
        cur = self.conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM agent_projects")
        project_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM agent_decisions")
        decision_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM deployments")
        deployment_count = cur.fetchone()[0]
        
        return {
            'projects': project_count,
            'decisions': decision_count,
            'deployments': deployment_count
        }

def test_integration():
    """Test the database integration"""
    print("🚀 Testing Scaleway Database Integration")
    print("=" * 50)
    
    db = AgentDatabase()
    
    # Test logging decisions
    print("\n📝 Testing decision logging...")
    db.log_decision("architect", "use_fastapi", "Better async support for APIs")
    db.log_decision("coder", "postgresql_db", "Scaleway managed PostgreSQL for reliability")
    db.log_decision("devops", "docker_deployment", "Containerize for easy deployment")
    
    # Test saving projects
    print("\n💾 Testing project metadata...")
    db.save_project(
        "todo-api", 
        "agent_team",
        "REST API for todo management",
        {"tech_stack": ["FastAPI", "PostgreSQL", "Docker"], "endpoints": 5}
    )
    
    # Test logging deployments
    print("\n🚀 Testing deployment logging...")
    db.log_deployment("todo-api", "snapshot_001", "production", "devops_agent")
    
    # Test metrics
    print("\n📊 Testing metrics logging...")
    db.log_metric("coder", "build_time", 45.2, {"project": "todo-api"})
    db.log_metric("architect", "planning_time", 12.5, {"project": "todo-api"})
    
    # Get statistics
    print("\n📈 Database Statistics:")
    stats = db.get_project_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Show recent decisions
    print("\n🤖 Recent Agent Decisions:")
    decisions = db.get_recent_decisions(5)
    for agent, decision, reasoning, timestamp in decisions:
        print(f"   {agent}: {decision}")
        print(f"      → {reasoning}")
    
    print("\n✅ Database integration test complete!")
    print("🎉 Your agent system is now connected to Scaleway PostgreSQL!")

if __name__ == "__main__":
    test_integration()
