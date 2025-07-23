# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional build and deployment system with Makefile
- Split requirements files by environment (base, production, development, testing, optional)
- Docker and docker-compose configurations for local development
- Kubernetes manifests for production deployment
- Pre-commit hooks configuration for code quality
- Automated release management scripts
- License compliance checking
- Changelog generation from git commits
- Comprehensive CI/CD pipeline with GitHub Actions
- Build automation scripts with validation
- Version management with bumpversion
- Security scanning with bandit and safety
- Code quality tools configuration (black, isort, flake8, mypy, pylint, ruff)
- Performance benchmarking integration
- SBOM (Software Bill of Materials) generation

### Changed
- Enhanced pyproject.toml with comprehensive tool configurations
- Improved project structure for enterprise deployment

### Fixed
- Build system now properly handles all dependency types
- Docker images optimized for security and size

### Security
- Added security scanning in CI/CD pipeline
- Non-root user in Docker containers
- Dependency vulnerability checking

## [0.0.39] - Previous Release

### Added
- Initial implementation of voidlight-markitdown
- Korean language support
- Multiple document format converters
- MCP server integration