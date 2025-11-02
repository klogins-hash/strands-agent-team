"""
Safety configuration for agent system
Provides guardrails while maintaining flexibility
"""

# Directories agents are allowed to write to
ALLOWED_WRITE_PATHS = [
    "/root/CascadeProjects",
    "/root/.cache",
    "/tmp",
]

# Directories agents should NEVER touch
FORBIDDEN_PATHS = [
    "/etc",
    "/root/.ssh",
    "/root/.config/code-server",
    "/var",
    "/usr",
    "/bin",
    "/sbin",
]

# Commands that require explicit confirmation
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "dd if=",
    "mkfs",
    "fdisk",
    "systemctl stop",
    "systemctl disable",
    "shutdown",
    "reboot",
    "userdel",
    "passwd",
]

# Safe commands that can run without confirmation
SAFE_COMMANDS = [
    "npm install",
    "pip install",
    "docker build",
    "docker-compose up",
    "git clone",
    "mkdir",
    "touch",
    "cat",
    "ls",
    "pwd",
]

def is_path_safe(path: str) -> bool:
    """Check if a path is safe to write to"""
    from pathlib import Path
    
    try:
        path_obj = Path(path).resolve()
        
        # Check if in forbidden paths
        for forbidden in FORBIDDEN_PATHS:
            if str(path_obj).startswith(forbidden):
                return False
        
        # Check if in allowed paths
        for allowed in ALLOWED_WRITE_PATHS:
            if str(path_obj).startswith(allowed):
                return True
        
        return False
    except:
        return False

def is_command_safe(command: str) -> tuple[bool, str]:
    """
    Check if a command is safe to run
    Returns: (is_safe, reason)
    """
    # Check for dangerous patterns
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command:
            return False, f"Contains dangerous pattern: {dangerous}"
    
    # Check if it's a known safe command
    for safe in SAFE_COMMANDS:
        if command.strip().startswith(safe):
            return True, "Known safe command"
    
    # Unknown command - allow but could add logging
    return True, "Unknown command (proceeding with caution)"

# E2B configuration (optional - for future use)
E2B_ENABLED = False  # Set to True to use E2B sandboxes
E2B_API_KEY = None   # Add your E2B API key if you want to use it

# Backup configuration
AUTO_BACKUP_BEFORE_BUILD = True  # Backup workspace before each build
BACKUP_RETENTION_DAYS = 7
