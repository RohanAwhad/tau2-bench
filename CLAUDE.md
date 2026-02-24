# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

τ²-bench (tau2-bench) is a simulation framework for evaluating conversational customer service agents across multiple domains (airline, retail, telecom, mock). It implements a dual-control environment where both the agent and user simulator can interact with the environment through domain-specific tools.

The framework evaluates agents on their ability to:
- Follow domain-specific policies
- Use tools effectively to solve customer service tasks
- Handle conversational interactions with user simulators
- Complete multi-turn tasks successfully

## Common Commands

### Development Setup
```bash
# Install in editable mode (recommended for development)
pip install -e .

# Check data directory configuration
tau2 check-data

# Run all tests
make test

# Run tests for specific domain
pytest tests/test_domains/test_<domain_name>/
```

### Code Quality
```bash
# Check linting
make lint

# Auto-fix linting issues
make lint-fix

# Format code with ruff
make format

# Run both linting and formatting
make check-all
```

### Running Evaluations
```bash
# Quick test evaluation (5 tasks, 1 trial)
tau2 run --domain airline --agent-llm gpt-4.1 --user-llm gpt-4.1 --num-trials 1 --num-tasks 5

# Full domain evaluation
tau2 run --domain retail --agent-llm gpt-4.1 --user-llm gpt-4.1 --num-trials 4

# Run with specific agent/user implementations
tau2 run --domain telecom --agent llm_agent_solo --user dummy_user --agent-llm gpt-4.1

# Run specific tasks
tau2 run --domain airline --agent-llm gpt-4.1 --user-llm gpt-4.1 --task-ids task_001 task_002
```

### Viewing Results
```bash
# Launch interactive results viewer
tau2 view

# View domain API documentation and policy (starts server on port 8004)
tau2 domain <domain>
# Then visit http://127.0.0.1:8004/redoc

# Interactive environment CLI for testing domain tools
make env-cli
```

### Leaderboard Submissions
```bash
# Prepare submission package
tau2 submit prepare data/tau2/simulations/my_model_*.json --output ./my_submission

# Validate submission
tau2 submit validate ./my_submission

# Verify trajectory files
tau2 submit verify-trajs data/tau2/simulations/my_model_*.json
```

## Architecture Overview

### Core Components

**Registry System** (`src/tau2/registry.py`):
- Central registration for agents, users, domains, and task sets
- All custom implementations must be registered here
- Use `registry.register_agent()`, `registry.register_user()`, `registry.register_domain()`, `registry.register_tasks()`

**Orchestrator** (`src/tau2/orchestrator/`):
- Manages message flow between Agent, User, and Environment
- Implements the simulation loop with turn limits and error handling
- Coordinates tool calls and state updates

**Environment** (`src/tau2/environment/`):
- Base classes: `Environment`, `ToolKitBase`, `Tool`, `DB`
- Handles tool execution and state management
- Each domain implements its own environment with custom tools and database schema

**Agent** (`src/tau2/agent/`):
- Base class: `BaseAgent` in `base.py`
- Default implementations: `LLMAgent`, `LLMGTAgent` (oracle plan), `LLMSoloAgent` (no user)
- Agents generate messages and tool calls based on conversation history

**User Simulator** (`src/tau2/user/`):
- Base class: `BaseUser` in `base.py`
- Implementations: `UserSimulator`, `DummyUser`
- Simulates customer behavior and validates agent responses

### Domain Structure

Each domain (`src/tau2/domains/<domain_name>/`) contains:
- `data_model.py`: Database schema (implements `DB` class)
- `tools.py`: Agent-facing tools (implements `ToolKitBase`)
- `user_tools.py`: User-facing tools (optional)
- `environment.py`: Domain environment and task loader functions
- `utils.py`: Domain-specific utilities

Domain data (`data/tau2/domains/<domain_name>/`):
- `tasks.json`: Task definitions
- `policy.md`: Domain policy document
- `db.json` or `db.toml`: Database initial state
- `user_db.json`: User simulator database (optional)

### Evaluation Flow

1. **Task Loading**: Tasks loaded from `data/tau2/domains/<domain>/tasks.json`
2. **Environment Initialization**: Domain environment set up with task-specific state
3. **Orchestration**: Agent ↔ User ↔ Environment message loop
4. **Evaluation**: Task completion evaluated against success criteria
5. **Metrics**: Pass@k rates computed across trials

## Key Implementation Patterns

### Adding a New Agent
1. Create agent class extending `BaseAgent` in `src/tau2/agent/`
2. Implement `generate_next_message()` and `get_init_state_info()`
3. Register in `src/tau2/registry.py`: `registry.register_agent(MyAgent, "my_agent")`
4. Test with: `tau2 run --agent my_agent ...`

### Adding a New Domain
1. Create domain directory in `src/tau2/domains/<domain_name>/`
2. Implement required files: `data_model.py`, `tools.py`, `environment.py`
3. Create domain data in `data/tau2/domains/<domain_name>/`
4. Register in `src/tau2/registry.py`:
   ```python
   from tau2.domains.my_domain.environment import get_environment, get_tasks
   registry.register_domain(get_environment, "my_domain")
   registry.register_tasks(get_tasks, "my_domain")
   ```
5. Add tests in `tests/test_domains/test_my_domain/`

### Adding Experimental Code
- Place in `src/experiments/` directory
- Include standalone README with clear documentation
- Keep isolated from core framework
- No strict support requirements (experimental status)

## Configuration

**Config file**: `src/tau2/config.py`
- Default LLM models and temperatures
- Simulation parameters (max steps, errors, concurrency)
- LLM caching settings (disabled by default)
- Redis configuration for caching
- API server port

**Environment Variables** (`.env` file):
- API keys for LLM providers (via LiteLLM)
- Optional: Langfuse configuration (`USE_LANGFUSE`)

## Data Directory Structure

```
data/tau2/
├── domains/
│   ├── airline/
│   ├── retail/
│   ├── telecom/
│   └── mock/
├── simulations/         # Evaluation results saved here
└── results/            # Processed metrics
```

**Important**: If installing with `pip install .` (non-editable), set `TAU2_DATA_DIR` environment variable to point to the data directory.

## Testing Notes

- Main test suite: `pytest tests/`
- Domain-specific tests: `pytest tests/test_domains/test_<domain>/`
- Each domain should have `test_tools_*.py` and optionally `test_user_tools_*.py`
- Tests use fixtures from `tests/conftest.py`

## LLM Integration

The framework uses **LiteLLM** for LLM API management:
- Supports any LiteLLM-compatible provider
- Configure API keys in `.env` file
- Default models: `gpt-4.1` for both agent and user
- Caching available via Redis (disabled by default)
- Optional Langfuse integration for tracing

## Submission Requirements

For leaderboard submissions:
- Must include all three domains: retail, airline, telecom
- Consistent agent and user LLM configuration across domains
- One result per domain
- All tasks completed (no `--task-ids` or `--num-tasks` filters)
- Validation required before submission

## Branch Naming Conventions

From CONTRIBUTING.md:
- `feature/description` - New features
- `fix/issue-description` - Bug fixes
- `domain/domain-name/feature` - Domain-specific work
- `experiment/name` - Experimental contributions
- `docs/description` - Documentation updates
- `test/description` - Test improvements
