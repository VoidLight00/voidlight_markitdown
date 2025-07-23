# Voidlight Markitdown Build System
# Professional build automation for enterprise deployment

# Configuration
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Project Configuration
PROJECT := voidlight-markitdown
PYTHON := python3
VENV := .venv
PACKAGE_DIR := src/voidlight_markitdown
MCP_PACKAGE_DIR := src/voidlight_markitdown_mcp

# Version Management
VERSION_FILE := $(PACKAGE_DIR)/__about__.py
VERSION := $(shell python -c "exec(open('$(VERSION_FILE)').read()); print(__version__)")

# Docker Configuration
DOCKER_REGISTRY ?= docker.io
DOCKER_ORG ?= voidlight
DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(DOCKER_ORG)/$(PROJECT)
DOCKER_TAG ?= $(VERSION)

# Colors for output
NO_COLOR := \033[0m
OK_COLOR := \033[32;01m
ERROR_COLOR := \033[31;01m
WARN_COLOR := \033[33;01m

# Macros
define print_ok
	@printf "$(OK_COLOR)[OK]$(NO_COLOR) %s\n" "$(1)"
endef

define print_error
	@printf "$(ERROR_COLOR)[ERROR]$(NO_COLOR) %s\n" "$(1)"
endef

define print_warn
	@printf "$(WARN_COLOR)[WARN]$(NO_COLOR) %s\n" "$(1)"
endef

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(OK_COLOR)%-20s$(NO_COLOR) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment Setup
.PHONY: init
init: ## Initialize development environment
	@echo "Initializing development environment..."
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip setuptools wheel
	$(VENV)/bin/pip install -e ".[dev]"
	$(call print_ok,"Development environment initialized")

.PHONY: clean-init
clean-init: clean init ## Clean and reinitialize environment

# Dependency Management
.PHONY: deps
deps: ## Install production dependencies
	@echo "Installing production dependencies..."
	$(VENV)/bin/pip install -r requirements/production.txt
	$(call print_ok,"Production dependencies installed")

.PHONY: deps-dev
deps-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	$(VENV)/bin/pip install -r requirements/development.txt
	$(call print_ok,"Development dependencies installed")

.PHONY: deps-test
deps-test: ## Install test dependencies
	@echo "Installing test dependencies..."
	$(VENV)/bin/pip install -r requirements/testing.txt
	$(call print_ok,"Test dependencies installed")

.PHONY: deps-all
deps-all: deps deps-dev deps-test ## Install all dependencies

.PHONY: deps-update
deps-update: ## Update all dependencies
	@echo "Updating dependencies..."
	$(VENV)/bin/pip install --upgrade pip setuptools wheel
	$(VENV)/bin/pip install --upgrade -r requirements/production.txt
	$(VENV)/bin/pip install --upgrade -r requirements/development.txt
	$(VENV)/bin/pip install --upgrade -r requirements/testing.txt
	$(call print_ok,"Dependencies updated")

.PHONY: deps-freeze
deps-freeze: ## Freeze current dependencies
	@echo "Freezing dependencies..."
	$(VENV)/bin/pip freeze --exclude-editable > requirements/frozen.txt
	$(call print_ok,"Dependencies frozen to requirements/frozen.txt")

# Code Quality
.PHONY: format
format: ## Format code with black and isort
	@echo "Formatting code..."
	$(VENV)/bin/black $(PACKAGE_DIR) $(MCP_PACKAGE_DIR) tests
	$(VENV)/bin/isort $(PACKAGE_DIR) $(MCP_PACKAGE_DIR) tests
	$(call print_ok,"Code formatted")

.PHONY: lint
lint: ## Run all linters
	@echo "Running linters..."
	$(VENV)/bin/flake8 $(PACKAGE_DIR) $(MCP_PACKAGE_DIR) tests
	$(VENV)/bin/pylint $(PACKAGE_DIR) $(MCP_PACKAGE_DIR)
	$(VENV)/bin/mypy $(PACKAGE_DIR) $(MCP_PACKAGE_DIR)
	$(call print_ok,"Linting completed")

.PHONY: security
security: ## Run security checks
	@echo "Running security checks..."
	$(VENV)/bin/bandit -r $(PACKAGE_DIR) $(MCP_PACKAGE_DIR)
	$(VENV)/bin/safety check
	$(call print_ok,"Security checks completed")

.PHONY: quality
quality: format lint security ## Run all quality checks

# Testing
.PHONY: test
test: ## Run unit tests
	@echo "Running unit tests..."
	$(VENV)/bin/pytest tests/unit -v
	$(call print_ok,"Unit tests completed")

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "Running integration tests..."
	$(VENV)/bin/pytest tests/integration -v
	$(call print_ok,"Integration tests completed")

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	@echo "Running e2e tests..."
	$(VENV)/bin/pytest tests/e2e -v
	$(call print_ok,"E2E tests completed")

.PHONY: test-all
test-all: ## Run all tests
	@echo "Running all tests..."
	$(VENV)/bin/pytest tests -v
	$(call print_ok,"All tests completed")

.PHONY: coverage
coverage: ## Run tests with coverage
	@echo "Running tests with coverage..."
	$(VENV)/bin/pytest tests --cov=$(PACKAGE_DIR) --cov-report=html --cov-report=term
	$(call print_ok,"Coverage report generated")

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	$(VENV)/bin/ptw tests

# Build
.PHONY: build
build: clean quality ## Build distribution packages
	@echo "Building distribution packages..."
	$(VENV)/bin/python -m build
	$(call print_ok,"Build completed")

.PHONY: build-docker
build-docker: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest
	$(call print_ok,"Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)")

.PHONY: build-docs
build-docs: ## Build documentation
	@echo "Building documentation..."
	$(VENV)/bin/mkdocs build
	$(call print_ok,"Documentation built")

# Version Management
.PHONY: version
version: ## Show current version
	@echo "Current version: $(VERSION)"

.PHONY: version-bump-patch
version-bump-patch: ## Bump patch version
	@echo "Bumping patch version..."
	$(VENV)/bin/bumpversion patch
	$(call print_ok,"Version bumped to $(shell python -c "exec(open('$(VERSION_FILE)').read()); print(__version__)")")

.PHONY: version-bump-minor
version-bump-minor: ## Bump minor version
	@echo "Bumping minor version..."
	$(VENV)/bin/bumpversion minor
	$(call print_ok,"Version bumped to $(shell python -c "exec(open('$(VERSION_FILE)').read()); print(__version__)")")

.PHONY: version-bump-major
version-bump-major: ## Bump major version
	@echo "Bumping major version..."
	$(VENV)/bin/bumpversion major
	$(call print_ok,"Version bumped to $(shell python -c "exec(open('$(VERSION_FILE)').read()); print(__version__)")")

# Release
.PHONY: release-check
release-check: ## Check if ready for release
	@echo "Checking release readiness..."
	@$(VENV)/bin/python scripts/ci/check_release.py
	$(call print_ok,"Release checks passed")

.PHONY: release
release: release-check build ## Create a release
	@echo "Creating release..."
	@$(VENV)/bin/python scripts/ci/create_release.py
	$(call print_ok,"Release created")

.PHONY: publish-test
publish-test: ## Publish to test PyPI
	@echo "Publishing to test PyPI..."
	$(VENV)/bin/twine upload --repository testpypi dist/*
	$(call print_ok,"Published to test PyPI")

.PHONY: publish
publish: ## Publish to PyPI
	@echo "Publishing to PyPI..."
	$(VENV)/bin/twine upload dist/*
	$(call print_ok,"Published to PyPI")

# Docker Operations
.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "Running Docker container..."
	docker run --rm -it $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-push
docker-push: ## Push Docker image to registry
	@echo "Pushing Docker image..."
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(DOCKER_IMAGE):latest
	$(call print_ok,"Docker image pushed")

.PHONY: docker-compose-up
docker-compose-up: ## Start services with docker-compose
	@echo "Starting services..."
	docker-compose up -d
	$(call print_ok,"Services started")

.PHONY: docker-compose-down
docker-compose-down: ## Stop services with docker-compose
	@echo "Stopping services..."
	docker-compose down
	$(call print_ok,"Services stopped")

# Development
.PHONY: dev
dev: ## Start development server
	@echo "Starting development server..."
	$(VENV)/bin/python -m voidlight_markitdown

.PHONY: shell
shell: ## Open Python shell with project context
	@echo "Opening Python shell..."
	$(VENV)/bin/ipython

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "Serving documentation..."
	$(VENV)/bin/mkdocs serve

# Maintenance
.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf build dist *.egg-info
	rm -rf .coverage htmlcov .pytest_cache
	rm -rf .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	$(call print_ok,"Build artifacts cleaned")

.PHONY: clean-all
clean-all: clean ## Clean everything including venv
	@echo "Cleaning everything..."
	rm -rf $(VENV)
	rm -rf node_modules
	$(call print_ok,"Everything cleaned")

.PHONY: install-hooks
install-hooks: ## Install git hooks
	@echo "Installing git hooks..."
	$(VENV)/bin/pre-commit install
	$(call print_ok,"Git hooks installed")

.PHONY: run-hooks
run-hooks: ## Run git hooks on all files
	@echo "Running git hooks..."
	$(VENV)/bin/pre-commit run --all-files
	$(call print_ok,"Git hooks completed")

# CI/CD
.PHONY: ci
ci: deps-all quality test-all build ## Run full CI pipeline

.PHONY: cd-staging
cd-staging: ## Deploy to staging
	@echo "Deploying to staging..."
	$(VENV)/bin/python scripts/ci/deploy_staging.py
	$(call print_ok,"Deployed to staging")

.PHONY: cd-production
cd-production: ## Deploy to production
	@echo "Deploying to production..."
	$(VENV)/bin/python scripts/ci/deploy_production.py
	$(call print_ok,"Deployed to production")

# Utilities
.PHONY: check-licenses
check-licenses: ## Check dependency licenses
	@echo "Checking licenses..."
	$(VENV)/bin/pip-licenses --with-urls --format=json > licenses.json
	$(VENV)/bin/python scripts/maintenance/check_licenses.py
	$(call print_ok,"License check completed")

.PHONY: generate-changelog
generate-changelog: ## Generate changelog
	@echo "Generating changelog..."
	$(VENV)/bin/python scripts/maintenance/generate_changelog.py
	$(call print_ok,"Changelog generated")

.PHONY: benchmark
benchmark: ## Run performance benchmarks
	@echo "Running benchmarks..."
	$(VENV)/bin/python tests/performance/benchmarks/run_all_tests.py
	$(call print_ok,"Benchmarks completed")

.PHONY: profile
profile: ## Profile application performance
	@echo "Profiling application..."
	$(VENV)/bin/python -m cProfile -o profile.stats scripts/maintenance/profile_app.py
	$(VENV)/bin/snakeviz profile.stats
	$(call print_ok,"Profiling completed")