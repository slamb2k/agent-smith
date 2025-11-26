# Ship Command

Ship current changes: manage branches, bump versions, commit, push, and create/update PR.

## Arguments
- `$ARGUMENTS` - Optional: version bump type (patch|minor|major, default: patch) and/or commit message hint

## Workflow

Execute the following steps in order. Stop and fix any errors before continuing.

### Step 1: Analyze Current State

Run these commands to understand the current git state:

```bash
# Get current branch
git branch --show-current

# Check for uncommitted changes
git status --porcelain

# Check if we're on main
git branch --show-current | grep -q "^main$" && echo "ON_MAIN" || echo "ON_FEATURE"
```

### Step 2: Branch Management

**If on `main` branch:**

1. Stash any uncommitted changes:
   ```bash
   git stash --include-untracked -m "ship-command-autostash"
   ```

2. Pull latest from origin:
   ```bash
   git pull origin main --rebase
   ```

3. Generate a feature branch name based on the changes being shipped (use format `feature/<descriptive-name>`):
   ```bash
   git checkout -b feature/<branch-name>
   ```

4. Unstash changes if there were any:
   ```bash
   git stash pop
   ```

**If on a feature branch:**

1. Check PR status:
   ```bash
   gh pr view --json state,number,url 2>/dev/null || echo "NO_PR"
   ```

2. **If PR is OPEN**: Continue with the existing branch (proceed to Step 3)

3. **If PR is CLOSED/MERGED or NO_PR exists**:
   - Stash any changes:
     ```bash
     git stash --include-untracked -m "ship-command-autostash"
     ```
   - Switch to main and update:
     ```bash
     git checkout main
     git pull origin main --rebase
     ```
   - Create a new feature branch:
     ```bash
     git checkout -b feature/<new-descriptive-name>
     ```
   - Unstash changes:
     ```bash
     git stash pop
     ```

### Step 3: Version Bump

Determine bump type from `$ARGUMENTS` (default: `patch`).

1. Read current versions:
   ```bash
   grep -E '^version = "' pyproject.toml
   grep -E '"version":' agent-smith-plugin/.claude-plugin/plugin.json
   ```

2. Calculate new version (semver: MAJOR.MINOR.PATCH):
   - `patch`: increment PATCH (e.g., 1.5.0 -> 1.5.1)
   - `minor`: increment MINOR, reset PATCH (e.g., 1.5.0 -> 1.6.0)
   - `major`: increment MAJOR, reset MINOR and PATCH (e.g., 1.5.0 -> 2.0.0)

3. Update `pyproject.toml`:
   ```bash
   sed -i 's/^version = ".*"/version = "<NEW_VERSION>"/' pyproject.toml
   ```

4. Update `agent-smith-plugin/.claude-plugin/plugin.json`:
   ```bash
   sed -i 's/"version": ".*"/"version": "<NEW_VERSION>"/' agent-smith-plugin/.claude-plugin/plugin.json
   ```

5. Verify updates:
   ```bash
   grep -E '^version = "' pyproject.toml
   grep -E '"version":' agent-smith-plugin/.claude-plugin/plugin.json
   ```

### Step 4: Sync Plugin Scripts

Sync source scripts to the plugin directory (plugin scripts are gitignored copies):

```bash
./scripts/dev-sync.sh
```

This ensures the plugin has the latest script changes. The sync copies from:
- Source: `/scripts/` (tracked in git)
- Target: `/agent-smith-plugin/skills/agent-smith/scripts/` (gitignored)

### Step 5: Stage and Commit

1. Stage all changes:
   ```bash
   git add -A
   ```

2. Review what will be committed:
   ```bash
   git diff --cached --stat
   ```

3. Generate a semantic commit message based on the changes:
   - Analyze the staged diff to determine the commit type:
     - `feat:` - New feature
     - `fix:` - Bug fix
     - `refactor:` - Code refactoring
     - `docs:` - Documentation only
     - `chore:` - Maintenance tasks
     - `perf:` - Performance improvement
     - `test:` - Adding/updating tests
   - Include the version bump in the message
   - Format: `<type>: <description>\n\n<detailed bullet points>\n\nBumps version to <NEW_VERSION>`

4. Commit with the generated message:
   ```bash
   git commit -m "<semantic-commit-message>"
   ```

### Step 6: Handle Pre-commit Hook Failures

If the commit fails due to pre-commit hooks:

1. Check what failed:
   ```bash
   git status
   ```

2. If files were auto-formatted (black, prettier, etc.):
   - Stage the reformatted files:
     ```bash
     git add -A
     ```
   - Retry the commit with `--no-verify` ONLY if the hooks made the fixes:
     ```bash
     git commit -m "<semantic-commit-message>"
     ```

3. If there are actual errors (lint errors, type errors):
   - Fix the errors in the code
   - Stage the fixes
   - Retry the commit

4. **IMPORTANT**: Loop until commit succeeds. Do not proceed until committed.

### Step 7: Push to Remote

1. Push the branch (set upstream if needed):
   ```bash
   git push -u origin HEAD
   ```

### Step 8: Handle Pre-push Hook Failures

If push fails due to pre-push hooks:

1. Identify the failures from the hook output

2. Fix any issues (tests, builds, etc.)

3. Amend the commit if needed:
   ```bash
   git add -A
   git commit --amend --no-edit
   ```

4. Retry push:
   ```bash
   git push -u origin HEAD --force-with-lease
   ```

5. **IMPORTANT**: Loop until push succeeds. Do not proceed until pushed.

### Step 9: Create or Update PR

1. Check if PR already exists:
   ```bash
   gh pr view --json number,url 2>/dev/null
   ```

2. **If NO PR exists**, create one:

   a. Generate a detailed PR description based on:
      - The commits on the branch
      - The files changed
      - The version bump

   b. Create the PR:
      ```bash
      gh pr create \
        --title "<semantic-type>: <concise-description>" \
        --body "$(cat <<'EOF'
      ## Summary
      <2-4 bullet points describing the changes>

      ## Changes
      <list of specific changes made>

      ## Version
      Bumps version from X.Y.Z to A.B.C

      ## Test Plan
      - [ ] <verification steps>

      ---
      Generated with [Claude Code](https://claude.ai/code)
      EOF
      )"
      ```

   c. Enable auto-merge with squash:
      ```bash
      gh pr merge --auto --squash
      ```

3. **If PR exists**, it will be updated automatically by the push.

### Step 10: Generate Report

Output a detailed report in this format:

```
============================================================
                    SHIP REPORT
============================================================

Branch:        <branch-name>
Previous:      <previous-branch-if-changed>
Version:       <old-version> -> <new-version>
Bump Type:     <patch|minor|major>

------------------------------------------------------------
                      COMMITS
------------------------------------------------------------
<commit-hash-short> <commit-message>

------------------------------------------------------------
                    FILES CHANGED
------------------------------------------------------------
<file-change-summary>

------------------------------------------------------------
                   HOOK RESULTS
------------------------------------------------------------
Pre-commit:    <PASSED|FIXED (n iterations)|N/A>
Pre-push:      <PASSED|FIXED (n iterations)|N/A>

------------------------------------------------------------
                   PULL REQUEST
------------------------------------------------------------
Status:        <CREATED|UPDATED|EXISTING>
Auto-merge:    <ENABLED|ALREADY SET|N/A>

>>> PR URL: <full-github-pr-url> <<<

============================================================
```

## Error Handling

- If any git operation fails unexpectedly, stop and report the error
- If hooks fail more than 5 times, stop and ask for user intervention
- If PR creation fails, provide the gh command output for debugging
- Never skip pre-commit or pre-push hooks unless they auto-fixed issues

## Notes

- This command follows the project's git workflow conventions
- Uses semantic versioning (semver)
- Uses conventional/semantic commit messages
- Squash merge is enforced for clean history
- Auto-merge is enabled to merge once CI passes
