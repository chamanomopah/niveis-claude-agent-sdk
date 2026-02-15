# QuickPatch Workflow

Rapid bug fix workflow: Diagnose → Create Patch Plan → Apply Patch → Validate

## Purpose

Quickly fix bugs with minimal overhead. Creates targeted surgical patches rather than full implementation plans.

## When to Use

- Bug fixes with clear symptoms
- Small targeted changes
- Hotfixes for production issues
- Quick corrections and tweaks

**NOT for:**
- New features (use SimpleSdlc or TeamSdlc)
- Large refactoring (use proper planning)
- Complex architectural changes

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | patch | Create minimal surgical patch plan | false |
| 2 | implement | Apply the patch | false |
| 3 | test | Validate the fix | false |

## Execution Flow

```
Bug Report
     ↓
[1] patch - Create targeted patch plan:
   - Problem statement
   - Root cause analysis
   - Minimal fix approach
   - Validation steps
     ↓
[2] implement - Apply the patch:
   - Read patch plan
   - Make minimal changes
   - No refactoring beyond fix
     ↓
[3] test - Validate:
   - Run relevant tests
   - Verify bug is fixed
   - Check for regressions
     ↓
Complete
```

## Agent Requirements

**Single agent** that:
- Creates focused patch plan
- Applies minimal changes
- Validates fix worked
- Does NOT refactor beyond the bug fix

**Principle:** Fix the bug, nothing more.

## Example Usage

```bash
/orchestrate-agents "Fix login button not responding on mobile" --workflow QuickPatch
```

**Output:**

```
✅ QuickPatch Workflow Started

Step 1: Creating patch plan...
→ Problem: Login button click handler missing on mobile viewport
→ Root cause: Media query hiding button without updating event listener
→ Fix: Add click handler to mobile-specific button element
→ Plan: specs/patch-login-mobile-button.md

Step 2: Applying patch...
→ Modified: src/components/LoginButton.tsx (+4 lines)
→ Added mobile click handler

Step 3: Validating...
→ Mobile login test: Passing ✓
→ Regression check: Desktop login still works ✓

✅ Workflow Complete
Patch applied and validated
```

## Patch Plan Format

```markdown
# Patch: [brief-name]

## Problem
[What's broken]

## Root Cause
[Why it's broken]

## Solution
[Minimal fix]

## Files to Change
- `path/to/file` - [what to change]

## Validation
[How to verify it works]
```

## Exit Conditions

**Success:**
- Patch applied
- Bug is fixed
- No regressions
- Relevant tests pass

**Failure:**
- Patch doesn't fix the issue
- Creates new bugs
- Can't apply patch cleanly

## Notes

- **Minimal changes**: Only fix the bug, don't refactor
- **Fast execution**: Complete in under 5 minutes typically
- **Low risk**: Small, focused changes
- **Best for**: Quick fixes, hotfixes

## Related Workflows

- `SimpleSdlc.md` - For proper feature development
- `TeamSdlc.md` - For complex fixes
