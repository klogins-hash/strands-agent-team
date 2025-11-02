"""
Agent-Centric State Management System
Replaces traditional GitOps with agent-optimized state tracking

Key Principles:
1. State snapshots, not commits
2. Automatic rollback capability
3. Agent decision history
4. Continuous deployment (no approval gates)
5. Self-healing on errors
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

class AgentStateManager:
    """
    Manages project state for autonomous agents
    No Git, no commits, no human concepts - just state snapshots
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / ".agent_state"
        self.state_dir.mkdir(exist_ok=True)
        
        self.current_state_file = self.state_dir / "current.json"
        self.snapshots_dir = self.state_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        
    def capture_state(self, agent_name: str, action: str, metadata: dict = None):
        """
        Capture current project state
        Agents call this after making changes
        """
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate project hash (for change detection)
        project_hash = self._calculate_project_hash()
        
        state = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "project_hash": project_hash,
            "metadata": metadata or {},
            "files": self._list_project_files()
        }
        
        # Save snapshot
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        snapshot_file.write_text(json.dumps(state, indent=2))
        
        # Update current state
        self.current_state_file.write_text(json.dumps(state, indent=2))
        
        return snapshot_id
    
    def get_current_state(self):
        """Get current project state"""
        if self.current_state_file.exists():
            return json.loads(self.current_state_file.read_text())
        return None
    
    def list_snapshots(self, limit: int = 10):
        """List recent snapshots"""
        snapshots = []
        for snapshot_file in sorted(self.snapshots_dir.glob("*.json"), reverse=True)[:limit]:
            data = json.loads(snapshot_file.read_text())
            snapshots.append({
                "id": data["snapshot_id"],
                "timestamp": data["timestamp"],
                "agent": data["agent"],
                "action": data["action"]
            })
        return snapshots
    
    def rollback_to_snapshot(self, snapshot_id: str):
        """
        Rollback to a previous snapshot
        Agents can decide to rollback if something breaks
        """
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        if not snapshot_file.exists():
            return f"❌ Snapshot {snapshot_id} not found"
        
        # Load snapshot
        snapshot = json.loads(snapshot_file.read_text())
        
        # Create backup of current state
        self.capture_state("system", "pre_rollback_backup")
        
        # Update current state
        self.current_state_file.write_text(json.dumps(snapshot, indent=2))
        
        return f"✅ Rolled back to {snapshot_id}"
    
    def get_agent_history(self, agent_name: str = None):
        """Get history of agent actions"""
        history = []
        for snapshot_file in sorted(self.snapshots_dir.glob("*.json"), reverse=True):
            data = json.loads(snapshot_file.read_text())
            if agent_name is None or data["agent"] == agent_name:
                history.append({
                    "snapshot_id": data["snapshot_id"],
                    "timestamp": data["timestamp"],
                    "agent": data["agent"],
                    "action": data["action"]
                })
        return history
    
    def detect_changes_since(self, snapshot_id: str):
        """Detect what changed since a snapshot"""
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        if not snapshot_file.exists():
            return None
        
        old_state = json.loads(snapshot_file.read_text())
        current_state = self.get_current_state()
        
        if not current_state:
            return None
        
        old_files = set(old_state.get("files", []))
        current_files = set(current_state.get("files", []))
        
        return {
            "added": list(current_files - old_files),
            "removed": list(old_files - current_files),
            "hash_changed": old_state["project_hash"] != current_state["project_hash"]
        }
    
    def auto_cleanup(self, keep_last: int = 50):
        """Automatically cleanup old snapshots"""
        snapshots = sorted(self.snapshots_dir.glob("*.json"), reverse=True)
        for snapshot in snapshots[keep_last:]:
            snapshot.unlink()
        return f"✅ Cleaned up {len(snapshots) - keep_last} old snapshots"
    
    def _calculate_project_hash(self):
        """Calculate hash of entire project state"""
        hasher = hashlib.sha256()
        
        # Hash all files in project (excluding .agent_state)
        for file_path in sorted(self.project_path.rglob("*")):
            if file_path.is_file() and ".agent_state" not in str(file_path):
                try:
                    hasher.update(file_path.read_bytes())
                except:
                    pass
        
        return hasher.hexdigest()[:16]
    
    def _list_project_files(self):
        """List all files in project"""
        files = []
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and ".agent_state" not in str(file_path):
                rel_path = file_path.relative_to(self.project_path)
                files.append(str(rel_path))
        return sorted(files)


class AgentDecisionLog:
    """
    Log agent decisions and reasoning
    Helps agents learn from past decisions
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.log_file = self.project_path / ".agent_state" / "decisions.jsonl"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_decision(self, agent_name: str, decision: str, reasoning: str, outcome: str = None):
        """Log an agent decision"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "decision": decision,
            "reasoning": reasoning,
            "outcome": outcome
        }
        
        # Append to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_recent_decisions(self, limit: int = 20):
        """Get recent decisions"""
        if not self.log_file.exists():
            return []
        
        decisions = []
        with open(self.log_file, "r") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                decisions.append(json.loads(line))
        
        return list(reversed(decisions))
    
    def get_decisions_by_agent(self, agent_name: str):
        """Get all decisions by a specific agent"""
        if not self.log_file.exists():
            return []
        
        decisions = []
        with open(self.log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                if entry["agent"] == agent_name:
                    decisions.append(entry)
        
        return decisions


class ContinuousDeployment:
    """
    Continuous deployment for agents
    No approval gates - agents deploy when ready
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.deploy_log = self.project_path / ".agent_state" / "deployments.json"
        self.deploy_log.parent.mkdir(exist_ok=True)
    
    def deploy(self, environment: str, snapshot_id: str, agent_name: str):
        """Deploy a snapshot to an environment"""
        deployment = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "snapshot_id": snapshot_id,
            "deployed_by": agent_name,
            "status": "active"
        }
        
        # Load existing deployments
        deployments = []
        if self.deploy_log.exists():
            deployments = json.loads(self.deploy_log.read_text())
        
        # Add new deployment
        deployments.append(deployment)
        
        # Save
        self.deploy_log.write_text(json.dumps(deployments, indent=2))
        
        return deployment["id"]
    
    def get_active_deployment(self, environment: str):
        """Get currently active deployment for an environment"""
        if not self.deploy_log.exists():
            return None
        
        deployments = json.loads(self.deploy_log.read_text())
        
        # Find most recent active deployment for environment
        for deployment in reversed(deployments):
            if deployment["environment"] == environment and deployment["status"] == "active":
                return deployment
        
        return None
    
    def mark_failed(self, deployment_id: str):
        """Mark a deployment as failed (for auto-rollback)"""
        if not self.deploy_log.exists():
            return
        
        deployments = json.loads(self.deploy_log.read_text())
        
        for deployment in deployments:
            if deployment["id"] == deployment_id:
                deployment["status"] = "failed"
                break
        
        self.deploy_log.write_text(json.dumps(deployments, indent=2))


# Integration with agent tools
def create_state_tools():
    """Create state management tools for agents"""
    from strands import tool
    
    @tool
    def capture_snapshot(project_path: str, agent_name: str, action: str) -> str:
        """Capture current project state after making changes"""
        state_mgr = AgentStateManager(Path(project_path))
        snapshot_id = state_mgr.capture_state(agent_name, action)
        return f"✅ Captured snapshot: {snapshot_id}"
    
    @tool
    def get_project_state(project_path: str) -> str:
        """Get current project state"""
        state_mgr = AgentStateManager(Path(project_path))
        state = state_mgr.get_current_state()
        return json.dumps(state, indent=2) if state else "No state captured yet"
    
    @tool
    def rollback_project(project_path: str, snapshot_id: str) -> str:
        """Rollback project to a previous snapshot"""
        state_mgr = AgentStateManager(Path(project_path))
        return state_mgr.rollback_to_snapshot(snapshot_id)
    
    @tool
    def log_agent_decision(project_path: str, agent_name: str, decision: str, reasoning: str) -> str:
        """Log an agent decision for future reference"""
        decision_log = AgentDecisionLog(Path(project_path))
        decision_log.log_decision(agent_name, decision, reasoning)
        return "✅ Decision logged"
    
    @tool
    def deploy_snapshot(project_path: str, snapshot_id: str, environment: str, agent_name: str) -> str:
        """Deploy a snapshot to an environment"""
        cd = ContinuousDeployment(Path(project_path))
        deployment_id = cd.deploy(environment, snapshot_id, agent_name)
        return f"✅ Deployed: {deployment_id}"
    
    return [capture_snapshot, get_project_state, rollback_project, log_agent_decision, deploy_snapshot]
