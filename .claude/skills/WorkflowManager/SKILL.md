---
name: WorkflowManager
description: Manage reusable workflow definitions for agent orchestration. USE WHEN user wants to create workflows, manage workflow files, or organize the workflows directory. USE WHEN user mentions "workflow", "sdlc", "orchestration pattern", or wants to create reusable command sequences.
---

# WorkflowManager

Manages reusable workflow definitions that encode SDLC patterns and command sequences into templates for agent orchestration.

## Workflow Routing

**When executing a workflow, output this notification:**

```
Running **WorkflowName** in **WorkflowManager**...
```

| Workflow | Trigger | File |
|----------|---------|------|
| **Create** | "create workflow", "new workflow", "add workflow" | `Workflows/Create.md` |
| **List** | "list workflows", "show workflows", "what workflows" | `Workflows/List.md` |
| **Canonicalize** | "fix workflow", "organize workflows", "clean workflows" | `Workflows/Canonicalize.md` |
| **Validate** | "validate workflow", "check workflow" | `Workflows/Validate.md` |

## Overview

The workflow system enables creating reusable orchestration patterns that:
- Define sequences of commands (Plan → Implement → Test → Review)
- Specify agent requirements (orchestrator, builders, validators)
- Control parallel vs sequential execution
- Encode SDLC best practices into templates

**Available Workflows:**
- **SimpleSdlc**: Basic plan → implement → test → review (simple features)
- **TeamSdlc**: Team-based orchestration with parallel execution (complex features)
- **QuickPatch**: Rapid bug fix workflow (hotfixes)

**Key Commands:**
- `/create-workflow [Name] "[description]"` - Create new workflow
- `/orchestrate-agents "[objective]" --workflow [WorkflowName]` - Execute workflow
- See `.claude/commands/workflows/README.md` for complete documentation

## Examples

**Example 1: Create a new workflow**
```
User: "Create a workflow for API endpoint development"
→ Invokes Create workflow
→ Prompts for workflow name, description, command sequence
→ Creates file in `.claude/commands/workflows/`
→ Registers in orchestrate-agents command
→ Returns workflow file path and usage example
```

**Example 2: List available workflows**
```
User: "What workflows are available?"
→ Invokes List workflow
→ Reads all workflow files from `.claude/commands/workflows/`
→ Displays table with name, purpose, when to use
→ Shows command sequence for each workflow
```

**Example 3: Fix workflow organization**
```
User: "Clean up the workflows directory"
→ Invokes Canonicalize workflow
→ Ensures only workflow .md files exist (no docs, no backups)
→ Verifies TitleCase naming
→ Updates orchestrate-agents registry if needed
→ Reports cleanup actions taken
```

**Example 4: Validate workflow before use**
```
User: "Validate the TeamSdlc workflow"
→ Invokes Validate workflow
→ Reads `workflows/TeamSdlc.md`
→ Checks command sequence is valid
→ Verifies all referenced commands exist
→ Tests syntax and structure
→ Reports validation status
```

## Workflow File Structure

**Location:** `.claude/commands/workflows/[WorkflowName].md`

**Required sections:**
```markdown
# [WorkflowName] Workflow

[Brief description]

## Purpose
[What this workflow accomplishes]

## When to Use
- Trigger condition 1
- Trigger condition 2

## Command Sequence
| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | command-name | What it does | false |

## Execution Flow
[Detailed explanation]

## Agent Requirements
[What agents are needed]

## Example Usage
```bash
/orchestrate-agents "[objective]" --workflow [WorkflowName]
```

## Notes
[Important considerations]
```

**Naming Convention:** TitleCase.md (e.g., `SimpleSdlc.md`, `TeamSdlc.md`)

**Workflows Directory Must Contain ONLY:**
- Workflow files (*.md)
- README.md (documentation)
- QUICKSTART.md (quick reference)
- SUMMARY.md (overview)
- NO backups, NO temporary files, NO other docs

## Creating Workflows

When user wants to create a workflow:

1. **Gather requirements:**
   - Workflow name (TitleCase)
   - What it does (purpose)
   - When to use (trigger conditions)
   - Command sequence (ordered list)
   - Parallel or sequential execution
   - Agent requirements

2. **Validate command sequence:**
   - Each command must exist in `.claude/commands/`
   - Commands must be executable independently
   - Dependencies between commands must be clear

3. **Create workflow file:**
   - Save to `.claude/commands/workflows/[Name].md`
   - Follow required structure above
   - Include clear usage examples

4. **Register workflow:**
   - Add to `orchestrate-agents.md` workflow table
   - Update workflow count in documentation

## Workflow Design Principles

1. **Reuse Existing Commands** - Workflows should sequence commands, not recreate them
2. **Clear Purpose** - Each workflow has a specific, well-defined use case
3. **Testable** - Easy to test with simple objectives
4. **Documented** - Clearly state when to use vs NOT use
5. **Composable** - Can reference other workflows if needed
6. **Idempotent** - Safe to run multiple times

## Common Workflow Patterns

### Sequential Pattern
```
Command 1 → Command 2 → Command 3
```
Each waits for previous to complete.
Example: `SimpleSdlc`

### Parallel Pattern
```
Command 1 → Command 2   Command 3
              ↓    ↙          ↓    ↙
                 Command 4
```
Independent commands run simultaneously.
Example: `TeamSdlc` (backend + frontend in parallel)

### Diamond Pattern
```
    Command 1
      ↓
Command 2  Command 3
      ↓
    Command 4
```
Parallel work that converges.
Example: Setup foundation → Build components → Integrate

## Managing Workflows Directory

**Directory Rules:**
- **ONLY** workflow .md files allowed (TitleCase naming)
- **MUST** keep README.md, QUICKSTART.md, SUMMARY.md
- **NEVER** store backups in workflows directory
- **NEVER** create temporary files in workflows directory
- **ALWAYS** validate before creating new workflow

**Canonicalization Checklist:**
- [ ] All workflow files use TitleCase.md naming
- [ ] Only workflow files exist (no docs mixed in)
- [ ] Documentation files at root level (README, QUICKSTART, SUMMARY)
- [ ] No backup or temporary files
- [ ] All workflows registered in orchestrate-agents.md
- [ ] Workflow names match file names exactly

## Error Handling

**Common Issues:**

1. **Command not found in workflow**
   - Verify command exists in `.claude/commands/`
   - Check command name is correct (no .md extension)
   - Test command individually before using in workflow

2. **Workflow file in wrong location**
   - Must be in `.claude/commands/workflows/`
   - Not in `.claude/workflows/` or `.claude/skills/`

3. **Parallel steps causing conflicts**
   - Verify tasks are truly independent
   - Check for file write conflicts
   - May need to make sequential

4. **Workflow not registered**
   - Add to orchestrate-agents.md workflow table
   - Update Available Workflows section

## Integration with Orchestration

Workflows are used by `/orchestrate-agents` command:

```bash
# Execute a workflow
/orchestrate-agents "[objective]" --workflow [WorkflowName]

# Custom orchestration (no workflow)
/orchestrate-agents "[objective]"
```

**Workflow Mode:**
- Loads workflow definition
- Executes command sequence exactly
- Follows parallel/sequential strategy
- Uses specified agent types

**Custom Mode:**
- Analyzes requirements
- Designs agent team
- Creates task structure
- Orchestrates execution

## Related Commands

- `/orchestrate-agents` - Execute workflows or custom orchestration
- `/plan` - Create implementation plan
- `/plan_w_team` - Create team-based plan
- `/implement` - Execute a plan
- `/test` - Run test suite
- `/review` - Review against spec
- `/patch` - Create patch plan

## Additional Resources

- `.claude/commands/workflows/README.md` - Complete workflow documentation
- `.claude/commands/workflows/QUICKSTART.md` - Quick start guide
- `.claude/commands/workflows/SUMMARY.md` - System overview
- `.claude/commands/create-workflow.md` - Workflow creation command
- `.claude/commands/orchestrate-agents.md` - Orchestration command
