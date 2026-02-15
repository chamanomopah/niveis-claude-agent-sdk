# TeamSdlc Workflow

Team-based SDLC with orchestration: Plan with Team → Orchestrate Implementation → Test → Review

## Purpose

Execute complex development tasks requiring multiple specialized agents working in coordination. Suitable for medium to high complexity features that benefit from parallel execution and specialization.

## When to Use

- Medium to high complexity features
- Tasks requiring multiple specialists (backend, frontend, database, etc.)
- Projects that can be parallelized
- Large-scale refactoring
- Full-stack features

**NOT for:**
- Simple bug fixes (use SimpleSdlc)
- Single-file changes (use SimpleSdlc)
- Quick chores

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | plan_w_team | Create team-based implementation plan with task breakdown | false |
| 2 | orchestrate-agents | Orchestrate team of agents to execute the plan | false |
| 3 | test | Run comprehensive test suite | false |
| 4 | test-e2e | Execute end-to-end user journey tests | false |
| 5 | review | Review implementation against original spec | false |

## Execution Flow

```
User Request
     ↓
[1] plan_w_team - Create detailed plan with:
   - Team member definitions
   - Task breakdown with IDs
   - Dependencies between tasks
   - Parallel/sequential execution strategy
     ↓
[2] orchestrate-agents - Execute the plan:
   - Create tasks with TaskCreate
   - Set dependencies with TaskUpdate
   - Deploy agents with Task tool
   - Monitor progress with TaskList
   - Coordinate communication between agents
     ↓
[3] test - Run unit and integration tests
     ↓
[4] test-e2e - Validate user journeys
     ↓
[5] review - Verify implementation matches spec
     ↓
Complete (or create patches for issues)
```

## Agent Requirements

**Orchestrator (Team Lead):**
- Reads the team-based plan
- NEVER writes code directly
- Uses Task* tools exclusively for coordination
- Deploys specialist agents via Task tool
- Monitors progress with TaskList and TaskOutput
- Coordinates communication between agents

**Specialist Agents (deployed as needed):**
- **Builder agents**: Write code, create files (general-purpose)
- **Explore agents**: Research codebase patterns (Explore)
- **Validator agents**: Test and verify (test-runner, validator)
- **Domain specialists**: Database, API, frontend, etc.

**Key Principle:** Orchestrator delegates, specialists execute.

## Task Management Flow

```javascript
// 1. Create all tasks first
TaskCreate({ subject: "Setup database schema", ... }) // Task 1
TaskCreate({ subject: "Build API endpoints", ... })   // Task 2
TaskCreate({ subject: "Create frontend components", ... }) // Task 3

// 2. Set dependencies
TaskUpdate({ taskId: "2", addBlockedBy: ["1"] }) // API depends on DB
TaskUpdate({ taskId: "3", addBlockedBy: ["1"] }) // Frontend depends on DB

// 3. Deploy agents
Task({
  description: "Build API",
  prompt: "Implement REST endpoints...",
  subagent_type: "general-purpose",
  run_in_background: true  // Can run in parallel with frontend
})

// 4. Monitor
TaskList({})  // Check all task statuses
TaskOutput({ task_id: "agent-id", block: true })  // Wait for completion

// 5. Update status
TaskUpdate({ taskId: "1", status: "completed" })
```

## Example Usage

```bash
/orchestrate-agents "Build real-time chat feature with WebSocket support" --workflow TeamSdlc
```

**Output:**

```
✅ TeamSdlc Workflow Started

Step 1: Planning with team...
→ Plan created: specs/realtime-chat-feature.md
→ Team members: builder-backend, builder-frontend, validator
→ Tasks: 8 tasks with 3 parallel tracks

Step 2: Orchestrating agents...
→ Task 1 (setup-websocket): Deploying agent builder-backend...
→ Task 2 (api-endpoints): Blocked by Task 1
→ Task 3 (ui-components): Deploying in parallel (builder-frontend)...
→ Task 4 (testing): Blocked by Tasks 1,2,3

✓ Task 1 completed by builder-backend
→ Task 2 unblocked, deploying agent builder-backend...
✓ Task 3 completed by builder-frontend
✓ Task 2 completed by builder-backend
→ Task 4 unblocked, deploying agent validator...

All tasks completed!

Step 3: Testing...
→ Unit tests: 145 passing ✓
→ Integration tests: 32 passing ✓

Step 4: E2E Testing...
→ User journey: Send message ✓
→ User journey: Receive message ✓
→ User journey: Multi-user chat ✓

Step 5: Review...
→ Implementation matches spec ✓
→ No blockers found ✓

✅ Workflow Complete
Files changed: 23 files, +1,847 lines
```

## Parallel Execution Strategy

**Independent tasks can run in parallel:**

```
         [Task 1: Setup]
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
[Task 2: Backend]  [Task 3: Frontend]
    ↓                   ↓
    └─────────┬─────────┘
              ↓
       [Task 4: Integration]
```

**Set with `run_in_background: true` in Task tool.**

## Exit Conditions

**Success:**
- All tasks in plan completed
- Tests passing (unit + integration + e2e)
- Review finds no blockers
- All acceptance criteria met

**Failure:**
- Tasks fail or block indefinitely
- Tests don't pass
- Review finds blockers
- Acceptance criteria not met

**On failure:** Create patch plan for each issue, queue fixes.

## Orchestration Best Practices

1. **Create tasks first**: Use TaskCreate before deploying any agents
2. **Set dependencies clearly**: Use addBlockedBy for execution order
3. **Monitor progress**: Check TaskList regularly
4. **Communicate**: Keep agents informed via task status updates
5. **Resume wisely**: Use resume parameter for related follow-up work
6. **Validate last**: Always end with validation and review

## Notes

- **Team coordination**: Orchestrator manages 3-10 agents typically
- **Context management**: Each agent has isolated context
- **Parallel efficiency**: 30-50% time savings on suitable tasks
- **Best for**: Complex features requiring multiple specialists

## Related Workflows

- `SimpleSdlc.md` - For single-developer tasks
- `QuickPatch.md` - For rapid fixes
- `FeatureDevelopment.md` - Complete feature lifecycle with documentation
