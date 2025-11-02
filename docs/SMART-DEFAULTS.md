# 🎯 Smart Model Defaults - Optimized for Each Task

## What Changed

Your agent system now uses **optimized models for each agent type** by default!

## Default Model Assignment

Each agent now uses the best model for its specific task:

| Agent | Default Model | Why? |
|-------|--------------|------|
| 🏗️ **Architect** | `claude-sonnet` | Best for planning & architecture |
| 💻 **Coder** | `deepseek` | Specialized for code generation |
| 🚀 **DevOps** | `claude-haiku` | Fast for deployment scripts |
| 🧪 **Tester** | `qwen-coder` | Excellent for test generation |

## How It Works

### Auto Mode (Default - Recommended)

```bash
build-agent

Choose mode (1=Auto, 2=Single, Enter=Auto): [press Enter]

🤖 Using optimized models for each agent:
   🏗️  Architect: anthropic/claude-sonnet-4.5
   💻 Coder: deepseek/deepseek-chat-v3.1
   🚀 DevOps: anthropic/claude-haiku-4.5
   🧪 Tester: qwen/qwen3-coder-plus
```

**Benefits:**
- ✅ Each agent uses the best model for its task
- ✅ Cost-optimized (uses cheaper models where appropriate)
- ✅ Performance-optimized (uses specialized models)
- ✅ No need to choose - just press Enter!

### Single Model Mode

```bash
build-agent

Choose mode (1=Auto, 2=Single, Enter=Auto): 2
Which model for all agents? (Enter=claude-sonnet): gpt5-pro

🤖 Using openai/gpt-5-pro for all agents
```

**Use when:**
- You want consistency across all agents
- You prefer a specific model
- You're testing a new model

## Why These Defaults?

### Architect: Claude Sonnet
- **Strengths**: Strategic thinking, planning, architecture
- **Temperature**: 0.5 (balanced creativity)
- **Best for**: Designing project structure, choosing tech stacks

### Coder: DeepSeek
- **Strengths**: Code generation, understanding code patterns
- **Temperature**: 0.3 (precise, deterministic)
- **Best for**: Writing production-ready code
- **Bonus**: Cost-effective for large codebases

### DevOps: Claude Haiku
- **Strengths**: Fast, efficient, good at scripts
- **Temperature**: 0.4 (balanced)
- **Best for**: Dockerfiles, deployment scripts, configs
- **Bonus**: Cheaper and faster than Sonnet

### Tester: Qwen Coder
- **Strengths**: Understanding code, generating tests
- **Temperature**: 0.3 (precise)
- **Best for**: Unit tests, integration tests, edge cases

## Customization

### Option 1: Edit Defaults in Script

Edit `/root/CascadeProjects/strands-agent-team/agent_team.py`:

```python
AGENT_MODELS = {
    "architect": "claude-sonnet",    # Change to "gpt5-pro"
    "coder": "deepseek",             # Change to "gpt5-codex"
    "devops": "claude-haiku",        # Change to "gemini-flash"
    "tester": "qwen-coder",          # Change to "deepseek"
}
```

### Option 2: Use Single Model Mode

Just choose mode 2 when prompted and select your preferred model.

### Option 3: Programmatic Override

```python
from agent_team import AgentTeam

# Override specific agents
team = AgentTeam(custom_models={
    "coder": "gpt5-codex",
    "tester": "claude-sonnet"
})
```

## Cost Comparison

### Auto Mode (Optimized)
- Architect: Claude Sonnet (premium)
- Coder: DeepSeek (cheap)
- DevOps: Claude Haiku (cheap)
- Tester: Qwen Coder (cheap)

**Estimated cost per project**: $1-3

### All Claude Sonnet
- All agents: Claude Sonnet (premium)

**Estimated cost per project**: $3-8

### All GPT-5 Pro
- All agents: GPT-5 Pro (premium)

**Estimated cost per project**: $4-10

## Performance Benefits

| Metric | Auto Mode | Single Model |
|--------|-----------|--------------|
| **Speed** | ⚡⚡⚡ Faster (uses Haiku for DevOps) | ⚡⚡ Slower |
| **Cost** | 💰 $1-3 | 💰💰 $3-10 |
| **Quality** | ⭐⭐⭐⭐⭐ Optimized | ⭐⭐⭐⭐ Good |
| **Specialization** | ✅ Each task optimized | ❌ One-size-fits-all |

## Examples

### Example 1: Default (Recommended)
```bash
build-agent
[press Enter for Auto mode]

# Uses optimized models for each agent
# Fast, cost-effective, high quality
```

### Example 2: All GPT-5 Pro
```bash
build-agent
2  # Single model mode
gpt5-pro

# Uses GPT-5 Pro for everything
# Consistent, premium quality, higher cost
```

### Example 3: Custom Mix
Edit script to use:
- Architect: gpt5-pro (best planning)
- Coder: deepseek (specialized)
- DevOps: gemini-flash (fast & cheap)
- Tester: qwen-coder (specialized)

## Recommendation

**For most users**: Use **Auto mode** (just press Enter)
- Best balance of quality, speed, and cost
- Each agent uses the optimal model
- No decision fatigue

**For specific needs**: Use **Single model mode**
- Testing a new model
- Need consistency across all agents
- Have specific model preferences

## Summary

✅ **Smart defaults** - No need to choose every time
✅ **Flexible** - Can override when needed
✅ **Optimized** - Each agent uses best model for its task
✅ **Cost-effective** - Uses cheaper models where appropriate
✅ **Fast** - Uses faster models for simple tasks

Your agent system is now **intelligent and efficient**! 🚀
