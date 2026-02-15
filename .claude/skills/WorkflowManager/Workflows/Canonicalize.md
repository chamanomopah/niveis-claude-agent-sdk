# Canonicalize Workflow

**Purpose:** Organize and clean up the workflows directory. Ensure only workflow files exist with proper TitleCase naming.

## Voice Notification

```bash
echo "Running **Canonicalize** in **WorkflowManager**..." >&2
```

Running the **Canonicalize** workflow in the **WorkflowManager** skill to organize workflows...

---

## Step 1: Scan Workflows Directory

```bash
# List ALL files in workflows directory
find .claude/commands/workflows -type f -name "*.md" | sort
```

---

## Step 2: Identify Issues

Check for:

1. **Non-workflow files** (anything that's not a workflow definition)
   - Documentation files should be at root level
   - No backups in workflows directory
   - No temporary files

2. **Incorrect naming** (not TitleCase)
   - Wrong: `simple-sdlc.md`, `api_workflow.md`, `CREATE.md`
   - Correct: `SimpleSdlc.md`, `ApiWorkflow.md`, `Create.md`

3. **Duplicate or outdated workflows**
   - Multiple versions of same workflow
   - Workflows not registered in orchestrate-agents.md

---

## Step 3: Fix Naming Issues

For each file with incorrect naming:

```bash
# Example rename
cd .claude/commands/workflows
mv old-name.md NewName.md
```

**TitleCase Reference:**
| Type | Wrong | Correct |
|------|-------|---------|
| Single word | `simple.md`, `SIMPLE.md` | `Simple.md` |
| Multiple words | `team-sdlc.md`, `team_sdlc.md` | `TeamSdlc.md` |
| Abbreviations | `api-dev.md` | `ApiDev.md` |

---

## Step 4: Remove Non-Workflow Files

**Files that SHOULD be in workflows directory:**
- `SimpleSdlc.md`
- `TeamSdlc.md`
- `QuickPatch.md`
- Other workflow definitions (TitleCase.md)

**Files that should NOT be in workflows directory:**
- Backups: `*.backup.md`, `*.bak`, `*~`
- Temporary files: `*.tmp`, `*.temp`
- Drafts: `draft-*`, `*draft.md`
- Test files: `test-*.md`
- Documentation (except README.md, QUICKSTART.md, SUMMARY.md at root)

**Action for non-workflow files:**
```bash
# Move to appropriate location or delete
# Backups should go to project backup location, not workflows directory
rm .claude/commands/workflows/*.backup.md
rm .claude/commands/workflows/*.tmp
```

---

## Step 5: Verify Registration

For each workflow file, check it's registered in `.claude/commands/orchestrate-agents.md`:

```bash
# For each workflow file
workflow="[WorkflowName]"
if ! grep -q "$workflow" .claude/commands/orchestrate-agents.md; then
    echo "⚠️  $workflow is NOT registered"
fi
```

**If workflow not registered:**
- Ask user if they want to register it
- Add to Available Workflows table in orchestrate-agents.md

---

## Step 6: Validate Structure

Ensure each workflow has required sections:

```bash
for file in .claude/commands/workflows/*.md; do
    if [[ ! "$file" =~ (README|QUICKSTART|SUMMARY) ]]; then
        echo "Checking $file..."

        # Check for required sections
        grep -q "^# .* Workflow" "$file" || echo "  ❌ Missing workflow header"
        grep -q "## Purpose" "$file" || echo "  ❌ Missing Purpose section"
        grep -q "## When to Use" "$file" || echo "  ❌ Missing When to Use section"
        grep -q "## Command Sequence" "$file" || echo "  ❌ Missing Command Sequence section"
        grep -q "## Agent Requirements" "$file" || echo "  ❌ Missing Agent Requirements section"
        grep -q "## Example Usage" "$file" || echo "  ❌ Missing Example Usage section"
    fi
done
```

---

## Step 7: Report Summary

Provide report of actions taken:

```markdown
## Workflows Directory Canonicalized

### Files Renamed
- `old-name.md` → `NewName.md` (reason)

### Files Removed
- `file.backup.md` (backup file moved)
- `draft-workflow.md` (draft file deleted)

### Workflows Registered
- `WorkflowName` (added to orchestrate-agents.md)

### Structure Validation
✅ All workflows have required sections
✅ All files use TitleCase naming
✅ No backup or temporary files
✅ All workflows registered

### Final State
```
.claude/commands/workflows/
├── README.md
├── QUICKSTART.md
├── SUMMARY.md
├── SimpleSdlc.md
├── TeamSdlc.md
└── QuickPatch.md
```

**Directory is clean and organized!**
```

---

## Done

Workflows directory is canonicalized with proper structure and naming.
