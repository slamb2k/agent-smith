# Agent Smith - Claude Code Skill Source

This directory contains the source files for the Agent Smith Claude Code skill.

## Directory Structure

```
skill/
├── SKILL.md                    # Main skill definition (required)
├── .env.sample                 # Configuration template
├── pyproject.toml              # Python dependencies
├── uv.lock                     # Dependency lock file
├── .gitignore                  # Git ignore patterns
│
├── scripts/                    # Python code (copied from ../scripts/)
│   ├── core/                   # API client, rule engine, unified rules
│   ├── operations/             # Categorization, batch processing
│   ├── analysis/               # Spending analysis, trends
│   ├── reporting/              # Report generation
│   ├── tax/                    # Tax intelligence (3-tier)
│   ├── scenarios/              # Scenario analysis
│   ├── orchestration/          # Subagent conductor
│   ├── workflows/              # Interactive workflows
│   ├── features/               # Advanced features
│   ├── health/                 # Health check system
│   └── utils/                  # Utilities
│
├── references/                 # Documentation (loaded on-demand)
│   ├── pocketsmith-api.md      # PocketSmith API reference
│   ├── design.md               # Complete system architecture
│   ├── unified-rules-guide.md  # Rule system documentation
│   ├── onboarding-guide.md     # First-time setup guide
│   ├── health-check-guide.md   # Health system details
│   └── LESSONS_LEARNED.md      # Migration insights
│
├── assets/                     # Templates and samples
│   ├── templates/              # Pre-built rule templates
│   ├── .env.sample             # Configuration template
│   └── config.json.sample      # User preferences template
│
└── data/                       # Working directories (empty, created at runtime)
    ├── templates/
    ├── merchants/
    ├── tax/
    └── [other runtime directories]
```

## Building the Skill Package

To rebuild the `agent-smith.skill` package after making changes:

```bash
# From the repository root
./build-skill.sh
```

Or manually:

```bash
cd /path/to/agent-smith
zip -r agent-smith.skill skill/ \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.git*" \
  -x "skill/data/*" \
  -x "skill/logs/*" \
  -x "skill/backups/*" \
  -x "skill/reports/*"
```

The packaged `.skill` file will be created in the repository root.

## Development Workflow

1. **Make changes** to files in this directory
2. **Test changes** by copying to `~/.claude/skills/agent-smith/` and testing in Claude Code
3. **Rebuild the package** using the build script
4. **Commit changes** to the repository

## What Gets Packaged

**Included:**
- ✅ SKILL.md (required)
- ✅ All Python scripts
- ✅ All reference documentation
- ✅ Asset templates and samples
- ✅ Configuration templates
- ✅ Dependency files (pyproject.toml, uv.lock)
- ✅ Empty data directories (structure only)

**Excluded:**
- ❌ Python cache files (*.pyc, __pycache__)
- ❌ Git files
- ❌ Runtime data (data/, logs/, backups/, reports/ contents)
- ❌ User-specific configuration (.env)

## File Organization

Following Claude Code skill best practices:

- **Progressive Disclosure**: SKILL.md is concise (~500 lines), detailed docs in references/
- **Bundled Scripts**: All executable Python code in scripts/
- **Reference Documentation**: Detailed guides loaded on-demand from references/
- **Asset Templates**: Pre-built templates and configuration samples in assets/

## Updating the Skill

### Adding New Scripts

1. Add/update scripts in `../scripts/`
2. Copy to `skill/scripts/`:
   ```bash
   cp -r ../scripts/* skill/scripts/
   ```
3. Rebuild the package

### Adding New Documentation

1. Add documentation to `skill/references/`
2. Reference it from SKILL.md if needed
3. Rebuild the package

### Updating SKILL.md

1. Edit `skill/SKILL.md`
2. Ensure frontmatter is valid YAML
3. Keep instructions concise (<500 lines)
4. Rebuild the package

## Testing the Skill

### Local Testing

```bash
# Install the skill locally
/plugin install /path/to/agent-smith.skill

# Or extract and copy manually
cd ~/.claude/skills/
unzip /path/to/agent-smith.skill
cd agent-smith/
cp .env.sample .env
# Edit .env with your API key
uv sync
```

### Run Tests

```bash
cd ~/.claude/skills/agent-smith/
uv run python -u scripts/operations/batch_categorize.py --mode=dry_run
```

## Version History

- **1.3.7** - Complete implementation (all 8 phases)
- **1.0.0** - Initial skill package

## Notes

- This is the **source directory** for the skill - the actual skill package is `../agent-smith.skill`
- Always rebuild the package after making changes
- Test changes locally before distributing
- Keep SKILL.md focused and concise
- Move detailed documentation to references/
