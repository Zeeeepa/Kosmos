# Git Worktree Setup for Parallel Bug Fixing

**Purpose:** Enable two AI models to work simultaneously on different bugs without merge conflicts
**Date:** 2025-11-19

## Overview

Git worktrees allow multiple working directories from the same repository, enabling:
- Parallel development without branch switching
- Independent commits and pushes
- Clean separation of work
- No risk of accidentally modifying the wrong branch

## Initial Setup Commands

### For Web Model

```bash
# 1. Navigate to main repository
cd /mnt/c/python/Kosmos

# 2. Ensure main branch is up to date
git checkout main
git pull origin main

# 3. Create Web model worktree
git worktree add ../kosmos-web-fixes --detach origin/main

# 4. Enter the worktree
cd ../kosmos-web-fixes

# 5. Create unique branch with timestamp
git checkout -b web-bugfix-$(date +%Y%m%d-%H%M%S)

# 6. Push branch to remote
git push -u origin HEAD

# 7. Verify setup
pwd  # Should show: /mnt/c/python/kosmos-web-fixes
git branch --show-current  # Should show: web-bugfix-[timestamp]
git remote -v  # Should show origin pointing to GitHub
```

### For CLI Model

```bash
# 1. Navigate to main repository
cd /mnt/c/python/Kosmos

# 2. Ensure main branch is up to date
git checkout main
git pull origin main

# 3. Create CLI model worktree
git worktree add ../kosmos-cli-fixes --detach origin/main

# 4. Enter the worktree
cd ../kosmos-cli-fixes

# 5. Create unique branch with timestamp
git checkout -b cli-bugfix-$(date +%Y%m%d-%H%M%S)

# 6. Push branch to remote
git push -u origin HEAD

# 7. Verify setup
pwd  # Should show: /mnt/c/python/kosmos-cli-fixes
git branch --show-current  # Should show: cli-bugfix-[timestamp]
git remote -v  # Should show origin pointing to GitHub
```

## Directory Structure After Setup

```
/mnt/c/python/
├── Kosmos/                 # Original repository
│   ├── .git/              # Main git directory
│   ├── kosmos/            # Source code
│   └── tests/             # Tests
├── kosmos-web-fixes/       # Web model worktree
│   ├── .git               # File pointing to main .git
│   ├── kosmos/            # Independent working copy
│   └── tests/             # Independent working copy
└── kosmos-cli-fixes/       # CLI model worktree
    ├── .git               # File pointing to main .git
    ├── kosmos/            # Independent working copy
    └── tests/             # Independent working copy
```

## Branch Naming Convention

### Format
```
{model}-{severity}-{component}-{timestamp}
```

### Examples
```bash
# Web model branches
web-bugfix-20251119-143022           # Main branch
web-critical-world-model              # Critical world_model fixes
web-high-llm                         # High priority LLM fixes
web-medium-interactive                # Medium priority interactive fixes

# CLI model branches
cli-bugfix-20251119-143045           # Main branch
cli-critical-result-collector         # Critical database fix
cli-high-knowledge                    # High priority knowledge fixes
cli-medium-sandbox                    # Medium priority sandbox fixes
```

## Working in Your Worktree

### Basic Workflow

```bash
# 1. Always work from your worktree directory
cd ../kosmos-web-fixes  # For Web model
cd ../kosmos-cli-fixes  # For CLI model

# 2. Make changes and test
# Edit files...
pytest tests/unit/[module] -v

# 3. Commit with descriptive message
git add [files]
git commit -m "Fix [component]: [description] (Bug #X)"

# 4. Push to your branch
git push origin HEAD
```

### Creating Feature Branches

When working on critical coordinated fixes:

```bash
# Create feature branch for specific fix
git checkout -b [model]-critical-[component]

# Example for Web model:
git checkout -b web-critical-world-model

# Example for CLI model:
git checkout -b cli-critical-result-collector

# Push the feature branch
git push -u origin HEAD
```

## Synchronization Points

### Checking Other Model's Progress

```bash
# Fetch latest from remote without switching
git fetch origin

# See all remote branches
git branch -r | grep -E "web-|cli-"

# Check if specific branch exists
git ls-remote origin | grep "web-critical-world-model"

# View commits from other model
git log origin/web-critical-world-model --oneline -5
git log origin/cli-critical-result-collector --oneline -5

# See what files were changed
git diff --name-only origin/main..origin/web-critical-world-model
```

### Pulling Other Model's Changes

When you need to build on the other model's work:

```bash
# 1. Fetch latest changes
git fetch origin

# 2. Merge or rebase (if approved)
git checkout main
git pull origin main

# 3. Create new branch based on updated main
git checkout -b [model]-[next-fix]

# Or rebase your branch
git checkout [your-branch]
git rebase origin/main
```

## Merge Strategy

### Order of Operations

```markdown
Phase 1: Independent Work (Parallel)
├── Web: Config, dependencies, safety modules
└── CLI: Test imports, knowledge modules, literature APIs

Phase 2: Sequential Coordination
├── Step 1: Web completes world_model fixes
├── Step 2: Web's PR merged to main
├── Step 3: CLI pulls main and applies world_model fixes
├── Step 4: CLI's PR merged to main
└── Continue pattern for other shared files
```

### Creating Pull Requests

```bash
# 1. Push your branch
git push origin HEAD

# 2. Create PR via GitHub CLI (if installed)
gh pr create --title "Fix [component]: [description]" \
             --body "Fixes bugs #X, #Y, #Z from [WEB|CLI]_BASED_BUGS.md" \
             --base main

# 3. Or create via GitHub web interface
echo "https://github.com/jimmc414/Kosmos/compare/main...$(git branch --show-current)"
```

## Handling Conflicts

### If Conflicts Occur During Development

```bash
# 1. Fetch latest changes
git fetch origin main

# 2. Attempt rebase
git rebase origin/main

# 3. If conflicts appear:
# Fix conflicts in editor
git add [resolved-files]
git rebase --continue

# 4. Or abort if needed
git rebase --abort
```

### Coordinating on Shared Files

For files that both models need to modify:

```bash
# Web Model (goes first for certain files)
git checkout -b web-critical-world-model
# Make changes to lines 144-176
git commit -m "Fix world model: create_paper, create_concept"
git push origin HEAD
# Create PR and notify CLI model

# CLI Model (waits, then proceeds)
# Wait for Web's PR to be merged
git fetch origin
git checkout main
git pull origin main
git checkout -b cli-critical-world-model
# Make changes to lines 193-451
git commit -m "Fix world model: create_author, create_method, create_citation"
git push origin HEAD
```

## Cleanup After Completion

### Removing Worktrees

```bash
# After all fixes are merged

# 1. Return to main repository
cd /mnt/c/python/Kosmos

# 2. List all worktrees
git worktree list

# 3. Remove worktrees
git worktree remove ../kosmos-web-fixes
git worktree remove ../kosmos-cli-fixes

# 4. Prune worktree information
git worktree prune

# 5. Clean up remote branches
git push origin --delete web-bugfix-[timestamp]
git push origin --delete cli-bugfix-[timestamp]
```

## Troubleshooting

### Common Issues and Solutions

```bash
# Issue: "fatal: branch already exists"
# Solution: Use unique timestamp
git checkout -b web-bugfix-$(date +%Y%m%d-%H%M%S)

# Issue: "worktree already exists"
# Solution: Remove old worktree first
git worktree remove ../kosmos-web-fixes

# Issue: "Cannot delete branch checked out at..."
# Solution: Switch to different branch first
git checkout main
git branch -d [old-branch]

# Issue: Push rejected - non-fast-forward
# Solution: Pull and rebase
git pull --rebase origin main
git push origin HEAD

# Issue: Worktree directory not found
# Solution: Recreate worktree
git worktree prune
git worktree add ../kosmos-web-fixes origin/main
```

## Best Practices

1. **Always verify your location**
   ```bash
   pwd  # Check you're in the right worktree
   git branch --show-current  # Check correct branch
   ```

2. **Commit frequently**
   - Small, focused commits are easier to merge
   - One bug fix per commit when possible

3. **Test before pushing**
   ```bash
   pytest tests/unit/[affected-module] -v
   mypy kosmos/[affected-module] --ignore-missing-imports
   ```

4. **Communicate at checkpoints**
   - Before starting shared files
   - After completing critical fixes
   - When ready for integration

5. **Keep main branch clean**
   - Never commit directly to main
   - Always work in feature branches
   - Merge via pull requests

## Quick Reference

### Web Model Commands
```bash
cd ../kosmos-web-fixes            # Enter worktree
git status                        # Check changes
git add -p                        # Stage changes interactively
git commit -m "Fix: ..."         # Commit
git push origin HEAD              # Push to remote
git fetch origin                  # Get latest changes
git log --oneline -5             # Recent commits
```

### CLI Model Commands
```bash
cd ../kosmos-cli-fixes            # Enter worktree
pytest tests/ -v --tb=short       # Run tests
git diff HEAD                     # View changes
git commit -am "Fix: ..."        # Add and commit
git push origin HEAD              # Push to remote
git branch -r | grep web-         # See Web branches
git pull origin main              # Update from main
```

## Communication Protocol

### Status Updates Format
```markdown
Model: [Web|CLI]
Current: Bug #X - [component]
Completed: Bugs #A, #B, #C
Blocked: Waiting for [Web|CLI] Bug #Y
Next: Bug #Z
```

### Coordination Messages
```markdown
"READY: web-critical-world-model pushed, ready for review"
"WAITING: Need cli-critical-result-collector before proceeding"
"COMPLETE: All Phase 1 bugs fixed, starting Phase 2"
"HELP: Conflict in [file], need coordination"
```

This setup ensures both models can work efficiently in parallel while maintaining code integrity and preventing merge conflicts.