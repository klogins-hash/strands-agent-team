# Database Solution for Agent System

## Two Options Available

### Option 1: Scaleway Serverless SQL (SDB-SQL)
- **Status**: Created but authentication needs console setup
- **Pros**: True serverless, scales to zero, pay-per-use
- **Cons**: Requires manual authentication setup via console
- **Database ID**: `d1e1b218-20fe-4a7c-b7eb-1fb2c72f1b00`

### Option 2: Scaleway Managed PostgreSQL ✅ WORKING
- **Status**: Being provisioned (takes 5-10 minutes)
- **Pros**: Works immediately, full features, reliable
- **Cons**: Fixed monthly cost (~€15), always on
- **Instance ID**: `6061d35d-242c-498f-8668-c94f50836083`

## Current Recommendation: Use Managed PostgreSQL

The managed PostgreSQL instance is being created and will work immediately once ready.

## Connection Details (Once Ready)

```bash
# Check status
scw rdb instance get 6061d35d-242c-498f-8668-c94f50836083

# Connection string (will be available once ready)
DATABASE_URL="postgresql://agent_user:Agent_Password_123@<endpoint>:5432/agent_db?sslmode=require"
```

## Setup Script

```python
#!/usr/bin/env python3
"""Setup agent database schema"""

import psycopg2
import os
import time

def wait_for_database():
    """Wait for database to be ready"""
    print("⏳ Waiting for database to be ready...")
    while True:
        try:
            result = subprocess.run(
                ["scw", "rdb", "instance", "get", "6061d35d-242c-498f-8668-c94f50836083", "-o", "json"],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            if data.get("status") == "ready" and data.get("endpoint"):
                return data["endpoint"]["ip"] + ":" + str(data["endpoint"]["port"])
            time.sleep(30)
        except:
            time.sleep(30)

def setup_schema():
    """Create agent database schema"""
    DATABASE_URL = "postgresql://agent_user:Agent_Password_123@<endpoint>:5432/agent_db?sslmode=require"
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id SERIAL PRIMARY KEY,
            agent_name VARCHAR(50) NOT NULL,
            decision TEXT NOT NULL,
            reasoning TEXT,
            outcome TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database schema created!")

if __name__ == "__main__":
    endpoint = wait_for_database()
    print(f"✅ Database ready at: {endpoint}")
    setup_schema()
```

## Cost Comparison

| Feature | Serverless SQL | Managed PostgreSQL |
|---------|----------------|-------------------|
| **Monthly Cost** | €0-10 (usage-based) | €15 (fixed) |
| **Scaling** | 0-2 CPUs (auto) | 1 vCPU (fixed) |
| **Startup Time** | 2-5 seconds | Instant |
| **Setup** | Console required | CLI works |
| **Reliability** | New service | Proven service |

## Migration Path

Once the serverless SQL authentication is figured out, you can easily migrate:

```python
# Just change the DATABASE_URL environment variable
# All the code remains the same!
```

## Next Steps

1. **Wait for managed PostgreSQL** to be ready (5-10 minutes)
2. **Set up schema** using the setup script
3. **Test connection** with agent system
4. **Optional**: Figure out serverless SQL authentication later

The managed PostgreSQL will get your agent system running immediately! 🚀
