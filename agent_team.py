#!/usr/bin/env python3
"""
Autonomous Agent Team using Strands Framework
Build anything by just describing it - no code needed from you!
"""

import os
from strands import Agent, tool
from strands.models.litellm import LiteLLMModel
from pathlib import Path
import subprocess
import json
import requests
import time
from safety_config import is_path_safe, is_command_safe, AUTO_BACKUP_BEFORE_BUILD
from agent_gitops import AgentGitOps
import psycopg2

# Database integration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:Agent_Password_123@51.159.25.151:16563/agent_db?sslmode=require")

class AgentDatabase:
    """Database integration for agent system"""
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.enabled = True
        except Exception as e:
            print(f"⚠️ Database not available: {e}")
            self.enabled = False
    
    def log_decision(self, agent_name, decision, reasoning, outcome=None):
        """Log an agent decision"""
        if not self.enabled:
            return
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO agent_decisions (agent_name, decision, reasoning, outcome)
                VALUES (%s, %s, %s, %s)
            """, (agent_name, decision, reasoning, outcome))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Failed to log decision: {e}")
    
    def save_project(self, project_name, created_by, description=None, metadata=None):
        """Save project metadata"""
        if not self.enabled:
            return
        try:
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
        except Exception as e:
            print(f"⚠️ Failed to save project: {e}")

# OpenRouter API configuration (ZDR enabled on your account)
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
CACHE_FILE = Path("/root/.cache/openrouter_models.json")
CACHE_DURATION = 86400  # 24 hours in seconds

def load_cached_models():
    """Load models from cache if fresh"""
    try:
        if CACHE_FILE.exists():
            cache_data = json.loads(CACHE_FILE.read_text())
            cache_time = cache_data.get('timestamp', 0)
            
            # Check if cache is still fresh (less than 24 hours old)
            if time.time() - cache_time < CACHE_DURATION:
                print(f"📦 Using cached models (updated {int((time.time() - cache_time) / 3600)} hours ago)")
                return cache_data.get('models', {}), cache_data.get('all_models', [])
    except Exception as e:
        pass
    return None, None

def save_models_to_cache(model_dict, all_models):
    """Save models to cache"""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache_data = {
            'timestamp': time.time(),
            'models': model_dict,
            'all_models': all_models
        }
        CACHE_FILE.write_text(json.dumps(cache_data))
    except Exception as e:
        pass  # Silently fail if can't write cache

def fetch_available_models():
    """Fetch latest models from OpenRouter API with caching"""
    # Try to load from cache first
    cached_models, cached_all = load_cached_models()
    if cached_models is not None:
        return cached_models, cached_all
    
    # Cache miss or expired, fetch from API
    print("🔄 Fetching latest models from OpenRouter API...")
    try:
        response = requests.get(f"{OPENROUTER_API_URL}/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            
            # Build a dict of popular models for easy selection
            model_dict = {}
            for m in models:
                model_id = m['id']
                name = m.get('name', model_id)
                
                # Add shortcuts for popular models
                if 'claude-sonnet-4.5' in model_id:
                    model_dict['claude-sonnet'] = model_id
                elif 'claude-haiku-4.5' in model_id:
                    model_dict['claude-haiku'] = model_id
                elif 'gpt-5-pro' in model_id:
                    model_dict['gpt5-pro'] = model_id
                elif 'gpt-5-codex' in model_id:
                    model_dict['gpt5-codex'] = model_id
                elif 'deepseek-chat-v3.1' in model_id and 'free' not in model_id:
                    model_dict['deepseek'] = model_id
                elif 'qwen3-coder-plus' in model_id:
                    model_dict['qwen-coder'] = model_id
                elif 'gemini-2.5-flash' in model_id and 'preview' in model_id:
                    model_dict['gemini-flash'] = model_id
            
            # Save to cache
            save_models_to_cache(model_dict, models)
            print(f"✅ Fetched {len(models)} models from OpenRouter")
            
            return model_dict, models
        else:
            print(f"⚠️  Could not fetch models from OpenRouter (status {response.status_code})")
            return get_fallback_models(), []
    except Exception as e:
        print(f"⚠️  Error fetching models: {e}")
        return get_fallback_models(), []

def get_fallback_models():
    """Fallback models if API fetch fails"""
    return {
        "claude-sonnet": "anthropic/claude-sonnet-4.5",
        "claude-haiku": "anthropic/claude-haiku-4.5",
        "gpt5-pro": "openai/gpt-5-pro",
        "deepseek": "deepseek/deepseek-chat-v3.1",
        "qwen-coder": "qwen/qwen3-coder-plus",
        "gemini-flash": "google/gemini-2.5-flash-preview-09-2025",
    }

# Fetch models on startup (uses cache if available)
MODELS, ALL_MODELS = fetch_available_models()

def create_model(model_name="claude-sonnet", temperature=0.7):
    """Create model using OpenRouter"""
    model_id = MODELS.get(model_name, MODELS["claude-sonnet"])
    return LiteLLMModel(
        model_id=f"openrouter/{model_id}",
        client_args={
            "api_key": OPENROUTER_API_KEY,
            "base_url": "https://openrouter.ai/api/v1"
        },
        params={"temperature": temperature, "max_tokens": 4000}
    )

# Default model
model = create_model()

# Define tools for agents
@tool
def create_file(filepath: str, content: str) -> str:
    """Create a new file with the given content.
    
    Args:
        filepath: Path where the file should be created
        content: Content to write to the file
    
    Returns:
        Success message with filepath
    """
    try:
        # Safety check
        if not is_path_safe(filepath):
            return f"❌ Safety check failed: Cannot write to {filepath} (restricted path)"
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"✅ Created file: {filepath}"
    except Exception as e:
        return f"❌ Error creating file: {str(e)}"

@tool
def read_file(filepath: str) -> str:
    """Read the contents of a file.
    
    Args:
        filepath: Path to the file to read
    
    Returns:
        File contents
    """
    return Path(filepath).read_text()

@tool
def list_directory(dirpath: str) -> str:
    """List files and directories in the given path.
    
    Args:
        dirpath: Directory path to list
    
    Returns:
        List of files and directories
    """
    path = Path(dirpath)
    if not path.exists():
        return f"Directory {dirpath} does not exist"
    
    items = []
    for item in path.iterdir():
        item_type = "📁" if item.is_dir() else "📄"
        items.append(f"{item_type} {item.name}")
    
    return "\n".join(items)

@tool
def run_command(command: str, cwd: str = "/root/CascadeProjects") -> str:
    """Execute a shell command and return the output.
    
    Args:
        command: Shell command to execute
        cwd: Working directory for the command
    
    Returns:
        Command output or error message
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Exit code: {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out after 30 seconds"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@tool
def create_docker_compose(project_path: str, services: str) -> str:
    """Create a docker-compose.yml file for the project.
    
    Args:
        project_path: Path to the project directory
        services: YAML content for docker-compose services
    
    Returns:
        Success message
    """
    compose_file = Path(project_path) / "docker-compose.yml"
    compose_file.write_text(services)
    return f"✅ Created docker-compose.yml at {project_path}"

# Agent role to model mapping - optimized for each task
AGENT_MODELS = {
    "architect": "claude-sonnet",    # Best for planning & architecture
    "coder": "deepseek",             # Specialized for code generation
    "devops": "claude-haiku",        # Fast for deployment scripts
    "tester": "qwen-coder",          # Good for test generation
}

# Create specialized agents
class AgentTeam:
    def __init__(self, model_choice=None, custom_models=None):
        """
        Initialize agent team with smart defaults
        
        Args:
            model_choice: Single model to use for all agents (overrides defaults)
            custom_models: Dict to override specific agents, e.g. {"coder": "gpt5-codex"}
        """
        self.workspace = Path("/root/CascadeProjects")
        
        # Determine which models to use for each agent
        if model_choice:
            # User specified one model for everything
            self.models = {
                "architect": model_choice,
                "coder": model_choice,
                "devops": model_choice,
                "tester": model_choice,
            }
            print(f"🤖 Using {MODELS.get(model_choice, model_choice)} for all agents")
        else:
            # Use smart defaults, with optional overrides
            self.models = AGENT_MODELS.copy()
            if custom_models:
                self.models.update(custom_models)
            
            print(f"🤖 Using optimized models for each agent:")
            print(f"   🏗️  Architect: {MODELS.get(self.models['architect'], self.models['architect'])}")
            print(f"   💻 Coder: {MODELS.get(self.models['coder'], self.models['coder'])}")
            print(f"   🚀 DevOps: {MODELS.get(self.models['devops'], self.models['devops'])}")
            print(f"   🧪 Tester: {MODELS.get(self.models['tester'], self.models['tester'])}")
        
        print(f"🔒 ZDR enabled: Your data is not retained\n")
        
        # Architect Agent - Plans the project
        self.architect = Agent(
            model=create_model(self.models["architect"], 0.5),
            system_prompt="""You are an expert software architect. Your job is to:
1. Analyze user requirements
2. Design the project structure (folders, files)
3. Choose the right tech stack
4. Create a detailed implementation plan
5. Output a JSON plan with all files needed and their purposes

Be specific and actionable. Think about scalability, best practices, and deployment.""",
            tools=[]
        )
        
        # Coder Agent - Writes the code
        self.coder = Agent(
            model=create_model(self.models["coder"], 0.3),
            system_prompt="""You are an expert software engineer. Your job is to:
1. Take the architect's plan
2. Write production-ready code for each file
3. Include error handling, logging, and best practices
4. Add comprehensive comments
5. Use the create_file tool to save each file

Write clean, maintainable, well-documented code.""",
            tools=[create_file, read_file, list_directory]
        )
        
        # DevOps Agent - Handles deployment
        self.devops = Agent(
            model=create_model(self.models["devops"], 0.4),
            system_prompt="""You are a DevOps expert. Your job is to:
1. Create Dockerfile if needed
2. Create docker-compose.yml for services
3. Write deployment scripts
4. Set up environment configuration
5. Create README with setup instructions

Make deployment simple and reliable.""",
            tools=[create_file, create_docker_compose, run_command, list_directory]
        )
        
        # Tester Agent - Writes tests
        self.tester = Agent(
            model=create_model(self.models["tester"], 0.3),
            system_prompt="""You are a QA engineer. Your job is to:
1. Write comprehensive unit tests
2. Write integration tests
3. Create test data/fixtures
4. Set up testing framework
5. Document how to run tests

Ensure high code coverage and edge case handling.""",
            tools=[create_file, read_file, list_directory]
        )
    
    def build_project(self, user_request: str):
        """Main orchestration - builds entire project from description"""
        # Initialize database
        db = AgentDatabase()
        
        print("🤖 AGENT TEAM ACTIVATED")
        print("=" * 60)
        print(f"📝 Request: {user_request}\n")
        
        # Log project start
        db.log_decision("system", "project_start", f"Starting project: {user_request}")
        
        # Step 1: Architect plans
        print("🏗️  ARCHITECT AGENT: Planning project...")
        print("-" * 60)
        
        architect_prompt = f"""
User wants: {user_request}

Create a detailed project plan including:
1. Project name (kebab-case)
2. Tech stack
3. File structure (all files needed)
4. Brief description of each file's purpose
5. Dependencies needed

Output as structured text that the coder can follow.
"""
        
        plan = self.architect(architect_prompt)
        print(plan)
        print()
        
        # Log architect decision
        db.log_decision("architect", "project_planning", f"Created plan for: {user_request}", "success")
        
        # Extract project name from plan (simple heuristic)
        project_name = user_request.split()[0].lower().replace(" ", "-")
        project_path = self.workspace / project_name
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save project metadata to database
        db.save_project(
            project_name,
            "agent_team",
            user_request,
            {"workspace": str(self.workspace)}
        )
        
        print(f"📁 Created project directory: {project_path}")
        
        # Initialize GitOps
        gitops = AgentGitOps(project_path)
        gitops.initialize(project_name, user_request)
        print(f"🔧 Initialized GitOps for automated version control\n")
        
        # Step 2: Coder implements
        print("💻 CODER AGENT: Writing code...")
        print("-" * 60)
        
        coder_prompt = f"""
Based on this plan:
{plan}

Implement the entire project at: {project_path}

For each file in the plan:
1. Write complete, production-ready code
2. Use create_file tool to save it
3. Include all necessary imports and error handling

Start with the main files, then supporting files.
"""
        
        code_result = self.coder(coder_prompt)
        print(code_result)
        print()
        
        # Log coder completion
        db.log_decision("coder", "implementation", f"Implemented code for: {project_name}", "success")
        
        # Step 3: Tester creates tests
        print("🧪 TESTER AGENT: Writing tests...")
        print("-" * 60)
        
        tester_prompt = f"""
Project at: {project_path}

Create comprehensive tests:
1. Unit tests for main functionality
2. Integration tests if applicable
3. Test fixtures/data
4. Testing documentation

Use appropriate testing framework for the tech stack.
"""
        
        test_result = self.tester(tester_prompt)
        print(test_result)
        print()
        
        # Log tester completion
        db.log_decision("tester", "testing", f"Created tests for: {project_name}", "success")
        
        # Step 4: DevOps sets up deployment
        print("🚀 DEVOPS AGENT: Setting up deployment...")
        print("-" * 60)
        
        devops_prompt = f"""
Project at: {project_path}

Set up deployment:
1. Create Dockerfile if needed
2. Create docker-compose.yml if multiple services
3. Create .env.example for configuration
4. Create deploy.sh script
5. Create comprehensive README.md with:
   - Setup instructions
   - How to run locally
   - How to deploy
   - Environment variables needed

Make it easy for anyone to run this project.
"""
        
        deploy_result = self.devops(devops_prompt)
        print(deploy_result)
        print()
        
        # Log devops completion
        db.log_decision("devops", "deployment", f"Set up deployment for: {project_name}", "success")
        
        # Log project completion
        db.log_decision("system", "project_complete", f"Project {project_name} completed successfully", "success")
        
        # Final summary
        print("=" * 60)
        print("✨ PROJECT COMPLETE!")
        print("=" * 60)
        print(f"📂 Location: {project_path}")
        print(f"📖 Next steps:")
        print(f"   1. cd {project_path}")
        print(f"   2. Read README.md for setup instructions")
        print(f"   3. Run the application")
        print()
        
        # List created files
        print("📄 Files created:")
        for file in project_path.rglob("*"):
            if file.is_file():
                print(f"   {file.relative_to(project_path)}")

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║      STRANDS AUTONOMOUS AGENT TEAM (OpenRouter Edition)          ║
║                                                                  ║
║  Describe what you want to build.                               ║
║  The agent team will handle everything:                         ║
║    • Architecture & planning                                    ║
║    • Writing all code                                           ║
║    • Creating tests                                             ║
║    • Setting up deployment                                      ║
║                                                                  ║
║  You don't write a single line of code!                         ║
║                                                                  ║
║  🔒 ZDR enabled: Your data is not retained by OpenRouter        ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Show model options
    print(f"📋 Model Selection:")
    print(f"   1. Auto (default) - Optimized models for each agent")
    print(f"   2. Single model - Use one model for all agents")
    print(f"\n   Available: {', '.join(list(MODELS.keys())[:6])}")
    print(f"   Full list: https://openrouter.ai/models\n")
    
    mode = input("Choose mode (1=Auto, 2=Single, Enter=Auto): ").strip()
    
    if mode == "2":
        model_input = input("Which model for all agents? (Enter=claude-sonnet): ").strip()
        model_choice = model_input if model_input in MODELS else "claude-sonnet"
        team = AgentTeam(model_choice=model_choice)
    else:
        # Use smart defaults
        print("\n💡 Using optimized defaults:")
        print("   You can override by editing AGENT_MODELS in the script\n")
        team = AgentTeam()
    
    user_request = input("💭 What do you want to build?\n> ")
    
    if not user_request.strip():
        print("❌ Please provide a description")
        return
    
    team.build_project(user_request)

if __name__ == "__main__":
    main()
