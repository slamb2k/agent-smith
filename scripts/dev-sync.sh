#!/bin/bash
#
# Local Development Sync Script
#
# Syncs source files from /scripts/ to the plugin directory for local testing.
# This mirrors what CI/CD does during the build process.
#
# Usage:
#   ./scripts/dev-sync.sh           # Sync all files
#   ./scripts/dev-sync.sh --dry-run # Show what would be synced
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/scripts"
TARGET_DIR="$REPO_ROOT/agent-smith-plugin/skills/agent-smith/scripts"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
fi

echo "================================================"
echo "  Agent Smith Development Sync"
echo "================================================"
echo ""
echo "Source:  $SOURCE_DIR"
echo "Target:  $TARGET_DIR"
echo ""

# Safety checks to prevent recursive nesting
if [ ! -d "$SOURCE_DIR" ]; then
    echo "${RED}Error: Source directory not found: $SOURCE_DIR${NC}"
    echo ""
    echo "This script must be run from the repository root:"
    echo "  cd /path/to/agent-smith"
    echo "  ./scripts/dev-sync.sh"
    exit 1
fi

# Verify we're not about to create a nested structure
if [[ "$TARGET_DIR" == *"/agent-smith-plugin/skills/agent-smith/agent-smith-plugin"* ]]; then
    echo "${RED}Error: Detected recursive path in TARGET_DIR!${NC}"
    echo ""
    echo "Target: $TARGET_DIR"
    echo ""
    echo "This happens when the script is run from the wrong directory."
    echo "Please run from the repository root:"
    echo "  cd /path/to/agent-smith"
    echo "  ./scripts/dev-sync.sh"
    exit 1
fi

# Verify the target looks correct
if [ ! -f "$REPO_ROOT/CLAUDE.md" ]; then
    echo "${RED}Error: Not in agent-smith repository root${NC}"
    echo ""
    echo "Could not find CLAUDE.md in: $REPO_ROOT"
    echo "Please run this script from the agent-smith repository root."
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Perform sync
if [ "$DRY_RUN" = true ]; then
    echo "${YELLOW}DRY RUN - No files will be modified${NC}"
    echo ""
    rsync -avn --delete "$SOURCE_DIR/" "$TARGET_DIR/"
else
    echo "Syncing files..."
    rsync -av --delete "$SOURCE_DIR/" "$TARGET_DIR/"
    echo ""
    echo "${GREEN}✓ Sync complete!${NC}"
    echo ""
    echo "Changes synced from source to plugin directory."
    echo "The plugin directory is gitignored - remember to edit source files in /scripts/"
fi

echo ""
echo "Files now match:"
echo "  /scripts/                    (source - tracked in git)"
echo "  /agent-smith-plugin/.../scripts/  (copy - gitignored)"
echo ""
