# Contributing to Agent Smith

Thank you for your interest in contributing to Agent Smith! This guide will help you get started with development.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Submitting Changes](#submitting-changes)

## Development Setup

### Prerequisites

- Python 3.9 or higher
- PocketSmith account with API access (works on all tiers including Free)
- Git

### Installation

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agent-smith.git
   cd agent-smith
   ```

2. **Install uv** (recommended dependency manager):
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or with pip
   pip install uv
   ```

3. **Install dependencies**:
   ```bash
   # Using uv (recommended - fast, reliable)
   uv sync

   # OR using pip
   pip install -r requirements.txt

   # OR install in development mode
   uv pip install -e .
   ```

4. **Configure API access**:
   ```bash
   # Copy environment template
   cp .env.sample .env

   # Edit .env and add your PocketSmith API key
   # Get your API key from: Settings > Security > Developer API Keys
   ```

   Add to `.env`:
   ```bash
   POCKETSMITH_API_KEY=your_api_key_here
   TAX_INTELLIGENCE_LEVEL=smart
   DEFAULT_INTELLIGENCE_MODE=smart
   TAX_JURISDICTION=AU
   FINANCIAL_YEAR_END=06-30
   ```

### Verification

Verify your setup is working:

```bash
# Check dependencies
uv pip list | grep -E "requests|python-dateutil|python-dotenv"

# Test API connection
uv run python -c "from scripts.core.api_client import PocketSmithClient; c = PocketSmithClient(); print(f'Connected as: {c.get_user()[\"login\"]}')"

# Run tests
uv run pytest tests/unit -v
```

### Running Python Scripts

**Always use `uv run` or activate the virtual environment:**

```bash
# Option 1: Use uv run (recommended)
uv run python -u scripts/health/check.py

# Option 2: Activate venv first
source .venv/bin/activate  # Unix/macOS
# .venv\Scripts\activate   # Windows
python -u scripts/health/check.py
```

**Why `-u` flag?** Python buffers output by default. The `-u` flag enables unbuffered output so you see progress in real-time. Essential for long-running operations.

## Project Structure

```
agent-smith/
├── .claude-plugin/           # Plugin metadata (marketplace.json)
├── agent-smith-plugin/       # Skill source for marketplace distribution
│   └── skills/agent-smith/   # Skill definition and assets
├── ai_docs/                  # Reference docs for AI agents
├── commands/                 # Slash command definitions
├── docs/                     # User and developer documentation
├── scripts/                  # Python source code
│   ├── core/                 # Core libraries (API, rule engine)
│   ├── operations/           # High-level operations
│   ├── workflows/            # Interactive workflows
│   ├── analysis/             # Financial analysis
│   ├── reporting/            # Report generation
│   ├── tax/                  # Tax intelligence (3-tier)
│   ├── scenarios/            # Scenario analysis
│   ├── health/               # Health check system
│   ├── features/             # Advanced features
│   └── utils/                # Utilities
└── tests/                    # Test suite
    ├── unit/                 # Unit tests
    └── integration/          # Integration tests
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feat/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-description` - Documentation updates
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test additions/updates

### Code Organization

- **Core libraries** go in `scripts/core/`
- **Operations** (high-level functionality) go in `scripts/operations/`
- **Features** (user-facing capabilities) go in `scripts/features/`
- **Tests** mirror the source structure in `tests/unit/` or `tests/integration/`

### Documentation

When making changes:
1. Update relevant documentation in `docs/`
2. Add docstrings to new functions/classes
3. Update `README.md` if changing user-facing features
4. Add examples to `docs/examples/` for new patterns

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/unit/test_api_client.py -v

# Run with coverage
uv run pytest tests/ --cov=scripts --cov-report=html
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test multiple components working together
- Use mocks for external API calls
- Follow existing test patterns in `tests/unit/`

Example:
```python
def test_merchant_normalization():
    """Test that merchant names are normalized correctly."""
    normalizer = MerchantNormalizer()
    result = normalizer.normalize("WOOLWORTHS METRO 123")
    assert result == "WOOLWORTHS"
```

### Test Requirements

- All new features must have unit tests
- Maintain test coverage above 80%
- Tests must pass before submitting PR
- Use descriptive test names that explain what is being tested

## Code Standards

### Style Guide

We use pre-commit hooks to enforce code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Tools:**
- **black**: Code formatting
- **flake8**: Linting (max line length: 100)
- **mypy**: Type checking

### Type Hints

Use type hints for all function signatures:

```python
def categorize_transaction(
    transaction: Dict[str, Any],
    rules: List[Dict[str, Any]]
) -> Optional[str]:
    """Categorize a transaction using rules."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def analyze_spending(
    transactions: List[Dict[str, Any]],
    period: str
) -> Dict[str, Any]:
    """Analyze spending patterns for a given period.

    Args:
        transactions: List of transaction dictionaries
        period: Period string (e.g., "2025-11", "2025")

    Returns:
        Dictionary with spending analysis including:
        - total: Total spending amount
        - by_category: Breakdown by category
        - trends: Spending trends

    Raises:
        ValueError: If period format is invalid
    """
    ...
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Don't catch exceptions you can't handle

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

## Submitting Changes

### Before Submitting

1. **Run tests**: `uv run pytest tests/`
2. **Run linters**: `pre-commit run --all-files`
3. **Update documentation** if needed
4. **Add tests** for new functionality
5. **Update CHANGELOG.md** (if applicable)

### Commit Messages

Use conventional commit format:

```
feat: Add LLM-powered transaction categorization

- Implement hybrid rule engine with LLM fallback
- Add confidence scoring and user confirmation
- Include rule learning from LLM patterns

Closes #123
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/updates
- `chore:` - Maintenance tasks

### Pull Request Process

1. **Create PR** from your feature branch to `main`
2. **Fill out PR template** with description and testing notes
3. **Ensure CI passes** (tests, linting, type checking)
4. **Request review** from maintainers
5. **Address feedback** and update PR
6. **Squash and merge** once approved

### PR Checklist

- [ ] Tests pass (`pytest tests/`)
- [ ] Linting passes (`pre-commit run --all-files`)
- [ ] Type checking passes (`mypy scripts/`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with main

## Development Workflow

### Typical Workflow

```bash
# 1. Create feature branch
git checkout -b feat/new-feature

# 2. Make changes and test
uv run python -u scripts/your_script.py
uv run pytest tests/unit/test_your_feature.py -v

# 3. Run pre-commit checks
pre-commit run --all-files

# 4. Commit changes
git add .
git commit -m "feat: Add new feature description"

# 5. Push and create PR
git push origin feat/new-feature
# Create PR on GitHub
```

### Testing Against PocketSmith API

When testing API integration:
- Use dry-run modes when available
- Test against a sandbox/test account if possible
- Be mindful of rate limiting
- Never commit API keys or sensitive data

### Working with the Rule Engine

The unified rule engine uses YAML configuration:

```bash
# 1. Edit rules
vim data/rules.yaml

# 2. Test with dry run
uv run python scripts/operations/batch_categorize.py --mode=dry_run --period=2025-11

# 3. Apply if satisfied
uv run python scripts/operations/batch_categorize.py --mode=apply --period=2025-11
```

See `docs/guides/unified-rules-guide.md` for complete rule syntax.

## Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Design docs**: See `docs/design/` for architecture details

## Additional Resources

- [Design Specification](docs/design/2025-11-20-agent-smith-design.md)
- [Unified Rules Guide](docs/guides/unified-rules-guide.md)
- [Health Check Guide](docs/guides/health-check-guide.md)
- [PocketSmith API Reference](ai_docs/pocketsmith-api-documentation.md)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Agent Smith! 🤖
