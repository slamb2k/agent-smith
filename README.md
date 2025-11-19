# Agent Smith

**An intelligent financial management skill for Claude Code**

Agent Smith provides comprehensive PocketSmith API integration with advanced AI-powered analysis, rule management, tax intelligence, and scenario planning.

## Project Status

🎨 **Design Phase Complete** - Full specification ready for implementation

📋 **Design Document:** [docs/design/2025-11-20-agent-smith-design.md](docs/design/2025-11-20-agent-smith-design.md)

## What is Agent Smith?

Agent Smith transforms PocketSmith from a passive tracking tool into an active financial intelligence system. Named after the Matrix AI agent, it serves as your intelligent assistant for managing your financial matrix.

### Key Features

- **Hybrid Rule Engine** - Platform-native + enhanced local rules with performance tracking
- **3-Tier Tax Intelligence** - Reference, Smart, and Full compliance modes (Australian ATO)
- **Scenario Analysis** - Historical analysis, projections, optimization, tax planning
- **Multi-Format Reports** - Markdown, CSV/JSON, HTML dashboards, Excel
- **Smart Orchestration** - Context-preserving subagent architecture
- **Proactive Insights** - Automated alerts, optimization recommendations
- **Health Checks** - Comprehensive PocketSmith setup evaluation

## Repository Structure

```
budget-smith/
├── README.md                    # This file
├── INDEX.md                     # Directory navigation guide
├── .gitignore                   # Git ignore rules
├── .env                         # API configuration (not committed)
│
├── docs/                        # Documentation
│   ├── INDEX.md
│   └── design/                  # Design specifications
│       └── 2025-11-20-agent-smith-design.md
│
├── ai_docs/                     # AI agent documentation
│   ├── INDEX.md
│   └── pocketsmith-api-documentation.md
│
├── build/                       # Reference materials (temporary)
│   ├── docs/                    # Migration documentation
│   └── scripts/                 # Python scripts for reference
│
└── .claude/                     # Claude Code configuration
    └── commands/                # Slash commands (future)
```

## Quick Start

### Prerequisites

- PocketSmith account with API access
- Developer API key from PocketSmith (Settings > Security)

### Setup

1. Clone the repository
2. Copy `.env.sample` to `.env`
3. Add your PocketSmith API key to `.env`
4. Install Agent Smith skill (see design doc)

## Documentation

- **[Design Specification](docs/design/2025-11-20-agent-smith-design.md)** - Complete Agent Smith design
- **[Repository Index](INDEX.md)** - Detailed directory structure
- **[PocketSmith API Docs](ai_docs/pocketsmith-api-documentation.md)** - API reference

## Development Status

### Completed
✅ Complete design specification
✅ Repository structure
✅ Documentation framework

### Next Steps
- [ ] Create git worktree for isolated development
- [ ] Implement Phase 1: Foundation (directory structure, core libraries)
- [ ] Implement Phase 2: Rule Engine
- [ ] Implement Phase 3: Analysis & Reporting
- [ ] Implement Phase 4: Tax Intelligence
- [ ] Implement Phase 5: Scenario Analysis
- [ ] Implement Phase 6: Orchestration & UX
- [ ] Implement Phase 7: Advanced Features
- [ ] Implement Phase 8: Health Check & Polish

See [design document](docs/design/2025-11-20-agent-smith-design.md) for full roadmap.

## License

[To be determined]

## Support

For questions or issues, please refer to the design documentation or create an issue in the repository.

---

**Note:** This project is in active development. The `build/` directory contains reference materials from previous migration work and will be removed before final publication.
