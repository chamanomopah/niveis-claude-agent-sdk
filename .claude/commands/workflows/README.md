# Workflows Directory

This directory contains reusable workflow definitions for agent orchestration.

## What are Workflows?

Workflows encode SDLC patterns and command sequences into reusable templates. Instead of manually specifying which commands to run and in what order, you can use a predefined workflow that orchestrates the entire process.

## Available Workflows

### SimpleSdlc
**Purpose:** Basic software development lifecycle

**Sequence:** Plan → Implement → Test → Review

**When to use:**
- Simple features
- Bug fixes
- Small refactoring tasks
- Chores

**Usage:**
```bash
/orchestrate-agents "[objective]" --workflow SimpleSdlc
```

---

### TeamSdlc
**Purpose:** Team-based SDLC with parallel execution

**Sequence:** Plan with Team → Orchestrate Agents → Test → E2E Test → Review

**When to use:**
- Medium to high complexity features
- Full-stack development
- Tasks requiring multiple specialists
- Projects that can be parallelized

**Usage:**
```bash
/orchestrate-agents "[objective]" --workflow TeamSdlc
```

---

### QuickPatch
**Purpose:** Rapid bug fix workflow

**Sequence:** Patch Plan → Apply Patch → Validate

**When to use:**
- Bug fixes with clear symptoms
- Hotfixes
- Quick corrections

**Usage:**
```bash
/orchestrate-agents "[objective]" --workflow QuickPatch
```

---

## Creating New Workflows

To create a new workflow:

```bash
/create-workflow [WorkflowName] "[description]"
```

This will:
1. Create a new workflow file in this directory
2. Define the command sequence
3. Specify agent requirements
4. Set parallel/sequential strategy
5. Register the workflow in `orchestrate-agents.md`

## Workflow File Format

Each workflow file follows this structure:

```markdown
# [WorkflowName] Workflow

[Brief description]

## Purpose
[Clear statement of objective]

## When to Use
- Trigger condition 1
- Trigger condition 2
- Trigger condition 3

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | command-name | What this does | false |
| 2 | command-name | What this does | true |

## Execution Flow
[Detailed explanation of command relationships]

## Agent Requirements
[What agents are needed]

## Example Usage
```bash
/orchestrate-agents "[objective]" --workflow [WorkflowName]
```

## Notes
[Important considerations]
```

## Workflow Design Principles

1. **Reuse Existing Commands**: Workflows should sequence existing commands, not recreate functionality
2. **Clear Purpose**: Each workflow should have a specific, well-defined use case
3. **Testable**: Should be easy to test with simple objectives
4. **Documented**: Clearly state when to use vs NOT use
5. **Composable**: Workflows can reference other workflows if needed
6. **Idempotent**: Running multiple times should be safe

## Orchestration Patterns

### Sequential Pattern
```
Command 1 → Command 2 → Command 3
```
Each command waits for the previous to complete.

**Example:** SimpleSdlc

### Parallel Pattern
```
Command 1 → Command 2   Command 3
              ↓    ↙          ↓    ↙
                 Command 4
```
Independent commands run simultaneously.

**Example:** TeamSdlc (backend and frontend in parallel)

### Mixed Pattern
```
Command 1 → Command 2 (parallel) → Command 3
```
Foundation work followed by parallel implementation.

## Related Commands

- `/orchestrate-agents` - Main orchestration command that uses workflows
- `/create-workflow` - Create new workflow definitions
- `/plan` - Create implementation plans
- `/implement` - Execute plans
- `/test` - Run test suite
- `/review` - Review against spec

## Examples

### Example 1: Simple Feature
```bash
/orchestrate-agents "Add user profile page" --workflow SimpleSdlc
```

### Example 2: Complex Feature
```bash
/orchestrate-agents "Build real-time chat with WebSocket" --workflow TeamSdlc
```

### Example 3: Quick Fix
```bash
/orchestrate-agents "Fix mobile navigation menu" --workflow QuickPatch
```

## Workflow Registry

Workflows are automatically registered in `.claude/commands/orchestrate-agents.md` when created.

To manually register a workflow, add it to the "Available Workflows" table in `orchestrate-agents.md`.

## Troubleshooting

**Workflow not found?**
- Check file exists in `.claude/commands/workflows/`
- Verify filename uses TitleCase
- Check workflow is registered in `orchestrate-agents.md`

**Commands in workflow failing?**
- Verify each command exists in `.claude/commands/`
- Test commands individually first
- Check command arguments are correct

**Parallel steps not working?**
- Verify `Parallel: true` is set in workflow
- Check tasks are truly independent
- May need to adjust to sequential if there are dependencies

## See Also

- `.claude/commands/orchestrate-agents.md` - Main orchestration command
- `.claude/commands/create-workflow.md` - Workflow creation command
- `~/.claude/skills_stop/CreateSkill/SKILL.md` - Skill system reference
