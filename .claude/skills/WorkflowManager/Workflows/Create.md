# Create Workflow

**Purpose:** Create a new reusable workflow definition for agent orchestration.

## Voice Notification

```bash
echo "Running **Create** in **WorkflowManager**..." >&2
```

Running the **Create** workflow in the **WorkflowManager** skill...

---

## Step 1: Gather Workflow Requirements

Ask the user for:

1. **Workflow Name** (TitleCase, required)
   - Example: "ApiDevelopment", "DatabaseMigration", "FeatureLifecycle"
   - Must use TitleCase (PascalCase)
   - No spaces, hyphens, or underscores

2. **Purpose** (required)
   - What does this workflow accomplish?
   - Clear, concise statement

3. **When to Use** (required)
   - Trigger conditions (2-4 items)
   - When NOT to use (1-2 items)

4. **Command Sequence** (required)
   - Ordered list of commands to execute
   - Each command must exist in `.claude/commands/`
   - Mark which steps can run in parallel

5. **Agent Requirements** (required)
   - What type of agents are needed?
   - Orchestrator, builders, validators?
   - Any special requirements?

6. **Description** (optional)
   - Any additional context or notes

If any required information is missing, STOP and ask the user.

---

## Step 2: Validate Command Sequence

For each command in the sequence:

```bash
# Check if command exists
test -f ".claude/commands/[command-name].md"
```

**Validation rules:**
- Each command must exist in `.claude/commands/`
- Commands must be executable
- Dependencies must be clear
- Parallel steps must be truly independent

**If any command is missing:**
- Inform user which commands don't exist
- Suggest alternatives or ask to create missing commands first
- DO NOT proceed until all commands are validated

---

## Step 3: Check for Existing Workflow

```bash
# Check if workflow already exists
test -f ".claude/commands/workflows/[WorkflowName].md"
```

**If workflow exists:**
- Inform user it already exists
- Ask if they want to:
  - Overwrite (backup existing first)
  - Create with different name
  - Cancel

---

## Step 4: Create Workflow File

Create `.claude/commands/workflows/[WorkflowName].md` with:

```markdown
# [WorkflowName] Workflow

[Purpose description from user]

## Purpose

[Detailed purpose statement]

## When to Use

- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

**NOT for:**
- [When NOT to use 1]
- [When NOT to use 2]

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | [command-1] | [description] | [true/false] |
| 2 | [command-2] | [description] | [true/false] |
| 3 | [command-3] | [description] | [true/false] |

## Execution Flow

[Detailed explanation of how commands relate]
[Include diagram if helpful]

## Agent Requirements

[What type of agents needed]
[Orchestrator requirements]
[Specialist requirements]

## Example Usage

```bash
/orchestrate-agents "[example objective]" --workflow [WorkflowName]
```

**Output:**
[What user should expect]

## Notes

[Any important notes, dependencies, or special considerations]
```

---

## Step 5: Register Workflow

Update `.claude/commands/orchestrate-agents.md`:

1. **Add to Available Workflows table:**

Find this section in orchestrate-agents.md:
```markdown
## Available Workflows

| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| **SimpleSdlc** | ... | ...
| **TeamSdlc** | ... | ...
| **QuickPatch** | ... | ... |
```

Add new row:
```markdown
| **[WorkflowName]** | [brief purpose] | [when to use] |
```

2. **Update workflow count** (if mentioned in file)

---

## Step 6: Validate Workflow

Run validation checks:

```bash
# File exists
test -f ".claude/commands/workflows/[WorkflowName].md"

# File has required sections
grep -q "## Purpose" ".claude/commands/workflows/[WorkflowName].md"
grep -q "## When to Use" ".claude/commands/workflows/[WorkflowName].md"
grep -q "## Command Sequence" ".claude/commands/workflows/[WorkflowName].md"
grep -q "## Agent Requirements" ".claude/commands/workflows/[WorkflowName].md"
grep -q "## Example Usage" ".claude/commands/workflows/[WorkflowName].md"

# Workflow is registered
grep -q "[WorkflowName]" ".claude/commands/orchestrate-agents.md"
```

---

## Step 7: Report Success

Provide summary:

```markdown
## Workflow Created Successfully

**Name:** [WorkflowName]
**File:** `.claude/commands/workflows/[WorkflowName].md`

### Command Sequence
[Summary of commands in order]

### Usage
```bash
/orchestrate-agents "[your objective]" --workflow [WorkflowName]
```

### Next Steps
1. Test the workflow with a simple objective
2. Refine command sequence based on results
3. Document any special patterns or considerations

### Registration
✅ Workflow registered in orchestrate-agents.md
✅ Ready to use
```

---

## Done

Workflow created, validated, and registered. Ready to use with `/orchestrate-agents`.
