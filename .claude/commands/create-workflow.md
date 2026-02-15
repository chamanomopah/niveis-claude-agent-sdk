---
description: Create reusable workflow definitions for agent orchestration. Workflows define the sequence of commands/tools to execute specific objectives.
argument-hint: [workflow-name] [workflow-description]
model: opus
allowed-tools: Read, Write, Glob
---

# Create Workflow

Create reusable workflow definitions that can be orchestrated by commands like `orchestrate-agents.md`. Workflows encode SDLC patterns and command sequences into reusable templates.

## Arguments

- `$1`: **WORKFLOW_NAME** - TitleCase name for the workflow (required)
- `$ARGUMENTS`: **DESCRIPTION** - What this workflow does and when to use it

## Instructions

### Step 1: Understand the Request

Extract:
- Workflow name from `$1` (required, must use TitleCase)
- Purpose and description from remaining arguments
- Command sequence needed
- When this workflow should be used

If no name provided, STOP and ask for workflow name.

### Step 2: Determine Command Sequence

**Workflows are composed of existing commands.**

Identify which commands should execute in sequence:
- Planning commands: `/plan`, `/plan_w_team`
- Implementation: `/implement`, `/patch`
- Validation: `/test`, `/test-e2e`, `/review`
- Orchestration: `/orchestrate-agents`

**Example SDLC workflow:**
```yaml
commands:
  - step: 1
    command: plan
    description: "Create implementation plan"
  - step: 2
    command: implement
    description: "Execute the plan"
  - step: 3
    command: test
    description: "Run tests"
  - step: 4
    command: review
    description: "Review against spec"
```

### Step 3: Design Workflow Structure

Based on the workflow complexity, determine:

**Simple Workflow:**
- Linear command sequence
- Each command waits for previous to complete
- Single orchestrator agent

**Parallel Workflow:**
- Multiple commands run simultaneously
- Independent task tracks
- Requires coordination

**Complex Workflow:**
- Mix of sequential and parallel
- Conditional execution
- Multiple agent types

### Step 4: Create Workflow File

Save to: `.claude/commands/workflows/[WorkflowName].md`

**Workflow File Format:**

```markdown
# [WorkflowName] Workflow

[Description of what this workflow does]

## Purpose

[Clear statement of the workflow's objective]

## When to Use

- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | [command-name] | [what this step does] | false |
| 2 | [command-name] | [what this step does] | false |
| 3 | [command-name] | [what this step does] | true |

## Execution Flow

[Detailed explanation of how commands relate to each other]

## Agent Requirements

[What type of agents are needed for this workflow]

## Example Usage

```bash
/[orchestration-command] "[objective]" --workflow [WorkflowName]
```

**Output:**
[What the user should expect]

## Notes

[Any important notes, dependencies, or special considerations]
```

### Step 5: Validate Workflow

**Checklist:**

- [ ] Workflow name uses TitleCase
- [ ] File saved to correct location: `.claude/commands/workflows/`
- [ ] Command sequence is clear and executable
- [ ] Each command exists in `.claude/commands/`
- [ ] Parallel/Sequential execution is specified
- [ ] Agent requirements are documented
- [ ] Usage examples are provided
- [ ] File uses TitleCase.md naming

### Step 6: Register Workflow

Add to orchestration command's workflow registry.

**In `orchestrate-agents.md`:**

Add entry to workflow routing table:

```markdown
## Available Workflows

| Workflow | Purpose | File |
|----------|---------|------|
| [WorkflowName] | [brief description] | `workflows/[WorkflowName].md` |
```

## Workflow Templates

### Template 1: Simple SDLC

```markdown
# SimpleSdlc Workflow

Basic software development lifecycle: Plan → Implement → Review

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | plan | Create implementation plan | false |
| 2 | implement | Execute the plan | false |
| 3 | test | Run test suite | false |
| 4 | review | Review against spec | false |

## Agent Requirements

- Single orchestrator agent
- General-purpose subagents for each step
```

### Template 2: Team SDLC

```markdown
# TeamSdlc Workflow

Team-based SDLC with parallel execution: Plan → Parallel Implementation → Test → Review

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | plan_w_team | Create team-based plan | false |
| 2 | orchestrate-agents | Orchestrate team implementation | false |
| 3 | test | Run test suite | false |
| 4 | review | Review against spec | false |

## Agent Requirements

- Orchestrator agent (team lead)
- Multiple specialist agents (parallel execution)
- Validator agent
```

### Template 3: Patch Flow

```markdown
# QuickPatch Workflow

Quick fix workflow: Diagnose → Patch → Validate

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | patch | Create patch plan | false |
| 2 | implement | Apply patch | false |
| 3 | test | Validate fix | false |

## Agent Requirements

- Single orchestrator
- Builder agent
- Tester agent
```

## Output

After creating the workflow, provide:

```markdown
## Workflow Created

**Name:** [WorkflowName]
**File:** `.claude/commands/workflows/[WorkflowName].md`

### Command Sequence

[Summary of commands in order]

### Usage

```bash
/orchestrate-agents "[objective]" --workflow [WorkflowName]
```

### Next Steps

1. Test the workflow with a simple objective
2. Refine command sequence based on results
3. Document any special patterns or considerations
```

## Notes

- Workflows should be reusable across different objectives
- Each command in the sequence must exist in `.claude/commands/`
- Workflows define the "what" and "order", orchestration handles the "how"
- Complex workflows may need conditional logic or error handling
- Always test workflows with simple objectives before complex ones
