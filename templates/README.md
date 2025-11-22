# Agent Smith Templates

This directory contains composable template configurations for PocketSmith onboarding.

## Structure

- **primary/** - Primary income structure templates (choose ONE)
- **living/** - Living arrangement templates (choose ONE)
- **additional/** - Additional income source templates (choose MULTIPLE)

## Usage

Templates are YAML files that define:
- Categories to create
- Categorization rules
- Tax tracking configuration
- Smart alerts

During onboarding, templates are selected and merged using `scripts/setup/template_merger.py`.

## Template Schema

See individual layer README files for YAML schema details.
