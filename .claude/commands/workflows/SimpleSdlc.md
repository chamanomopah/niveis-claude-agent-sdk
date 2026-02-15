# SimpleSdlc Workflow

Basic software development lifecycle for simple features and fixes: Plan → Implement → Review

## Purpose

Execute a simple, linear SDLC process suitable for straightforward features, bug fixes, and chores that don't require team orchestration.

## When to Use

- Single-developer tasks (simple to medium complexity)
- Bug fixes with clear root cause
- Small feature additions
- Refactoring tasks
- Chore work

**NOT for:**
- Complex features requiring multiple specialists
- Tasks requiring parallel execution
- Large-scale refactoring

## Command Sequence

| Step | Command | Description | Parallel |
|------|---------|-------------|----------|
| 1 | plan | Create implementation plan based on requirements | false |
| 2 | implement | Execute the plan step by step | false |
| 3 | test | Run test suite to validate implementation | false |
| 4 | review | Review implementation against original spec | false |

## Execution Flow

```
User Request
     ↓
[1] plan - Analyze requirements, create plan in specs/
     ↓
[2] implement - Read plan, execute tasks sequentially
     ↓
[3] test - Run validation commands, check acceptance criteria
     ↓
[4] review - Compare implementation to spec, classify any issues
     ↓
Complete (or patch if blockers found)
```

## Agent Requirements

**Single orchestrator agent** that:
- Reads the workflow definition
- Executes each command in sequence
- Waits for each command to complete before next
- Handles any errors or blockers found
- Reports final status

**No subagent delegation needed** - commands handle their own execution.

## Example Usage

```bash
/orchestrate-agents "Add password reset feature" --workflow SimpleSdlc
```

**Output:**

```
✅ SimpleSdlc Workflow Started

Step 1: Planning...
→ Plan created: specs/password-reset-feature.md

Step 2: Implementing...
→ Password reset email implemented
→ Token generation added
→ API endpoint created

Step 3: Testing...
→ All tests passing ✓
→ Acceptance criteria met ✓

Step 4: Review...
→ Implementation matches spec ✓
→ No blockers found ✓

✅ Workflow Complete
```

## Exit Conditions

**Success:**
- All commands execute without errors
- Tests pass
- Review finds no blockers

**Failure:**
- Any command fails
- Tests don't pass
- Review finds blocker issues

**On failure:** Automatically invoke `/patch` workflow to create targeted fix.

## Notes

- **Linear execution**: Each step must complete before next begins
- **Fast feedback**: Issues caught early in the cycle
- **Minimal overhead**: No team coordination needed
- **Best for**: 70% of typical development tasks

## Related Workflows

- `TeamSdlc.md` - For complex, multi-agent tasks
- `QuickPatch.md` - For rapid bug fixes
- `FeatureDevelopment.md` - For full feature lifecycle
