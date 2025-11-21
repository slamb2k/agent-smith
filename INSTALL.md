# Agent Smith Plugin Installation Guide

## Prerequisites

- Python 3.9 or higher
- PocketSmith account with API access
- Claude Code CLI installed

## Installation Methods

### Method 1: Install from Git Repository (Recommended)

```bash
# Clone the repository
git clone https://github.com/slamb2k/agent-smith.git
cd agent-smith

# Install dependencies with uv (recommended)
uv sync

# OR install with pip
pip install -r requirements.txt

# OR install package in development mode
uv pip install -e .

# Configure your API key
cp .env.sample .env
# Edit .env and add your POCKETSMITH_API_KEY
```

**Note:** Agent Smith uses `uv` for fast, reliable dependency management. If you don't have `uv` installed:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Method 2: Install from Release Package

1. Download the latest release from [GitHub Releases](https://github.com/slamb2k/agent-smith/releases)
2. Extract the package:
   ```bash
   # For tar.gz
   tar -xzf agent-smith-plugin-X.Y.Z.tar.gz

   # For zip
   unzip agent-smith-plugin-X.Y.Z.zip
   ```
3. Run the installation script:
   ```bash
   cd agent-smith-plugin-X.Y.Z
   ./install.sh
   ```
4. Configure your API key in `.env`

## Configuration

### Required: PocketSmith API Key

**✅ Works with ALL PocketSmith tiers** (including Free)

API access is available on all subscription levels with no restrictions.

1. Log in to your PocketSmith account (any tier)
2. Go to **Settings** > **Security** > **Developer API Keys**
3. Generate a new API key
4. Add it to your `.env` file:
   ```
   POCKETSMITH_API_KEY=your_api_key_here
   ```

### Optional Settings

Add these to your `.env` file to customize behavior:

```bash
# Tax intelligence level: reference, smart, or full
TAX_INTELLIGENCE_LEVEL=smart

# Categorization mode: conservative, smart, or aggressive
DEFAULT_INTELLIGENCE_MODE=smart

# Tax jurisdiction (currently AU supported)
TAX_JURISDICTION=AU

# Financial year end (MM-DD format)
FINANCIAL_YEAR_END=06-30
```

## PocketSmith Subscription Tiers

Agent Smith works with **all** PocketSmith subscription tiers. The table below is for reference only - there are no API restrictions.

| Feature | Free | Foundation | Flourish | Fortune |
|---------|------|------------|----------|---------|
| **Price (Annual)** | Free | $9.99/mo AUD | $16.66/mo AUD | $26.66/mo AUD |
| **API Access** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Agent Smith** | ✅ Works | ✅ Works | ✅ Works | ✅ Works |
| **Accounts** | 2 | Unlimited | Unlimited | Unlimited |
| **Bank Connections** | Manual | 6 (1 country) | 18 (all) | Unlimited |
| **Automatic Feeds** | ❌ | ✅ | ✅ | ✅ |
| **Budgets** | 12 | Unlimited | Unlimited | Unlimited |
| **Forecast** | 6 months | 10 years | 30 years | 60 years |
| **Support** | - | Email | Email | Priority |

**Key Points:**
- ✅ API access available on **all** tiers (including Free)
- ✅ Agent Smith has **no feature restrictions** based on tier
- ⚠️ Category rules created via API can only be modified/deleted via PocketSmith web interface (API limitation)
- 💡 Free tier limited to 2 accounts and manual imports only

## Verification

After installation, verify everything is working:

```bash
# Verify dependencies are installed
uv pip list | grep -E "requests|python-dateutil|python-dotenv"

# Test API connection (using uv)
uv run python -c "from scripts.core.api_client import PocketSmithClient; c = PocketSmithClient(); print(f'Connected as: {c.get_user()[\"login\"]}')"

# OR activate virtual environment first
source .venv/bin/activate  # Unix/macOS
# .venv\Scripts\activate   # Windows
python -c "from scripts.core.api_client import PocketSmithClient; c = PocketSmithClient(); print(f'Connected as: {c.get_user()[\"login\"]}')"

# Run a quick health check via Claude Code
/agent-smith-health --quick
```

**Important:** When running Python scripts directly, always use:
- `uv run python script.py` (recommended), OR
- Activate the venv first: `source .venv/bin/activate`

This ensures scripts use the installed dependencies instead of system Python.

## Available Commands

Once installed, you have access to these slash commands:

| Command | Description |
|---------|-------------|
| `/agent-smith` | Main conversational assistant |
| `/agent-smith-categorize` | Categorize transactions |
| `/agent-smith-analyze` | Financial analysis |
| `/agent-smith-scenario` | What-if scenarios |
| `/agent-smith-report` | Generate reports |
| `/agent-smith-optimize` | Optimization suggestions |
| `/agent-smith-tax` | Tax intelligence |
| `/agent-smith-health` | Setup health check |

## Getting Started

1. **Run a health check** to see the state of your PocketSmith setup:
   ```
   /agent-smith-health --full
   ```

2. **Categorize uncategorized transactions**:
   ```
   /agent-smith-categorize --mode=smart
   ```

3. **Analyze your spending**:
   ```
   /agent-smith-analyze spending --period=2025
   ```

## Updating

### From Git
```bash
cd agent-smith
git pull origin main

# Update dependencies with uv (recommended)
uv sync

# OR with pip
pip install -r requirements.txt
```

### From Release Package
Download and extract the new version, then run `./install.sh` again.

## Troubleshooting

### API Connection Issues
- Verify your API key is correct in `.env`
- Check that your PocketSmith account has API access enabled
- Ensure your firewall allows HTTPS connections to api.pocketsmith.com

### Python Issues

**"ModuleNotFoundError: No module named 'requests'"**
- This means Python is not using the virtual environment
- **Solution 1:** Use `uv run` for all Python commands:
  ```bash
  uv run python your_script.py
  ```
- **Solution 2:** Activate the virtual environment:
  ```bash
  source .venv/bin/activate  # Unix/macOS
  .venv\Scripts\activate     # Windows
  ```
- **Solution 3:** Install dependencies if missing:
  ```bash
  uv sync  # Recommended
  # OR
  pip install -r requirements.txt
  ```

**General Python Issues:**
- Ensure Python 3.9+ is installed: `python --version`
- Try using `python3` explicitly if `python` doesn't work
- Verify dependencies are installed:
  ```bash
  uv pip list | grep -E "requests|python-dateutil|python-dotenv"
  ```

### Permission Issues
- On Unix, ensure install.sh is executable: `chmod +x install.sh`
- If pip install fails, try: `pip install --user -r requirements.txt`

## Support

- [GitHub Issues](https://github.com/slamb2k/agent-smith/issues)
- [Documentation](docs/guides/health-check-guide.md)
- [API Reference](ai_docs/pocketsmith-api-documentation.md)
