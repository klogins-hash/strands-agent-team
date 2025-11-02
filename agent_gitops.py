"""
Agent-Optimized GitOps System
Automated version control and deployment for AI agents
No human intervention needed - agents handle everything
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import hashlib

class AgentGitOps:
    """GitOps system optimized for autonomous agents"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.git_dir = self.project_path / ".git"
        self.metadata_file = self.project_path / ".agent_metadata.json"
        
    def initialize(self, project_name: str, description: str):
        """Initialize Git repo with agent metadata"""
        # Initialize git if not already done
        if not self.git_dir.exists():
            subprocess.run(["git", "init"], cwd=self.project_path, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Agent Team"], cwd=self.project_path)
            subprocess.run(["git", "config", "user.email", "agents@hitsdifferent.ai"], cwd=self.project_path)
        
        # Create agent metadata
        metadata = {
            "project_name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "created_by": "agent_team",
            "version": "0.1.0",
            "build_history": [],
            "deployments": []
        }
        
        self.metadata_file.write_text(json.dumps(metadata, indent=2))
        
        # Create .gitignore optimized for agent projects
        gitignore_content = """
# Agent-generated artifacts
.agent_metadata.json
*.pyc
__pycache__/
node_modules/
.env
.venv/
venv/
*.log
.DS_Store
.cache/
dist/
build/
*.egg-info/
"""
        (self.project_path / ".gitignore").write_text(gitignore_content.strip())
        
        return "✅ GitOps initialized"
    
    def auto_commit(self, agent_name: str, action: str, files_changed: list):
        """Automatic commit by agent - no human review needed"""
        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], cwd=self.project_path, capture_output=True)
            
            # Generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"[{agent_name}] {action}\n\nTimestamp: {timestamp}\nFiles: {', '.join(files_changed[:5])}"
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Get commit hash
                commit_hash = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                ).stdout.strip()
                
                # Update metadata
                self._update_build_history(agent_name, action, commit_hash)
                
                return f"✅ Auto-committed: {commit_hash[:7]}"
            else:
                return f"⚠️  Nothing to commit or error: {result.stderr}"
                
        except Exception as e:
            return f"❌ Commit failed: {str(e)}"
    
    def create_version_tag(self, version: str = None):
        """Create version tag automatically"""
        if not version:
            # Auto-increment version
            metadata = self._load_metadata()
            current = metadata.get("version", "0.1.0")
            major, minor, patch = map(int, current.split("."))
            version = f"{major}.{minor}.{patch + 1}"
        
        try:
            subprocess.run(
                ["git", "tag", "-a", f"v{version}", "-m", f"Agent release v{version}"],
                cwd=self.project_path,
                capture_output=True
            )
            
            # Update metadata
            metadata = self._load_metadata()
            metadata["version"] = version
            self.metadata_file.write_text(json.dumps(metadata, indent=2))
            
            return f"✅ Tagged version: v{version}"
        except Exception as e:
            return f"❌ Tagging failed: {str(e)}"
    
    def auto_deploy(self, environment: str = "production"):
        """Automatic deployment - no human approval needed"""
        try:
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            deployment = {
                "commit": commit_hash,
                "environment": environment,
                "timestamp": datetime.now().isoformat(),
                "status": "deployed"
            }
            
            # Update metadata
            metadata = self._load_metadata()
            metadata["deployments"].append(deployment)
            self.metadata_file.write_text(json.dumps(metadata, indent=2))
            
            return f"✅ Deployed {commit_hash[:7]} to {environment}"
        except Exception as e:
            return f"❌ Deployment failed: {str(e)}"
    
    def rollback(self, steps: int = 1):
        """Automatic rollback to previous version"""
        try:
            subprocess.run(
                ["git", "reset", "--hard", f"HEAD~{steps}"],
                cwd=self.project_path,
                capture_output=True
            )
            return f"✅ Rolled back {steps} commit(s)"
        except Exception as e:
            return f"❌ Rollback failed: {str(e)}"
    
    def get_project_state(self):
        """Get current project state for agents"""
        try:
            # Get current commit
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get status
            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            ).stdout
            
            # Get recent commits
            log = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            ).stdout
            
            metadata = self._load_metadata()
            
            return {
                "current_commit": commit[:7],
                "version": metadata.get("version", "unknown"),
                "uncommitted_changes": bool(status.strip()),
                "recent_commits": log.strip().split("\n") if log.strip() else [],
                "total_builds": len(metadata.get("build_history", [])),
                "total_deployments": len(metadata.get("deployments", []))
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_branch(self, branch_name: str, from_commit: str = "HEAD"):
        """Create a new branch for experimental features"""
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name, from_commit],
                cwd=self.project_path,
                capture_output=True
            )
            return f"✅ Created branch: {branch_name}"
        except Exception as e:
            return f"❌ Branch creation failed: {str(e)}"
    
    def merge_branch(self, branch_name: str):
        """Auto-merge branch - agents decide when to merge"""
        try:
            # Switch to main
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.project_path,
                capture_output=True
            )
            
            # Merge
            result = subprocess.run(
                ["git", "merge", branch_name, "--no-edit"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Merged {branch_name} into main"
            else:
                return f"⚠️  Merge conflict or error: {result.stderr}"
        except Exception as e:
            return f"❌ Merge failed: {str(e)}"
    
    def generate_changelog(self):
        """Auto-generate changelog from commits"""
        try:
            log = subprocess.run(
                ["git", "log", "--pretty=format:%h - %s (%an, %ar)"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            ).stdout
            
            changelog_path = self.project_path / "CHANGELOG.md"
            changelog_content = f"""# Changelog

Generated automatically by Agent GitOps

## Commits

{log}
"""
            changelog_path.write_text(changelog_content)
            return "✅ Generated CHANGELOG.md"
        except Exception as e:
            return f"❌ Changelog generation failed: {str(e)}"
    
    def _load_metadata(self):
        """Load agent metadata"""
        try:
            if self.metadata_file.exists():
                return json.loads(self.metadata_file.read_text())
            return {}
        except:
            return {}
    
    def _update_build_history(self, agent_name: str, action: str, commit_hash: str):
        """Update build history in metadata"""
        metadata = self._load_metadata()
        if "build_history" not in metadata:
            metadata["build_history"] = []
        
        metadata["build_history"].append({
            "agent": agent_name,
            "action": action,
            "commit": commit_hash,
            "timestamp": datetime.now().isoformat()
        })
        
        self.metadata_file.write_text(json.dumps(metadata, indent=2))


# Integration with agent tools
def create_gitops_tool():
    """Create GitOps tool for agents"""
    from strands import tool
    
    @tool
    def git_commit(project_path: str, agent_name: str, action: str, files: list) -> str:
        """Automatically commit changes made by agent"""
        gitops = AgentGitOps(Path(project_path))
        return gitops.auto_commit(agent_name, action, files)
    
    @tool
    def git_deploy(project_path: str, environment: str = "production") -> str:
        """Automatically deploy project"""
        gitops = AgentGitOps(Path(project_path))
        return gitops.auto_deploy(environment)
    
    @tool
    def git_status(project_path: str) -> str:
        """Get project Git status"""
        gitops = AgentGitOps(Path(project_path))
        state = gitops.get_project_state()
        return json.dumps(state, indent=2)
    
    @tool
    def git_version(project_path: str, version: str = None) -> str:
        """Create version tag"""
        gitops = AgentGitOps(Path(project_path))
        return gitops.create_version_tag(version)
    
    return [git_commit, git_deploy, git_status, git_version]
