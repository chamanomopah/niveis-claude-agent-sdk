---
description: Orchestrate specialized agents based on user requirements. Creates agent teams with specific commands and task coordination. Supports reusable workflows.
argument-hint: [objective] [--workflow WORKFLOW_NAME] [orchestration-guidance]
model: opus
---

# Orchestrate Agents

Create and orchestrate a team of specialized agents based on the user's objective. This command analyzes requirements, designs agent specialization, creates tasks with dependencies, and coordinates execution using TaskCreate, TaskUpdate, and related tools.

## Arguments

- `$1`: **OBJECTIVE** - The main objective or problem to solve (required)
- `--workflow WORKFLOW_NAME`: Use a predefined workflow from `.claude/commands/workflows/` (optional)
- Remaining arguments: **ORCHESTRATION_GUIDANCE** - Optional guidance for agent specialization, command allocation, and execution strategy

## Workflow Mode

**When `--workflow` is specified:**

1. Load the workflow definition from `.claude/commands/workflows/[WorkflowName].md`
2. Execute the predefined command sequence
3. Follow the workflow's execution flow exactly
4. Use the workflow's specified agent requirements
5. Apply the workflow's parallel/sequential strategy

**Example:**
```bash
/orchestrate-agents "Add password reset feature" --workflow SimpleSdlc
```

**When `--workflow` is NOT specified:**

Proceed with custom orchestration (see Custom Mode below).

## Available Workflows

| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| **SimpleSdlc** | Basic plan → implement → test → review | Simple features, bug fixes, chores |
| **TeamSdlc** | Team-based orchestration with parallel execution | Complex features, full-stack work |
| **QuickPatch** | Rapid bug fix workflow | Hotfixes, quick corrections |

See `.claude/commands/workflows/` for complete workflow definitions.

## Context

You have deep knowledge of:
- **Claude Code**: Architecture, capabilities, and interaction patterns
- **Slash Commands**: Available commands in `.claude/commands/` and when to use each
- **Task Management**: TaskCreate, TaskUpdate, TaskDelete, TaskList, TaskGet, TaskOutput
- **Agent Types**: Available subagents in `.claude/agents/team/*.md` and built-in types (general-purpose, Explore, Plan, etc.)
- **Execution Flow**: How to sequence and parallelize work effectively

## Instructions

### Mode Selection

**First, check if `--workflow` flag is present:**

1. **Workflow Mode**: If `--workflow WORKFLOW_NAME` is specified
   - Load `.claude/commands/workflows/[WorkflowName].md`
   - Follow the workflow's command sequence exactly
   - Skip to "Execute Workflow" section below

2. **Custom Mode**: If no `--workflow` flag
   - Proceed with "Phase 1: Analyze Requirements" below
   - Design custom orchestration strategy

### Execute Workflow (Workflow Mode)

When a workflow is specified:

1. **Load Workflow Definition**
   ```markdown
   Read: .claude/commands/workflows/[WorkflowName].md
   ```

2. **Parse Command Sequence**
   - Extract the command sequence table
   - Note which steps are parallel vs sequential
   - Identify agent requirements

3. **Execute Commands in Order**
   - For each step in the workflow:
     - Execute the specified command with the objective
     - Wait for completion (unless `Parallel: true`)
     - Capture results for next step

4. **Handle Parallel Steps**
   - When `Parallel: true`, launch commands simultaneously
   - Use `run_in_background: true` in Task tool
   - Wait for all parallel steps to complete before next sequential step

5. **Report Completion**
   - Follow workflow's expected output format
   - Report any deviations or issues

### Custom Mode (No Workflow)

Proceed with custom orchestration phases below.

### Phase 1: Analyze Requirements (Custom Mode)

1. **Parse the OBJECTIVE** from `$1`
   - If no objective provided, STOP and ask the user
   - Identify the core problem/opportunity
   - Determine complexity level (simple|medium|complex)

2. **Parse ORCHESTRATION_GUIDANCE** from `$2` (optional)
   - Agent specialization hints
   - Preferred command patterns
   - Execution strategy preferences

3. **Ultrathink** about:
   - What types of agents are needed?
   - What commands should each agent use?
   - How should work be divided (parallel vs sequential)?
   - What dependencies exist between tasks?

### Phase 2: Design Agent Team

For each agent needed, define:

```
Agent Name: <unique-name>
Role: <specialization - e.g., "database-migrator", "api-builder">
Agent Type: <subagent_type - e.g., "general-purpose", "Explore", custom>
Commands: <list of specific commands this agent will use>
Capabilities: <what this agent can do>
Resume: <true/false - whether to maintain context>
```

**Agent Specialization Patterns:**

- **Builder Agents**: Write code, create files, implement features
- **Explorer Agents**: Research codebase, find patterns, analyze architecture
- **Validator Agents**: Test, verify, check acceptance criteria
- **Orchestrator Agents**: Coordinate other agents, manage task lists
- **Specialist Agents**: Domain-specific (database, API, frontend, etc.)

### Phase 3: Create Task Structure

**BEFORE deploying any agents**, use `TaskCreate` to build the task list:

```javascript
// Example: Creating initial task list
TaskCreate({
  subject: "Research existing authentication patterns",
  description: "Use Explore agent to find current auth implementation in the codebase",
  activeForm: "Researching authentication patterns"
})
// Returns: taskId "1"

TaskCreate({
  subject: "Design new authentication flow",
  description: "Design JWT-based auth with refresh tokens",
  activeForm: "Designing authentication flow"
})
// Returns: taskId "2"

TaskCreate({
  subject: "Implement authentication endpoints",
  description: "Create login, logout, and refresh token endpoints",
  activeForm: "Implementing authentication endpoints"
})
// Returns: taskId "3"
```

### Phase 4: Set Dependencies

Use `TaskUpdate` with `addBlockedBy` to create execution order:

```javascript
// Task 2 depends on Task 1
TaskUpdate({
  taskId: "2",
  addBlockedBy: ["1"]
})

// Task 3 depends on both Task 1 and Task 2
TaskUpdate({
  taskId: "3",
  addBlockedBy: ["1", "2"]
})
```

**Dependency Patterns:**

```
Sequential:  A → B → C
Parallel:    A   B
              ↘ ↙
                C
Diamond:    A → B ↛
          ↙       ↛
        C → D ↛
```

### Phase 5: Deploy and Orchestrate

For each task, deploy the appropriate agent:

```javascript
// Deploy agent for Task 1
Task({
  description: "Research authentication patterns",
  prompt: "Use available commands to explore the codebase and find all authentication-related code. Focus on: 1) Current auth implementation, 2) User models, 3) API endpoints. Report findings with file references.",
  subagent_type: "Explore",
  model: "sonnet",
  run_in_background: false  // Sequential execution
})
// Returns: agentId "agent-1"

// After Task 1 completes, deploy for Task 2
Task({
  description: "Design authentication flow",
  prompt: "Based on research findings, design a new JWT-based authentication system with: 1) Access tokens (15min expiry), 2) Refresh tokens (7 days), 3) Secure storage. Create design document in docs/auth-design.md",
  subagent_type: "general-purpose",
  model: "opus"
})
// Returns: agentId "agent-2"

// For parallel tasks
Task({
  description: "Implement login endpoint",
  prompt: "Create POST /auth/login endpoint following the design in docs/auth-design.md",
  subagent_type: "general-purpose",
  model: "sonnet",
  run_in_background: true  // Parallel execution
})
// Returns: agentId "agent-3"
```

### Phase 6: Monitor and Coordinate

**Track Progress:**
```javascript
// Check all tasks
TaskList({})
// Returns: Array of {id, subject, status, owner, blockedBy}

// Get specific task details
TaskGet({ taskId: "1" })
// Returns: Full task info
```

**Update Task Status:**
```javascript
// Mark task as in progress
TaskUpdate({
  taskId: "1",
  status: "in_progress",
  owner: "agent-1"
})

// Mark task as completed
TaskUpdate({
  taskId: "1",
  status: "completed"
})
```

**Check Agent Output:**
```javascript
// For background tasks
TaskOutput({
  task_id: "agent-3",
  block: false,  // Non-blocking check
  timeout: 5000
})

// Wait for completion
TaskOutput({
  task_id: "agent-3",
  block: true,   // Wait until done
  timeout: 300000
})
```

### Phase 7: Resume and Iterate

**Resume Context:**
```javascript
// Continue with same agent context
Task({
  description: "Continue auth implementation",
  prompt: "Now add the refresh token endpoint to complete the auth system",
  subagent_type: "general-purpose",
  resume: "agent-2"  // Same agent, preserved context
})
```

**When to Resume vs Fresh:**
- **Resume**: Related work, needs prior context (e.g., "now add error handling")
- **Fresh**: New task, clean slate preferred (e.g., "write tests")

### Phase 8: Validation and Completion

**Final Validation:**
```javascript
// Create final validation task
TaskCreate({
  subject: "Validate authentication system",
  description: "Run all tests, verify acceptance criteria, check security",
  activeForm: "Validating authentication system"
})

// Deploy validator agent
Task({
  description: "Validate authentication system",
  prompt: "Run validation commands from the plan. Verify: 1) All tests pass, 2) Acceptance criteria met, 3) Security requirements satisfied. Report status.",
  subagent_type: "validator"
})
```

## Command Usage Patterns

**Common Commands by Agent Type:**

| Agent Type | Typical Commands | Usage |
|------------|-----------------|-------|
| **Explore** | Grep, Glob, Read | Research codebase patterns |
| **Builder** | Write, Edit, Bash | Create and modify files |
| **Tester** | Bash(test), Read | Run tests and verify |
| **Orchestrator** | Task*, Task, TaskOutput | Coordinate workflow |
| **Specialist** | Domain-specific | Database, API, frontend, etc. |

## Execution Strategy

**Sequential (default):**
```javascript
run_in_background: false  // Wait for each agent to finish
```
Use when: Tasks have dependencies, require shared context

**Parallel:**
```javascript
run_in_background: true  // Launch multiple agents simultaneously
```
Use when: Independent tasks, different parts of codebase

**Mixed:**
```javascript
// Sequential foundation
Task({ run_in_background: false, ... })  // Foundation

// Parallel implementation
Task({ run_in_background: true, ... })   // Component A
Task({ run_in_background: true, ... })   // Component B

// Wait and validate
TaskOutput({ task_id: "...", block: true })
```

## Communication Protocol

**Agent Communication Flow:**

1. **Orchestrator → Agent**: Initial task delegation via Task()
2. **Agent → Orchestrator**: Results returned in TaskOutput
3. **Orchestrator → Agent**: Follow-up via resume or new Task()
4. **Inter-Agent**: Use orchestrator as message hub

**Status Updates:**
- Mark tasks as in_progress when starting
- Mark as completed when done
- Update owner to track which agent is working
- Use TaskList for team-wide visibility

## Report Format

After orchestration is complete, provide:

```markdown
## Orchestration Complete

**Objective:** <brief summary of what was accomplished>

### Agents Deployed

<Agent Name> (<Agent Type>)
- Role: <specialization>
- Tasks: <Task IDs worked on>
- Status: <completed/failed/in-progress>

### Task Summary

✅ Task 1: <subject> - <status>
✅ Task 2: <subject> - <status>
⏳ Task 3: <subject> - <status>

### Files Created/Modified

- <file1> - <purpose>
- <file2> - <purpose>

### Next Steps

<if incomplete> Continue with: <remaining tasks>
<if complete> Verification: <validation commands>

### Agent Session IDs

<agent-name>: <session-id> (for resume)
```

## Key Principles

1. **Plan First**: Always create task list BEFORE deploying agents
2. **Clear Dependencies**: Use addBlockedBy explicitly
3. **Track Ownership**: Update owner field when assigning tasks
4. **Monitor Progress**: Check TaskList regularly
5. **Resume Wisely**: Preserve context when related, fresh when not
6. **Validate Last**: Always have final validation task
7. **Communicate**: Keep team informed via task status updates

## Troubleshooting

**Agent stuck?**
- Check TaskOutput for errors
- Consider resume vs new agent
- Verify dependencies are complete

**Task blocked indefinitely?**
- Check blockedBy list
- Verify dependencies exist
- May need to unblock manually

**Parallel conflicts?**
- Check for file write conflicts
- Use different files or sequential execution
- Consider merge strategy

## Notes

- This command operates as an orchestrator, NOT a builder
- Use Task* tools extensively for coordination
- Document agent session IDs for resumption
- Keep task descriptions clear and actionable
- Test orchestration flow with simple tasks first
- Scale complexity as you learn patterns

## Usage Examples

### Example 1: Workflow Mode (SimpleSdlc)

```bash
/orchestrate-agents "Add user profile page" --workflow SimpleSdlc
```

**Output:**
```
✅ SimpleSdlc Workflow Started

Step 1: Planning...
→ Plan created: specs/user-profile-page.md

Step 2: Implementing...
→ Profile page component created
→ User data fetching implemented
→ Styling applied

Step 3: Testing...
→ All tests passing ✓

Step 4: Review...
→ Implementation matches spec ✓

✅ Workflow Complete
```

### Example 2: Workflow Mode (TeamSdlc)

```bash
/orchestrate-agents "Build real-time notifications system" --workflow TeamSdlc
```

**Output:**
```
✅ TeamSdlc Workflow Started

Step 1: Planning with team...
→ Plan created: specs/realtime-notifications.md
→ Team: builder-backend, builder-frontend, validator
→ Tasks: 6 tasks with parallel tracks

Step 2: Orchestrating agents...
→ Deploying builder-backend for WebSocket setup...
→ Deploying builder-frontend for notification UI (parallel)...
→ Coordinating integration...

All tasks completed!

Step 3: Testing...
→ Unit tests: 89 passing ✓

Step 4: E2E Testing...
→ User journey tests: 12 passing ✓

Step 5: Review...
→ Implementation matches spec ✓

✅ Workflow Complete
```

### Example 3: Custom Mode (Manual Orchestration)

```bash
/orchestrate-agents "Migrate database to PostgreSQL with minimal downtime"
```

**Output:**
```
✅ Custom Orchestration Started

Analyzing requirements...
→ Complexity: High
→ Strategy: Blue-green deployment with data sync

Creating task structure...
→ Task 1: Setup PostgreSQL instance
→ Task 2: Create data sync pipeline
→ Task 3: Migrate schema
→ Task 4: Switch traffic
→ Task 5: Validate and cleanup

Deploying agents...
→ Agent db-migrator working on Task 1...
→ Agent pipeline-builder working on Task 2 (parallel)...
✓ Tasks 1,2 completed
→ Agent schema-migrator working on Task 3...
✓ Task 3 completed
→ Agent traffic-controller working on Task 4...
✓ Task 4 completed
→ Agent validator working on Task 5...
✓ Task 5 completed

✅ Orchestration Complete
Database migrated with 2 seconds downtime
```

### Example 4: Quick Patch

```bash
/orchestrate-agents "Fix navigation menu not collapsing on mobile" --workflow QuickPatch
```

**Output:**
```
✅ QuickPatch Workflow Started

Step 1: Creating patch plan...
→ Problem: CSS media query incorrect breakpoint
→ Fix: Update breakpoint from 768px to 640px

Step 2: Applying patch...
→ Modified: src/styles/navigation.css

Step 3: Validating...
→ Mobile navigation test: Passing ✓

✅ Workflow Complete
```

## Creating New Workflows

To create a new workflow:

```bash
/create-workflow [WorkflowName] "[description of what workflow does]"
```

This will:
1. Create `.claude/commands/workflows/[WorkflowName].md`
2. Define command sequence
3. Specify agent requirements
4. Set parallel/parallel strategy
5. Register in orchestration command

## Workflow Best Practices

1. **Reuse commands**: Workflows should sequence existing commands, not recreate them
2. **Clear purpose**: Each workflow should have a specific use case
3. **Test incrementally**: Start with simple objectives, add complexity
4. **Document assumptions**: Specify when to use vs NOT use each workflow
5. **Handle failures**: Define what happens when a step fails
6. **Version control**: Track workflow changes in git

## Orchestration Patterns

### Sequential Pattern (SimpleSdlc)
```
Command 1 → Command 2 → Command 3 → Command 4
```
Use for: Simple tasks, clear dependencies

### Parallel Pattern (TeamSdlc)
```
Command 1 → Command 2   Command 3
              ↓    ↙          ↓    ↙
                 Command 4
```
Use for: Independent tasks that can run simultaneously

### Mixed Pattern
```
Command 1 → Command 2 (parallel) → Command 3
```
Use for: Foundation work followed by parallel implementation

### Conditional Pattern
```
Command 1 → if (success) → Command 2a
                      else → Command 2b
```
Use for: Workflows with decision points
