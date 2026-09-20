---
alwaysApply: true
---
---
description: Core engineering and research rules for the AgentTrace project
alwaysApply: true
---

# AgentTrace Project Rules

## 1. Project Identity

AgentTrace is an independent research and engineering project investigating:

"Can we detect when an AI agent is moving toward an unsafe outcome by analyzing its trajectory before the final tool call?"

The project studies security risks in agentic systems by combining:

1. Agent execution
2. Structured telemetry
3. Security-relevant trajectory analysis
4. Risk detection
5. Runtime enforcement
6. Reproducible evaluation

This is a research project, not a production security product and not a clone of any existing commercial platform.

The implementation should be technically serious enough to demonstrate:

- AI agent engineering
- AI security research
- security telemetry
- systems design
- experimental methodology
- evaluation
- runtime controls

---

# 2. Core Research Principle

AgentTrace must treat an agent's behavior as a trajectory, not just as isolated tool calls.

A security decision should be able to consider:

- Agent goal
- Current task
- Previous actions
- Current action
- Tool being invoked
- Tool arguments
- Data being accessed
- Identity
- Permissions
- Environment
- Retrieved context
- Memory
- Model output
- Planned next action
- Historical risk signals

Do not reduce the system to:

"Is this tool allowed?"

The research question is whether contextual and sequential information can reveal unsafe behavior before the final harmful action occurs.

---

# 3. Security Scope

All security experiments must run against:

- local environments
- synthetic data
- intentionally vulnerable test environments
- explicitly authorized infrastructure

Never implement functionality intended to scan, exploit, compromise, or interfere with real third-party systems.

For demonstrations of attacks, create controlled local simulations that reproduce the relevant security behavior.

---

# 4. Engineering Philosophy

Prefer:

- simple architecture
- explicit interfaces
- typed data models
- deterministic tests
- reproducible experiments
- small composable modules
- clear separation of concerns
- observable behavior
- explainable decisions

Avoid:

- unnecessary frameworks
- premature abstractions
- giant classes
- hidden global state
- hard-coded secrets
- magic configuration
- unnecessary dependencies
- copying an existing security product architecture

The system should remain understandable by one engineer reading the repository.

---

# 5. Architecture

The initial architecture should contain these conceptual layers:

agent/
    planner
    executor
    memory

tools/
    filesystem
    database
    email
    search
    MCP-style tool interface

telemetry/
    events
    tracer
    trace storage

detection/
    baseline rules
    LLM judge
    trajectory analysis

enforcement/
    policy engine
    allow
    block
    require approval

attacks/
    prompt injection
    tool poisoning
    memory poisoning
    excessive agency
    long-horizon behavior

evaluation/
    scenarios
    benchmark
    metrics
    experiment runner

shared/
    schemas
    configuration
    utilities

The exact implementation can evolve, but these conceptual boundaries should remain clear.

---

# 6. Event-First Design

Telemetry is a first-class component.

Every meaningful agent action should produce a structured event.

Events should capture enough context to reconstruct an agent trajectory.

At minimum, an event should be capable of representing:

- trace_id
- event_id
- timestamp
- agent_id
- session_id
- step_number
- event_type
- goal
- tool_name
- tool_arguments
- identity
- data_accessed
- model_output
- previous_event_id
- environment
- result
- risk_signals

Do not make every field mandatory if it does not semantically apply to an event.

Use typed schemas rather than arbitrary dictionaries wherever practical.

---

# 7. Separation of Concerns

Keep these responsibilities separate:

Agent:
    Decides what it wants to do.

Executor:
    Executes the requested action.

Telemetry:
    Records what happened.

Detector:
    Evaluates whether behavior appears risky.

Policy engine:
    Decides whether an action is allowed.

Tool:
    Performs the actual operation.

Evaluation:
    Measures system behavior.

Do not allow the detector to silently modify agent state.

Do not allow tools to bypass telemetry.

Do not put security policy directly inside individual tools.

---

# 8. Security Decision Model

The initial policy decision should support:

ALLOW
BLOCK
REQUIRE_APPROVAL

Every security decision should have an explanation.

For example:

{
  "decision": "REQUIRE_APPROVAL",
  "risk_score": 0.82,
  "reasons": [
    "Agent accessed credentials after an unexpected context change",
    "Current action differs from the original task objective",
    "Sensitive data is being passed to an external tool"
  ]
}

Do not expose arbitrary model reasoning or chain-of-thought.

Store concise security-relevant explanations and observable evidence instead.

---

# 9. Baselines Are Required

AgentTrace must eventually compare trajectory-aware detection against simpler approaches.

At minimum, plan for:

1. Tool allowlist
2. Static rule-based detection
3. LLM-as-judge
4. Trajectory-aware detection

The purpose is experimental comparison.

Do not assume the trajectory-aware approach is better.

The benchmark must be capable of showing that it fails.

---

# 10. Evaluation

Experiments must be reproducible.

Every scenario should define:

- scenario name
- threat category
- initial goal
- environment
- available tools
- attack condition
- expected unsafe behavior
- expected security boundary
- expected detection point

Metrics should eventually include:

- detection rate
- false positive rate
- false negative rate
- time/steps to detection
- latency
- token usage
- enforcement outcome
- attack category

Avoid cherry-picking successful demonstrations.

Negative results are valuable research results.

---

# 11. Testing Requirements

Every meaningful component should have tests.

Prioritize:

- schema validation
- telemetry generation
- trajectory reconstruction
- policy decisions
- detector behavior
- attack scenarios
- benchmark calculations

Tests should be deterministic whenever possible.

Mock model calls when testing infrastructure.

Do not require an external API key for the core test suite.

---

# 12. Configuration

Configuration should be explicit.

Use environment variables for:

- API keys
- model configuration
- external services

Never commit secrets.

Provide a `.env.example`.

The repository should work in a local development environment without external infrastructure whenever possible.

---

# 13. Documentation

The repository must explain:

1. What AgentTrace is
2. The research question
3. Why trajectory analysis matters
4. Architecture
5. Threat model
6. Attack scenarios
7. Detection approaches
8. Evaluation methodology
9. Limitations
10. How to reproduce experiments

Do not make unsupported claims such as:

"AgentTrace solves agent security."

Use research language such as:

"AgentTrace investigates whether..."

---

# 14. Research Integrity

The project must distinguish:

- observed behavior
- experimental results
- hypotheses
- assumptions
- conclusions

Do not design experiments to prove a predetermined conclusion.

If a baseline performs better, document it.

If the approach fails, document it.

If results are inconclusive, document that.

---

# 15. Development Process

Work incrementally.

Before implementing a major component:

1. Inspect the existing repository.
2. Understand current architecture.
3. Identify the smallest useful change.
4. Implement it.
5. Add tests.
6. Run tests.
7. Update documentation.
8. Only then move to the next component.

Do not rewrite working code without a clear reason.

Do not introduce large dependencies without justification.

---

# 16. Initial Milestone

The first implementation milestone is NOT the complete research system.

The first milestone is a minimal end-to-end vertical slice:

User goal
    ↓
Agent
    ↓
Tool request
    ↓
Telemetry event
    ↓
Trajectory
    ↓
Simple detector
    ↓
Policy decision
    ↓
ALLOW / BLOCK / REQUIRE_APPROVAL
    ↓
Structured result

This vertical slice must run locally and be testable.

Once it works, expand the system.

---

# 17. Code Quality

Use:

- Python 3.11+
- type hints
- Pydantic or equivalent typed schemas
- pytest
- clear module boundaries
- meaningful names
- small functions
- explicit error handling

Prefer boring, readable code over clever code.

---

# 18. Git Discipline

Make changes in coherent commits.

Suggested initial commits:

1. `chore: initialize project`
2. `feat: add agent event schemas`
3. `feat: add telemetry pipeline`
4. `feat: add minimal agent executor`
5. `feat: add baseline security policy`
6. `test: add initial attack scenarios`

Do not commit generated secrets, local databases, virtual environments, or API credentials.

---

# 19. Agent Behavior

When acting as a coding agent:

- inspect before modifying
- explain architectural decisions briefly
- do not invent requirements
- do not silently change the research question
- do not over-engineer
- do not skip tests
- do not hide failures
- do not fabricate experimental results
- do not claim a feature works without testing it

If an architectural decision is ambiguous, choose the simplest reversible option and document the assumption.

---

# 20. Definition of Done

A feature is not complete merely because the code exists.

A meaningful feature should have:

- implementation
- tests
- usable interface
- example
- documentation where appropriate
- successful local execution

The repository should remain runnable after every major change.`