# VoidLight MarkItDown - Professional Project Structure Plan

## Current Structure Issues
- Mixed test types in single directory
- Scattered configuration files
- No clear separation between library and application
- Missing standard directories (docs, scripts, etc.)

## Proposed Professional Structure

```
voidlight-markitdown/
├── src/                              # Source code
│   ├── voidlight_markitdown/         # Core library
│   │   ├── __init__.py
│   │   ├── core/                     # Core functionality
│   │   ├── converters/               # Document converters
│   │   ├── korean/                   # Korean language features
│   │   ├── utils/                    # Utilities
│   │   └── api/                      # Public API
│   └── voidlight_markitdown_mcp/     # MCP server application
│       ├── __init__.py
│       ├── server/                   # Server implementation
│       ├── handlers/                 # Request handlers
│       └── config/                   # Configuration
├── tests/                            # All tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── e2e/                          # End-to-end tests
│   ├── performance/                  # Performance tests
│   └── fixtures/                     # Test fixtures and data
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── guides/                       # User guides
│   ├── development/                  # Developer documentation
│   └── deployment/                   # Deployment guides
├── scripts/                          # Utility scripts
│   ├── setup/                        # Setup scripts
│   ├── ci/                           # CI/CD scripts
│   └── maintenance/                  # Maintenance scripts
├── config/                           # Configuration files
│   ├── development/                  # Dev configs
│   ├── production/                   # Prod configs
│   └── testing/                      # Test configs
├── deploy/                           # Deployment files
│   ├── docker/                       # Docker files
│   ├── kubernetes/                   # K8s manifests
│   └── terraform/                    # Infrastructure as code
├── benchmarks/                       # Performance benchmarks
├── examples/                         # Usage examples
├── .github/                          # GitHub specific files
│   ├── workflows/                    # GitHub Actions
│   ├── ISSUE_TEMPLATE/              # Issue templates
│   └── PULL_REQUEST_TEMPLATE/       # PR templates
├── .vscode/                          # VSCode settings (if needed)
├── requirements/                     # Dependency management
│   ├── base.txt                      # Core dependencies
│   ├── dev.txt                       # Development dependencies
│   ├── test.txt                      # Test dependencies
│   └── prod.txt                      # Production dependencies
├── pyproject.toml                    # Project configuration
├── setup.py                          # Package setup
├── setup.cfg                         # Setup configuration
├── MANIFEST.in                       # Package manifest
├── Makefile                          # Build automation
├── tox.ini                           # Test automation
├── .gitignore                        # Git ignore rules
├── .dockerignore                     # Docker ignore rules
├── .editorconfig                     # Editor configuration
├── .pre-commit-config.yaml           # Pre-commit hooks
├── LICENSE                           # License file
├── README.md                         # Project readme
├── CHANGELOG.md                      # Version history
├── CONTRIBUTING.md                   # Contribution guidelines
├── CODE_OF_CONDUCT.md               # Code of conduct
└── SECURITY.md                       # Security policy
```

## Migration Steps

1. Create new directory structure
2. Move core library files to src/
3. Reorganize tests by type
4. Consolidate documentation
5. Update all imports
6. Create proper packaging files
7. Set up development tools
8. Update CI/CD configurations