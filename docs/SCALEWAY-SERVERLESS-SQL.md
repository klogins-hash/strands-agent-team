# Scaleway Serverless SQL Database Guide

## Overview

Scaleway Serverless SQL (SDB-SQL) provides PostgreSQL databases that scale to zero when not in use, perfect for agent workloads.

## Key Features

- ✅ **True Serverless**: Scales from 0 to N CPU units automatically
- ✅ **Pay-per-use**: Only pay for CPU time when active
- ✅ **PostgreSQL 16**: Full PostgreSQL features including JSONB
- ✅ **Managed**: No maintenance, automatic backups
- ✅ **Fast Startup**: Scales up in seconds
- ✅ **Secure**: SSL required, IAM integration

## Quick Start

### 1. Create Database

```bash
scw sdb-sql database create \
  name=agent-db \
  cpu-min=0 \
  cpu-max=2 \
  region=fr-par
```

### 2. Check Status

```bash
scw sdb-sql database get <database-id>
```

### 3. Start Database (if needed)

```bash
scw sdb-sql database update <database-id> cpu-min=1 cpu-max=2
```

## Authentication

Scaleway Serverless SQL uses **IAM-based authentication**:

### Connection String Format

```
postgres://<database-id>:<scaleway-secret-key>@<endpoint>/<database-name>?sslmode=require
```

### Example

```bash
# Get your database details
DATABASE_ID=$(scw sdb-sql database list -o json | jq -r '.[0].id')
ENDPOINT=$(scw sdb-sql database get $DATABASE_ID -o json | jq -r '.endpoint')
SECRET_KEY=$(scw config get secret-key)

# Connection string
DATABASE_URL="postgres://${DATABASE_ID}:${SECRET_KEY}@${ENDPOINT#postgres://}"
```

## Environment Setup

```bash
# Add to ~/.bashrc
export DATABASE_URL="postgres://d1e1b218-20fe-4a7c-b7eb-1fb2c72f1b00:a8236888-6261-4b2b-b717-6cd339e907bf@d1e1b218-20fe-4a7c-b7eb-1fb2c72f1b00.pg.sdb.fr-par.scw.cloud:5432/agent-db?sslmode=require"
```

## Python Integration

```python
import psycopg2
import os

# Connect to serverless SQL
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Example: Create table for agent decisions
cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_decisions (
        id SERIAL PRIMARY KEY,
        agent_name VARCHAR(50) NOT NULL,
        decision TEXT NOT NULL,
        reasoning TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
```

## Agent Use Cases

### 1. Decision Logging
```sql
CREATE TABLE agent_decisions (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50),
    decision TEXT,
    reasoning TEXT,
    outcome TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Project Metadata
```sql
CREATE TABLE agent_projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) UNIQUE,
    created_by VARCHAR(50),
    metadata JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Performance Metrics
```sql
CREATE TABLE agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Cost Optimization

### Scaling Configuration
- **cpu-min=0**: Scales to zero when not used (no cost)
- **cpu-max=1**: Sufficient for most agent workloads
- **cpu-max=2**: For concurrent agent operations

### Example Configurations
```bash
# Development (scales to zero)
scw sdb-sql database create name=dev-db cpu-min=0 cpu-max=1

# Production (always ready)
scw sdb-sql database create name=prod-db cpu-min=1 cpu-max=2

# High-load (multiple agents)
scw sdb-sql database create name=busy-db cpu-min=2 cpu-max=4
```

## Monitoring

### Check Database Status
```bash
# Current CPU usage
scw sdb-sql database get <database-id> -o json | jq '.cpu_current'

# Database size (via SQL)
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('agent-db'));"
```

### Performance Queries
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';
```

## Best Practices for Agents

### 1. Connection Pooling
```python
from psycopg2 import pool

# Create connection pool for agents
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    1, 5,  # Min 1, Max 5 connections
    os.getenv('DATABASE_URL')
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)
```

### 2. Auto-retry Logic
```python
import time
from psycopg2 import OperationalError

def execute_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            conn.close()
            return True
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### 3. Batch Operations
```sql
-- Insert multiple decisions efficiently
INSERT INTO agent_decisions (agent_name, decision, reasoning) VALUES
    ('architect', 'use_fastapi', 'Better async support'),
    ('coder', 'jwt_auth', 'Stateless authentication'),
    ('tester', 'pytest', 'Most popular framework');
```

## Troubleshooting

### Common Issues

#### 1. "Database not started"
```bash
# Solution: Set cpu-min to 1
scw sdb-sql database update <database-id> cpu-min=1
```

#### 2. "Authentication failed"
```bash
# Solution: Use Scaleway secret key as password
SECRET_KEY=$(scw config get secret-key)
DATABASE_URL="postgres://$DATABASE_ID:$SECRET_KEY@$ENDPOINT"
```

#### 3. "Connection timeout"
```bash
# Solution: Database might be scaling up, wait a few seconds
# Or set cpu-min to 1 for always-on
```

## Backup and Restore

### Create Backup
```bash
scw sdb-sql backup export <database-id>
```

### Restore from Backup
```bash
scw sdb-sql database create \
  name=restored-db \
  cpu-min=0 \
  cpu-max=1 \
  from-backup-id=<backup-id>
```

## Integration with Agent System

The serverless SQL database integrates seamlessly with the agent system:

1. **State Management**: Store agent decisions and reasoning
2. **Project Tracking**: Metadata for all built projects
3. **Performance Metrics**: Track agent efficiency
4. **Learning Data**: Store outcomes for future improvements

## Example: Complete Agent Workflow

```python
class AgentDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.setup_tables()
    
    def log_decision(self, agent_name, decision, reasoning):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO agent_decisions (agent_name, decision, reasoning)
            VALUES (%s, %s, %s)
        """, (agent_name, decision, reasoning))
        self.conn.commit()
    
    def save_project(self, project_name, metadata):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO agent_projects (project_name, created_by, metadata)
            VALUES (%s, %s, %s)
            ON CONFLICT (project_name) DO UPDATE SET
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (project_name, 'agent_team', json.dumps(metadata)))
        self.conn.commit()
```

## Summary

Scaleway Serverless SQL is perfect for agent systems:
- ✅ Cost-effective (scales to zero)
- ✅ Fully managed
- ✅ PostgreSQL features
- ✅ IAM authentication
- ✅ Fast scaling
- ✅ Production ready

Your agent system now has a robust, serverless database backend! 🚀
