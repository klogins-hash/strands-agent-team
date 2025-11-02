"""
Scaleway Integration for Agent System
Automatic use of Scaleway services by agents
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ScalewayStorage:
    """Object Storage integration for agent artifacts"""
    
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET", "agent-projects")
        self.endpoint = os.getenv("S3_ENDPOINT", "s3.fr-par.scw.cloud")
    
    def upload_project(self, project_path: Path, project_name: str):
        """Upload completed project to Object Storage"""
        try:
            s3_path = f"s3://{self.bucket}/{project_name}/"
            
            result = subprocess.run(
                [
                    "s3cmd", "sync",
                    str(project_path) + "/",
                    s3_path,
                    "--host", self.endpoint,
                    "--host-bucket", f"%(bucket)s.{self.endpoint}"
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Uploaded to {s3_path}"
            else:
                return f"⚠️  Upload failed: {result.stderr}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def download_project(self, project_name: str, local_path: Path):
        """Download project from Object Storage"""
        try:
            s3_path = f"s3://{self.bucket}/{project_name}/"
            
            result = subprocess.run(
                [
                    "s3cmd", "sync",
                    s3_path,
                    str(local_path) + "/",
                    "--host", self.endpoint
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Downloaded from {s3_path}"
            else:
                return f"⚠️  Download failed: {result.stderr}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def list_projects(self):
        """List all projects in storage"""
        try:
            result = subprocess.run(
                [
                    "s3cmd", "ls",
                    f"s3://{self.bucket}/",
                    "--host", self.endpoint
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"⚠️  List failed: {result.stderr}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class ScalewayDatabase:
    """PostgreSQL integration for agent metadata"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.enabled = bool(self.db_url)
    
    def store_project_metadata(self, project_name: str, metadata: dict):
        """Store project metadata in PostgreSQL"""
        if not self.enabled:
            return "⚠️  Database not configured"
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agent_projects (
                    id SERIAL PRIMARY KEY,
                    project_name VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP,
                    metadata JSONB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert or update
            cur.execute("""
                INSERT INTO agent_projects (project_name, created_at, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (project_name)
                DO UPDATE SET metadata = %s, updated_at = CURRENT_TIMESTAMP
            """, (project_name, datetime.now(), json.dumps(metadata), json.dumps(metadata)))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return "✅ Metadata stored in PostgreSQL"
        except Exception as e:
            return f"❌ Database error: {str(e)}"
    
    def get_project_metadata(self, project_name: str):
        """Retrieve project metadata"""
        if not self.enabled:
            return None
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute(
                "SELECT metadata FROM agent_projects WHERE project_name = %s",
                (project_name,)
            )
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            return json.loads(result[0]) if result else None
        except Exception as e:
            return None


class ScalewayCache:
    """Redis integration for agent caching"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.enabled = bool(self.redis_url)
    
    def cache_model_response(self, key: str, response: str, ttl: int = 3600):
        """Cache model responses to save API calls"""
        if not self.enabled:
            return False
        
        try:
            import redis
            
            r = redis.from_url(self.redis_url)
            r.setex(key, ttl, response)
            return True
        except Exception as e:
            return False
    
    def get_cached_response(self, key: str):
        """Get cached model response"""
        if not self.enabled:
            return None
        
        try:
            import redis
            
            r = redis.from_url(self.redis_url)
            result = r.get(key)
            return result.decode() if result else None
        except Exception as e:
            return None


class ScalewayContainerRegistry:
    """Container Registry integration"""
    
    def __init__(self):
        self.registry = "rg.fr-par.scw.cloud/agent-builds"
    
    def push_image(self, project_name: str, version: str = "latest"):
        """Push Docker image to Scaleway registry"""
        try:
            image_name = f"{self.registry}/{project_name}:{version}"
            
            # Tag image
            subprocess.run(
                ["docker", "tag", project_name, image_name],
                capture_output=True
            )
            
            # Push image
            result = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Pushed to {image_name}"
            else:
                return f"⚠️  Push failed: {result.stderr}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def list_images(self):
        """List images in registry"""
        try:
            result = subprocess.run(
                ["scw", "registry", "image", "list"],
                capture_output=True,
                text=True
            )
            
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"


def create_scaleway_tools():
    """Create Scaleway integration tools for agents"""
    from strands import tool
    
    @tool
    def upload_to_storage(project_path: str, project_name: str) -> str:
        """Upload project to Scaleway Object Storage"""
        storage = ScalewayStorage()
        return storage.upload_project(Path(project_path), project_name)
    
    @tool
    def save_project_metadata(project_name: str, metadata: dict) -> str:
        """Save project metadata to Scaleway PostgreSQL"""
        db = ScalewayDatabase()
        return db.store_project_metadata(project_name, metadata)
    
    @tool
    def push_docker_image(project_name: str, version: str = "latest") -> str:
        """Push Docker image to Scaleway Container Registry"""
        registry = ScalewayContainerRegistry()
        return registry.push_image(project_name, version)
    
    return [upload_to_storage, save_project_metadata, push_docker_image]


# Auto-backup to Scaleway after project completion
class AutoBackup:
    """Automatically backup projects to Scaleway"""
    
    @staticmethod
    def backup_project(project_path: Path, project_name: str):
        """Backup project to all Scaleway services"""
        results = []
        
        # 1. Upload to Object Storage
        storage = ScalewayStorage()
        results.append(storage.upload_project(project_path, project_name))
        
        # 2. Save metadata to PostgreSQL
        db = ScalewayDatabase()
        metadata = {
            "name": project_name,
            "path": str(project_path),
            "backed_up_at": datetime.now().isoformat(),
            "files_count": len(list(project_path.rglob("*")))
        }
        results.append(db.store_project_metadata(project_name, metadata))
        
        return results
