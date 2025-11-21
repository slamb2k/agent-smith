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

# Install Python dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.sample .env
# Edit .env and add your POCKETSMITH_API_KEY
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

1. Log in to your PocketSmith account
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

## Verification

After installation, verify everything is working:

```bash
# Run a quick health check
/agent-smith-health --quick

# Test API connection
python -c "from scripts.core.api_client import PocketSmithClient; c = PocketSmithClient(); print(f'Connected as: {c.get_user()[\"login\"]}')"
```

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
- Ensure Python 3.9+ is installed: `python --version`
- Try using `python3` explicitly if `python` doesn't work
- Consider using a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Unix
  .venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

### Permission Issues
- On Unix, ensure install.sh is executable: `chmod +x install.sh`
- If pip install fails, try: `pip install --user -r requirements.txt`

## Support

- [GitHub Issues](https://github.com/slamb2k/agent-smith/issues)
- [Documentation](docs/guides/health-check-guide.md)
- [API Reference](ai_docs/pocketsmith-api-documentation.md)
