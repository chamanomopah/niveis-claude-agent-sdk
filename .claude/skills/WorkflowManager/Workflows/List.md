# List Workflow

**Purpose:** List all available workflows with their command sequences and usage information.

## Voice Notification

```bash
echo "Running **List** in **WorkflowManager**..." >&2
```

Running the **List** workflow in the **WorkflowManager** skill...

---

## Step 1: Scan Workflows Directory

```bash
# List all workflow files
ls -1 .claude/commands/workflows/*.md 2>/dev/null | grep -v -E "(README|QUICKSTART|SUMMARY)" || echo "No workflows found"
```

---

## Step 2: Extract Workflow Information

For each workflow file found:

1. Read the workflow file
2. Extract:
   - Purpose (from ## Purpose section)
   - When to use (from ## When to Use section)
   - Command sequence (from table in ## Command Sequence section)
   - Agent requirements (from ## Agent Requirements section)

---

## Step 3: Present Workflow Summary

Display in this format:

```markdown
## Available Workflows

Found [N] workflows in `.claude/commands/workflows/`

### [WorkflowName]

**Purpose:** [What it does]

**When to Use:**
- [Condition 1]
- [Condition 2]

**Command Sequence:**
| Step | Command | Parallel |
|------|---------|----------|
| 1 | [command-name] | [yes/no] |
| 2 | [command-name] | [yes/no] |

**Agent Requirements:** [agent types needed]

**Usage:**
```bash
/orchestrate-agents "[objective]" --workflow [WorkflowName]
```

---

[Repeat for each workflow]
```

---

## Step 4: Provide Quick Reference

Also display quick reference table:

```markdown
## Quick Reference

| Workflow | Best For | Complexity | Commands |
|----------|----------|------------|----------|
| [WorkflowName] | [use case] | [Simple/Medium/Complex] | [N] steps |
| [WorkflowName] | [use case] | [Simple/Medium/Complex] | [N] steps |

## Usage Summary

```bash
# Simple features
/orchestrate-agents "[objective]" --workflow SimpleSdlc

# Complex features with team
/orchestrate-agents "[objective]" --workflow TeamSdlc

# Quick fixes
/orchestrate-agents "[objective]" --workflow QuickPatch
```

## Related Commands

- `/create-workflow [Name] "[description]"` - Create new workflow
- See `.claude/commands/workflows/README.md` for complete documentation
```

---

## Done

All workflows listed with their command sequences and usage information.
