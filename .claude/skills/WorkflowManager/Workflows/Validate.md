# Validate Workflow

**Purpose:** Validate a workflow file to ensure it's properly structured and all commands exist.

## Voice Notification

```bash
echo "Running **Validate** in **WorkflowManager**..." >&2
```

Running the **Validate** workflow in the **WorkflowManager** skill...

---

## Step 1: Identify Workflow to Validate

**If user specified workflow:**
- Use that workflow name

**If user didn't specify:**
- Ask which workflow to validate
- List available workflows

Example: `Validate the TeamSdlc workflow`

---

## Step 2: Check Workflow File Exists

```bash
workflow_file=".claude/commands/workflows/[WorkflowName].md"

if [[ ! -f "$workflow_file" ]]; then
    echo "❌ Workflow file not found: $workflow_file"
    echo "Available workflows:"
    ls -1 .claude/commands/workflows/*.md | grep -v -E "(README|QUICKSTART|SUMMARY)" | sed 's/.claude\/commands\/workflows\///' | sed 's/\.md$//'
    exit 1
fi
```

---

## Step 3: Validate Structure

Check for required sections:

```bash
echo "Checking structure of $workflow_file..."

# Required sections
sections=(
    "^# .* Workflow"
    "## Purpose"
    "## When to Use"
    "## Command Sequence"
    "## Agent Requirements"
    "## Example Usage"
)

for section in "${sections[@]}"; do
    if grep -q "$section" "$workflow_file"; then
        echo "✅ Found: $section"
    else
        echo "❌ Missing: $section"
    fi
done
```

---

## Step 4: Validate Command Sequence

Extract and validate each command:

```bash
echo "Validating command sequence..."

# Extract command table (between ## Command Sequence and ## Agent Requirements)
sed -n '/## Command Sequence/,/## Agent Requirements/p' "$workflow_file" |
    grep -E '^\|.*\|' |
    tail -n +3 |                   # Skip header rows
    head -n -1 |                   # Skip separator row
    while IFS='|' read -r step cmd desc parallel; do
        cmd=$(echo "$cmd" | xargs)  # Trim whitespace

        echo "Checking command: $cmd"

        # Check if command file exists
        if [[ -f ".claude/commands/${cmd}.md" ]]; then
            echo "  ✅ $cmd exists"
        else
            echo "  ❌ $cmd NOT FOUND in .claude/commands/"
            missing_commands+=("$cmd")
        fi
    done
```

---

## Step 5: Validate Naming

```bash
workflow_name=$(basename "$workflow_file" .md)

# Check TitleCase naming
if [[ ! "$workflow_name" =~ ^[A-Z][a-zA-Z0-9]*$ ]]; then
    echo "❌ Workflow name doesn't use TitleCase: $workflow_name"
    echo "   Expected format: WorkflowName (TitleCase)"
    naming_valid=false
else
    echo "✅ Workflow name uses TitleCase: $workflow_name"
    naming_valid=true
fi
```

---

## Step 6: Validate Registration

```bash
# Check if registered in orchestrate-agents.md
if grep -q "$workflow_name" .claude/commands/orchestrate-agents.md; then
    echo "✅ Workflow is registered in orchestrate-agents.md"
    registered=true
else
    echo "⚠️  Workflow is NOT registered in orchestrate-agents.md"
    echo "   Run /create-workflow to register it, or add manually"
    registered=false
fi
```

---

## Step 7: Check for Common Issues

```bash
echo "Checking for common issues..."

# Check for proper markdown formatting
if grep -q "^# .* Workflow" "$workflow_file"; then
    echo "✅ Has proper workflow header"
else
    echo "❌ Missing workflow header (should be '# WorkflowName Workflow')"
fi

# Check command sequence table format
if grep -q '^\| Step \| Command \|' "$workflow_file"; then
    echo "✅ Command sequence table has proper format"
else
    echo "❌ Command sequence table format is incorrect"
fi

# Check for parallel column
if grep -q '^\|.*\|.*\|.*\| Parallel \|' "$workflow_file"; then
    echo "✅ Has Parallel column in command sequence"
else
    echo "⚠️  Missing Parallel column in command sequence"
fi
```

---

## Step 8: Generate Validation Report

```markdown
## Workflow Validation Report

**Workflow:** [WorkflowName]
**File:** `.claude/commands/workflows/[WorkflowName].md`

### Structure Validation
- ✅/❌ Workflow header
- ✅/❌ Purpose section
- ✅/❌ When to Use section
- ✅/❌ Command Sequence section
- ✅/❌ Agent Requirements section
- ✅/❌ Example Usage section

### Command Validation
[Table of commands and their status]

| Command | Exists | Notes |
|---------|--------|-------|
| [command-1] | ✅/❌ | [notes] |
| [command-2] | ✅/❌ | [notes] |

### Naming Validation
- ✅/❌ Uses TitleCase naming

### Registration Status
- ✅/⚠️ Registered in orchestrate-agents.md

### Overall Status
**[VALID / INVALID / WARNING]**

[If valid]
✅ Workflow is ready to use!

[If invalid)
❌ Workflow has issues that must be fixed:
- [list of issues]

[If warning]
⚠️  Workflow has warnings:
- [list of warnings]

### Recommendations
[Any specific recommendations for fixing issues]
```

---

## Done

Validation complete with status report.
