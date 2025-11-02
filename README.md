# Strands Autonomous Agent Team

**Build anything by just describing it - no code needed!**

> 🚀 **Production-ready agent system** running on Scaleway with OpenRouter integration
> 
> - ✅ Multi-model support (Claude, GPT-5, DeepSeek, Qwen, Gemini)
> - ✅ Smart model defaults optimized for each agent
> - ✅ Agent-centric state management (no Git needed)
> - ✅ Scaleway infrastructure integration
> - ✅ Zero data retention (ZDR enabled)

## What This Does

You describe what you want to build. A team of AI agents:
1. **🏗️ Architect** - Plans the project structure
2. **💻 Coder** - Writes all the code
3. **🧪 Tester** - Creates comprehensive tests
4. **🚀 DevOps** - Sets up deployment

You get a complete, production-ready project without writing a single line of code.

## Quick Start

### 1. Set Your API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

Get your key from: https://console.anthropic.com/

### 2. Run the Agent Team

```bash
cd /root/CascadeProjects/strands-agent-team
python3 agent_team.py
```

### 3. Describe What You Want

```
💭 What do you want to build?
> A REST API for a todo app with Express, MongoDB, and JWT authentication
```

### 4. Watch the Agents Work

```
🏗️  ARCHITECT AGENT: Planning project...
💻 CODER AGENT: Writing code...
🧪 TESTER AGENT: Writing tests...
🚀 DEVOPS AGENT: Setting up deployment...
✨ PROJECT COMPLETE!
```

## Example Projects

### Example 1: Simple Web App
```
> A blog website with Next.js and Tailwind CSS
```

### Example 2: API Service
```
> A REST API for user management with FastAPI and PostgreSQL
```

### Example 3: Real-time App
```
> A chat application with WebSockets and React
```

### Example 4: Data Pipeline
```
> A data processing pipeline that reads CSV files and generates reports
```

### Example 5: Microservice
```
> A payment processing microservice with Stripe integration
```

## What Gets Created

For each project, the agents create:

- ✅ **All source code files** - Complete, production-ready
- ✅ **Tests** - Unit and integration tests
- ✅ **Dockerfile** - For containerization
- ✅ **docker-compose.yml** - For multi-service apps
- ✅ **README.md** - Complete setup instructions
- ✅ **deploy.sh** - Deployment script
- ✅ **.env.example** - Configuration template

## How It Works

### The Agent Team

**Architect Agent**
- Analyzes your requirements
- Designs project structure
- Chooses tech stack
- Creates implementation plan

**Coder Agent**
- Writes all code files
- Implements best practices
- Adds error handling
- Includes documentation

**Tester Agent**
- Creates unit tests
- Writes integration tests
- Sets up test framework
- Ensures code coverage

**DevOps Agent**
- Creates Dockerfile
- Sets up docker-compose
- Writes deployment scripts
- Creates comprehensive README

### Tools Available to Agents

- `create_file` - Create files with content
- `read_file` - Read existing files
- `list_directory` - Browse directories
- `run_command` - Execute shell commands
- `create_docker_compose` - Set up Docker services

## Advanced Usage

### Custom Instructions

Be specific in your request:

```
> Build a REST API for e-commerce with:
  - Product catalog with search
  - Shopping cart
  - Order management
  - Stripe payment integration
  - Admin dashboard
  - Use Node.js, Express, MongoDB
  - Include rate limiting and authentication
```

### Multi-Service Apps

```
> Build a microservices app with:
  - Frontend: React with TypeScript
  - API Gateway: Express
  - Auth Service: JWT with Redis
  - Database: PostgreSQL
  - All services in Docker Compose
```

### Specific Tech Stack

```
> Build a data dashboard using:
  - Backend: Python FastAPI
  - Database: PostgreSQL
  - Frontend: React with Chart.js
  - Real-time updates with WebSockets
```

## Cost Estimate

Using Claude 3.5 Sonnet:
- Simple project: $0.50 - $2.00
- Medium project: $2.00 - $5.00
- Complex project: $5.00 - $15.00

The agents are efficient and only use tokens for actual work.

## Tips for Best Results

✅ **DO:**
- Be specific about requirements
- Mention tech stack preferences
- Describe key features clearly
- Specify integrations needed

❌ **DON'T:**
- Be too vague ("make an app")
- Ask for extremely complex systems in one go
- Expect perfection on first try (you can iterate)

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

**Agents not creating files**
- Check you have write permissions
- Verify the project path exists

**Code has errors**
- The agents write production-ready code, but you can:
  1. Run the agent again with more specific instructions
  2. Manually fix small issues
  3. Ask agents to fix specific problems

## Examples of What You Can Build

- 🌐 **Web Applications** - Full-stack apps with frontend/backend
- 🔌 **REST APIs** - Complete API services with documentation
- 💬 **Chat Apps** - Real-time communication systems
- 📊 **Dashboards** - Data visualization and analytics
- 🤖 **Bots** - Slack bots, Discord bots, etc.
- 📱 **Mobile Backends** - APIs for mobile apps
- 🔄 **Data Pipelines** - ETL and data processing
- 🎮 **Games** - Simple web-based games
- 🛒 **E-commerce** - Shopping platforms
- 📝 **CMS** - Content management systems

## Next Steps

After the agents finish:

1. **Navigate to project**
   ```bash
   cd /root/CascadeProjects/your-project-name
   ```

2. **Read the README**
   ```bash
   cat README.md
   ```

3. **Install dependencies**
   ```bash
   # Follow instructions in README
   npm install  # or pip install -r requirements.txt
   ```

4. **Run the project**
   ```bash
   # Follow instructions in README
   npm start  # or python main.py
   ```

5. **Deploy**
   ```bash
   ./deploy.sh  # or docker-compose up
   ```

## Iterate and Improve

If you want to add features or fix issues:

```bash
python3 agent_team.py
> Add user profile page to the blog project at /root/CascadeProjects/blog
```

The agents can modify existing projects too!

---

**You describe it. Agents build it. That's it.** 🚀

## Documentation

- 📖 [OpenRouter Integration](docs/OPENROUTER-UPDATED.md) - Multi-model support with 343+ models
- 📖 [Smart Model Defaults](docs/SMART-DEFAULTS.md) - Optimized models for each agent
- 📖 [Agent State Management](docs/AGENT-CENTRIC-STATE.md) - Better than GitOps for agents
- 📖 [Scaleway Optimization](docs/SCALEWAY-AGENT-OPTIMIZATION.md) - Full infrastructure guide
- 📖 [Complete Scaleway Stack](docs/SCALEWAY-COMPLETE-AGENT-STACK.md) - All services catalog

## Features

### Multi-Model Support
- Access 343+ models via OpenRouter
- Smart caching (24-hour refresh)
- Auto-discovery of latest models
- ZDR (Zero Data Retention) enabled

### Intelligent Defaults
- **Architect**: Claude Sonnet (best for planning)
- **Coder**: DeepSeek (specialized for code)
- **DevOps**: Claude Haiku (fast & efficient)
- **Tester**: Qwen Coder (excellent for tests)

### Agent-Centric State
- State snapshots instead of commits
- Decision logging for agent learning
- Continuous deployment
- Self-healing on errors

### Scaleway Integration
- Object Storage for backups
- PostgreSQL for metadata
- Redis for caching
- Serverless deployment
- Email notifications

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Strands Agent Team                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  OpenRouter (343+ models)                               │
│    ↓                                                     │
│  Agent Team                                             │
│    ├─ Architect (Claude Sonnet)                        │
│    ├─ Coder (DeepSeek)                                 │
│    ├─ DevOps (Claude Haiku)                            │
│    └─ Tester (Qwen Coder)                              │
│                                                          │
│  State Management                                       │
│    ├─ Snapshots (not commits)                          │
│    ├─ Decision Log                                      │
│    └─ Continuous Deployment                             │
│                                                          │
│  Scaleway Infrastructure                                │
│    ├─ Object Storage                                    │
│    ├─ PostgreSQL                                        │
│    ├─ Redis                                             │
│    └─ Serverless Functions                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## License

Apache 2.0

## Contributing

This is an agent-first system. Contributions welcome\!

