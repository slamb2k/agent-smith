# Ship Command

Ship current changes: manage branches, bump versions, commit, push, and create/update PR.

## Arguments
- `$ARGUMENTS` - Optional: version bump type (patch|minor|major, default: patch)

## Execution

**IMPORTANT: Delegate ALL work to a subagent to preserve main context window.**

Use the Task tool with `subagent_type: "general-purpose"` to execute the shipping workflow:

```
Task(
  subagent_type: "general-purpose",
  description: "Ship changes workflow",
  prompt: <full prompt below>
)
```

### Subagent Prompt

You are the Ship Agent. Execute the shipping workflow with visual progress indicators.

**Arguments received:** $ARGUMENTS (default bump type: patch)

## Visual Style Guide

Use these indicators throughout:
- Step headers: `🚀 STEP N: Title`
- Success: `✅`
- In progress: `⏳`
- Warning: `⚠️`
- Error: `❌`
- Info: `📋`
- Git: `🔀`
- Version: `📦`
- Commit: `💾`
- Push: `📤`
- PR: `🔗`

Print progress as you work:
```
🚀 STEP 1: Analyzing Repository State
   ⏳ Checking current branch...
   ✅ On branch: main
   ⏳ Checking for changes...
   ✅ Found 5 modified files
```

## Workflow Steps

### Step 1: Analyze Current State 🔍

```bash
git branch --show-current
git status --porcelain
git branch --show-current | grep -q "^main$" && echo "ON_MAIN" || echo "ON_FEATURE"
```

Print: `🔍 STEP 1: Analyzing Repository State`

### Step 2: Branch Management 🔀

**If on `main`:**
1. `git stash --include-untracked -m "ship-command-autostash"`
2. `git pull origin main --rebase`
3. Generate descriptive branch name, create: `git checkout -b feature/<name>`
4. `git stash pop` (if stashed)

**If on feature branch:**
1. Check PR: `gh pr view --json state,number,url 2>/dev/null || echo "NO_PR"`
2. If OPEN: continue
3. If CLOSED/NO_PR: stash → checkout main → pull → new branch → unstash

Print: `🔀 STEP 2: Managing Branches`

### Step 3: Version Bump 📦

Parse bump type from arguments (default: patch).

1. Read versions:
   ```bash
   grep -E '^version = "' pyproject.toml
   grep -E '"version":' agent-smith-plugin/.claude-plugin/plugin.json
   ```

2. Calculate new version:
   - `patch`: X.Y.Z → X.Y.(Z+1)
   - `minor`: X.Y.Z → X.(Y+1).0
   - `major`: X.Y.Z → (X+1).0.0

3. Update files:
   ```bash
   sed -i 's/^version = ".*"/version = "<NEW>"/' pyproject.toml
   sed -i 's/"version": ".*"/"version": "<NEW>"/' agent-smith-plugin/.claude-plugin/plugin.json
   ```

Print: `📦 STEP 3: Bumping Version (X.Y.Z → A.B.C)`

### Step 4: Sync Plugin Scripts 🔄

```bash
./scripts/dev-sync.sh
```

Print: `🔄 STEP 4: Syncing Plugin Scripts`

### Step 5: Commit Changes 💾

1. `git add -A`
2. `git diff --cached --stat`
3. Generate semantic commit message:
   - Types: `feat:` | `fix:` | `refactor:` | `docs:` | `chore:` | `perf:` | `test:`
   - Include version bump
4. Commit with HEREDOC format

Print: `💾 STEP 5: Creating Commit`

### Step 6: Handle Pre-commit Hooks 🔧

If commit fails:
1. Check `git status`
2. If auto-formatted: `git add -A` and retry
3. If errors: fix them, stage, retry
4. Loop until success (max 5 attempts)

Track iterations for report.

Print: `🔧 STEP 6: Running Pre-commit Hooks`

### Step 7: Push to Remote 📤

```bash
git push -u origin HEAD
```

Print: `📤 STEP 7: Pushing to Remote`

### Step 8: Handle Pre-push Hooks 🧪

If push fails:
1. Fix issues (tests, builds)
2. `git add -A && git commit --amend --no-edit`
3. `git push -u origin HEAD --force-with-lease`
4. Loop until success (max 5 attempts)

Track iterations for report.

Print: `🧪 STEP 8: Running Pre-push Hooks`

### Step 9: Create/Update PR 🔗

1. Check: `gh pr view --json number,url 2>/dev/null`
2. If no PR:
   ```bash
   gh pr create --title "<type>: <description>" --body "<detailed-body>"
   gh pr merge --auto --squash
   ```
3. If PR exists: already updated by push

Print: `🔗 STEP 9: Managing Pull Request`

### Step 10: Generate Report 📊

**Output this exact format with the collected data:**

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🚀  S H I P   R E P O R T                                      ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   📋 SUMMARY                                                     ║
║   ─────────────────────────────────────────────────────────────  ║
║   Branch:       <branch-name>                                    ║
║   Previous:     <previous-branch or "—">                         ║
║   Version:      <old> → <new>                                    ║
║   Bump Type:    <patch|minor|major>                              ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   💾 COMMIT                                                      ║
║   ─────────────────────────────────────────────────────────────  ║
║   <short-hash>  <commit-title>                                   ║
║                                                                  ║
║   📁 Files Changed: <N> files (+<additions> -<deletions>)        ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   🔧 HOOKS                                                       ║
║   ─────────────────────────────────────────────────────────────  ║
║   Pre-commit:   <✅ Passed | ⚠️ Fixed (N iterations) | — N/A>    ║
║   Pre-push:     <✅ Passed | ⚠️ Fixed (N iterations) | — N/A>    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   🔗 PULL REQUEST                                                ║
║   ─────────────────────────────────────────────────────────────  ║
║   Status:       <✨ Created | 📝 Updated | 📋 Existing>          ║
║   Auto-merge:   <✅ Enabled | ⏳ Already Set | — N/A>            ║
║   PR Number:    #<number>                                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

   ┌──────────────────────────────────────────────────────────────┐
   │                                                              │
   │  🔗 <full-github-pr-url>                                     │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘
```

## Error Handling

- If any git operation fails unexpectedly: stop and report with `❌`
- If hooks fail more than 5 times: stop and report, ask for intervention
- If PR creation fails: show `gh` output for debugging
- Never skip hooks unless they auto-fixed the issues

## Data to Track

Throughout execution, track:
- `previous_branch`: branch before any changes
- `current_branch`: final branch name
- `old_version`: version before bump
- `new_version`: version after bump
- `bump_type`: patch/minor/major
- `commit_hash`: short hash of commit
- `commit_title`: first line of commit message
- `files_changed`: count of files
- `additions`: lines added
- `deletions`: lines removed
- `precommit_result`: "passed" | "fixed" | "n/a"
- `precommit_iterations`: number if fixed
- `prepush_result`: "passed" | "fixed" | "n/a"
- `prepush_iterations`: number if fixed
- `pr_status`: "created" | "updated" | "existing"
- `pr_number`: PR number
- `pr_url`: full URL
- `automerge_status`: "enabled" | "already_set" | "n/a"

Return ONLY the final beautiful report to the main agent.
