#!/bin/bash
# Build Agent Smith Claude Code Skill Package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SKILL_DIR="agent-smith-plugin/skills/agent-smith"

echo "Building Agent Smith skill package..."

# Clean up old package
if [ -f agent-smith.skill ]; then
    echo "Removing old package..."
    rm agent-smith.skill
fi

# Update scripts from source
echo "Updating scripts from source..."
if [ -d "$SKILL_DIR/scripts" ]; then
    rm -rf "$SKILL_DIR/scripts"
fi
cp -r scripts "$SKILL_DIR/"

# Package the skill
echo "Creating skill package..."
cd "$SKILL_DIR"
zip -r ../../../agent-smith.skill . \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.git*" \
    -x ".DS_Store" \
    -x ".env"

cd "$SCRIPT_DIR"

# Show package info
PACKAGE_SIZE=$(du -h agent-smith.skill | cut -f1)
echo ""
echo "✅ Skill package created successfully!"
echo "   File: agent-smith.skill"
echo "   Size: $PACKAGE_SIZE"
echo ""
echo "To install: /plugin install $(pwd)/agent-smith.skill"
echo "Or copy to: ~/.claude/skills/agent-smith/"
