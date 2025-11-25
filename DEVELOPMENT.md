# Agent Smith Development Guide

This guide explains the development workflow for the Agent Smith plugin, particularly around the dual-directory architecture.

## Architecture Overview

Agent Smith uses a **source-and-copy architecture** for plugin distribution:

```
agent-smith/
├── scripts/                                    # ✅ SOURCE OF TRUTH (tracked in git)
│   ├── core/                                   # Edit files here
│   ├── health/
│   └── ...
│
└── agent-smith-plugin/skills/agent-smith/
    └── scripts/                                # ❌ BUILD OUTPUT (gitignored)
        ├── core/                               # Gets overwritten by sync
        ├── health/
        └── ...
```

### Why This Architecture?

1. **Clean Git History**: Only source files are tracked, not build artifacts
2. **CI/CD Integration**: Release builds automatically sync source → plugin
3. **Marketplace Distribution**: Plugin directory is self-contained for users

### The Critical Rule

**⚠️ ALWAYS edit files in `/scripts/`, NEVER in `/agent-smith-plugin/.../scripts/`**

Files in the plugin directory are gitignored and will be overwritten during builds!

## Development Workflow

### Option 1: Edit Source + Manual Sync (Recommended)

This is the standard workflow for most development:

1. **Edit source files** in `/scripts/`
   ```bash
   # Edit the source
   vim scripts/health/collector.py
   ```

2. **Sync to plugin** for testing
   ```bash
   ./scripts/dev-sync.sh
   ```

3. **Test using the plugin**
   ```bash
   cd agent-smith-plugin/skills/agent-smith
   uv run python -u scripts/run_health_check.py --quick
   ```

4. **Commit source changes**
   ```bash
   git add scripts/
   git commit -m "feat: update health collector for new rule architecture"
   ```

### Option 2: Symlink During Development (Advanced)

For rapid iteration without manual syncing:

1. **Remove the gitignored plugin scripts directory**
   ```bash
   rm -rf agent-smith-plugin/skills/agent-smith/scripts
   ```

2. **Create a symlink to source**
   ```bash
   cd agent-smith-plugin/skills/agent-smith
   ln -s ../../../../scripts scripts
   ```

3. **Develop directly in `/scripts/`**
   - Changes are immediately visible to the plugin
   - No sync step needed
   - Still edit `/scripts/` (the symlink target)

4. **Before building for distribution:**
   ```bash
   # Remove symlink
   rm agent-smith-plugin/skills/agent-smith/scripts

   # Run normal sync
   ./scripts/dev-sync.sh
   ```

### Option 3: Git Worktrees (For Feature Branches)

Use worktrees to work on multiple features simultaneously:

```bash
# Create a worktree for a new feature
git worktree add ../agent-smith-feature feature/new-health-checks

# Develop in the worktree
cd ../agent-smith-feature
vim scripts/health/new_feature.py

# Sync and test
./scripts/dev-sync.sh

# When done, commit and create PR
git add scripts/
git commit -m "feat: add new health checks"
git push -u origin feature/new-health-checks
```

## The Dev Sync Script

`./scripts/dev-sync.sh` mirrors what CI/CD does during builds:

```bash
# Sync all files (overwrites plugin directory)
./scripts/dev-sync.sh

# See what would be synced without making changes
./scripts/dev-sync.sh --dry-run
```

**What it does:**
- Copies all files from `/scripts/` → `/agent-smith-plugin/.../scripts/`
- Uses `rsync --delete` to remove files not in source
- Ensures plugin directory matches source exactly

## Common Mistakes to Avoid

### ❌ DON'T: Edit Files in Plugin Directory

```bash
# ❌ WRONG - Changes will be lost!
vim agent-smith-plugin/skills/agent-smith/scripts/health/collector.py
```

**Why:** These files are gitignored and get overwritten by CI/CD builds

### ❌ DON'T: Forget to Sync Before Testing

```bash
# ❌ WRONG - Testing outdated code!
vim scripts/health/collector.py
# ... make changes ...
uv run python -u scripts/run_health_check.py  # Still uses old code!
```

**Fix:** Run `./scripts/dev-sync.sh` after editing

### ❌ DON'T: Commit Without Checking Source

```bash
# ❌ WRONG - Plugin files won't be committed!
git add agent-smith-plugin/skills/agent-smith/scripts/
git commit -m "Update health checks"  # Changes not in git!
```

**Fix:** Only commit `/scripts/` directory

## CI/CD Pipeline

The GitHub Actions workflow handles syncing during releases:

```yaml
# .github/workflows/main-ci-cd.yml (line 183)
# Copy source code and commands
cp -r scripts "${PLUGIN_DIR}/"
```

**When it runs:**
- On pushes to `main` branch
- During release tagging
- Creates plugin packages for distribution

**What it does:**
1. Runs tests on `/scripts/` (source)
2. Creates a clean plugin directory
3. Copies `/scripts/` → plugin package
4. Builds `.tar.gz` and `.zip` distributions

## Testing Your Changes

### Unit Tests

Test source code directly:

```bash
pytest tests/unit -v
```

### Integration Tests

```bash
pytest tests/integration -v -m integration
```

### Manual Testing

1. Edit source in `/scripts/`
2. Sync to plugin: `./scripts/dev-sync.sh`
3. Test via plugin:
   ```bash
   cd agent-smith-plugin/skills/agent-smith
   uv run python -u scripts/run_health_check.py --full
   ```

## Git Workflow

Agent Smith uses branch protection and PR-based development:

```bash
# 1. Create feature branch
git checkout -b feature/improve-health-checks

# 2. Edit source files
vim scripts/health/collector.py

# 3. Sync for testing
./scripts/dev-sync.sh

# 4. Test
uv run pytest tests/

# 5. Commit source changes
git add scripts/
git commit -m "feat: improve health check for unified rules"

# 6. Push and create PR
git push -u origin feature/improve-health-checks
gh pr create --fill

# 7. Wait for CI validation
# 8. Squash and merge
```

## Quick Reference

| Task | Command |
|------|---------|
| Edit code | `vim scripts/some_file.py` |
| Sync to plugin | `./scripts/dev-sync.sh` |
| Dry-run sync | `./scripts/dev-sync.sh --dry-run` |
| Run tests | `pytest tests/ -v` |
| Test health check | `uv run python -u scripts/run_health_check.py` |
| Format code | `black scripts/ tests/` |
| Lint | `flake8 scripts/ tests/` |
| Type check | `mypy scripts/` |

## Troubleshooting

### "My changes disappeared!"

**Cause:** Edited files in the gitignored plugin directory

**Fix:**
1. Check git status: `git status`
2. If no changes shown, check plugin directory for orphaned edits
3. Copy changes back: `cp agent-smith-plugin/.../scripts/FILE scripts/FILE`
4. Sync properly: `./scripts/dev-sync.sh`

### "Tests are failing but my code works"

**Cause:** Forgot to sync before testing

**Fix:**
```bash
./scripts/dev-sync.sh
pytest tests/
```

### "Git shows no changes but I edited files"

**Cause:** Edited gitignored files instead of source

**Fix:**
1. Find the edited files in `agent-smith-plugin/.../scripts/`
2. Copy to source: `cp plugin/path/file scripts/path/file`
3. Verify: `git status` should now show changes

## Summary

**The Golden Rule of Agent Smith Development:**

> Edit `/scripts/`, sync to `/agent-smith-plugin/.../scripts/`, commit `/scripts/`

Follow this workflow and you'll never lose work!

---

**Questions?** See [CONTRIBUTING.md](CONTRIBUTING.md) or [CLAUDE.md](CLAUDE.md)
