# VoidLight MarkItDown - Migration Plan

## Overview

This document outlines the step-by-step migration plan to transform the current project structure into an enterprise-grade architecture.

## Migration Phases

### Phase 1: Preparation (Day 1)
- [ ] Create backup of current project
- [ ] Set up new directory structure
- [ ] Update version control ignore files
- [ ] Create migration scripts

### Phase 2: Core Structure Migration (Day 2-3)

#### 2.1 Documentation Migration
- [ ] Move all top-level documentation to `docs/`
- [ ] Organize documentation by category
- [ ] Create proper index files

#### 2.2 Source Code Reorganization
- [ ] Create new `src/` directory structure
- [ ] Move `packages/voidlight_markitdown/src/voidlight_markitdown/` to `src/voidlight_markitdown/`
- [ ] Move `packages/voidlight_markitdown-mcp/src/voidlight_markitdown_mcp/` to `src/voidlight_markitdown_mcp/`
- [ ] Create interface layer in `src/voidlight_markitdown/interfaces/`
- [ ] Reorganize converters with proper abstraction

#### 2.3 Test Suite Reorganization
- [ ] Create new test structure under `tests/`
- [ ] Separate unit, integration, and e2e tests
- [ ] Move test fixtures to centralized location
- [ ] Update test imports

### Phase 3: Infrastructure Setup (Day 4)

#### 3.1 Container Configuration
- [ ] Create production-ready Dockerfiles
- [ ] Set up multi-stage builds
- [ ] Create docker-compose configurations
- [ ] Add health checks

#### 3.2 CI/CD Enhancement
- [ ] Update GitHub Actions workflows
- [ ] Add security scanning
- [ ] Add performance benchmarking
- [ ] Set up release automation

### Phase 4: Configuration Management (Day 5)

#### 4.1 Environment Configuration
- [ ] Create environment-specific configs
- [ ] Implement configuration validation
- [ ] Add secrets management
- [ ] Create configuration documentation

#### 4.2 Dependency Management
- [ ] Split requirements by environment
- [ ] Pin all dependencies
- [ ] Add security scanning
- [ ] Create dependency update process

### Phase 5: Quality Assurance (Day 6)

#### 5.1 Code Quality
- [ ] Add pre-commit hooks
- [ ] Set up linting and formatting
- [ ] Add type checking
- [ ] Implement code coverage requirements

#### 5.2 Testing Enhancement
- [ ] Add missing unit tests
- [ ] Create integration test suite
- [ ] Add performance benchmarks
- [ ] Implement chaos engineering tests

### Phase 6: Documentation (Day 7)

#### 6.1 Technical Documentation
- [ ] Generate API documentation
- [ ] Create architecture diagrams
- [ ] Write deployment guides
- [ ] Add troubleshooting guides

#### 6.2 User Documentation
- [ ] Update README files
- [ ] Create user guides
- [ ] Add examples
- [ ] Create video tutorials

## Migration Script

```bash
#!/bin/bash
# migration.sh - Automated migration script

set -euo pipefail

echo "Starting VoidLight MarkItDown migration..."

# Create backup
echo "Creating backup..."
cp -r . ../voidlight_markitdown_backup_$(date +%Y%m%d_%H%M%S)

# Create new directory structure
echo "Creating new directory structure..."
mkdir -p src/voidlight_markitdown/{core,converters,interfaces,models,utils,config}
mkdir -p src/voidlight_markitdown_mcp/{server,handlers,protocols,middleware}
mkdir -p tests/{unit,integration,e2e,performance,security,fixtures}
mkdir -p docs/{architecture,api,deployment,development,user-guide}
mkdir -p infrastructure/{terraform,kubernetes,docker,scripts}
mkdir -p config/{environments,logging,security}
mkdir -p scripts/{build,deploy,test,tools}
mkdir -p benchmarks/{converters,load,reports}
mkdir -p examples/{basic,advanced,integrations}
mkdir -p requirements

# Move files
echo "Moving files..."
# ... (detailed move commands)

echo "Migration complete!"
```

## File Mapping

### Documentation Files
| Current Location | New Location |
|-----------------|--------------|
| `ARCHITECTURE_ALIGNMENT_REPORT.md` | `docs/architecture/alignment-report.md` |
| `AUDIT_REPORT.md` | `docs/development/audit-report.md` |
| `CI_CD_VALIDATION_REPORT.md` | `docs/deployment/ci-cd-validation.md` |
| `PRODUCTION_DEPLOYMENT_GUIDE.md` | `docs/deployment/production-guide.md` |
| `README.md` | `README.md` (keep at root) |

### Source Files
| Current Location | New Location |
|-----------------|--------------|
| `packages/voidlight_markitdown/src/voidlight_markitdown/` | `src/voidlight_markitdown/` |
| `packages/voidlight_markitdown-mcp/src/voidlight_markitdown_mcp/` | `src/voidlight_markitdown_mcp/` |

### Test Files
| Current Location | New Location |
|-----------------|--------------|
| `packages/voidlight_markitdown/tests/` | `tests/unit/voidlight_markitdown/` |
| `packages/voidlight_markitdown-mcp/tests/` | `tests/unit/voidlight_markitdown_mcp/` |
| `mcp_client_tests/` | `tests/integration/mcp/` |
| `stress_testing/` | `tests/performance/stress/` |
| `chaos_engineering/` | `tests/security/chaos/` |

### Infrastructure Files
| Current Location | New Location |
|-----------------|--------------|
| `Dockerfile.test` | `infrastructure/docker/Dockerfile.test` |
| `docker-compose.test.yml` | `infrastructure/docker/docker-compose.test.yml` |
| `.github/workflows/` | `.github/workflows/` (keep as is) |

## Import Updates

After moving files, the following imports need to be updated:

```python
# Old import
from voidlight_markitdown.converters import PDFConverter

# New import
from src.voidlight_markitdown.converters.pdf import PDFConverter
```

## Configuration Updates

### pyproject.toml Updates
```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
voidlight_markitdown = ["py.typed"]
voidlight_markitdown_mcp = ["py.typed"]
```

### GitHub Actions Updates
Update all workflow files to use new paths:
```yaml
- name: Run tests
  run: |
    python -m pytest tests/unit/
    python -m pytest tests/integration/
```

## Rollback Plan

If migration fails:
1. Stop all migration activities
2. Restore from backup
3. Document issues encountered
4. Revise migration plan
5. Schedule retry

## Success Criteria

- [ ] All tests pass in new structure
- [ ] CI/CD pipeline runs successfully
- [ ] Documentation is accessible and correct
- [ ] No broken imports
- [ ] Performance benchmarks show no regression
- [ ] Security scans pass

## Timeline

- **Total Duration**: 7 days
- **Daily Checkpoint**: 5 PM
- **Review Meeting**: End of each phase
- **Final Review**: Day 8

## Risk Mitigation

1. **Import Issues**: Use automated tool to update imports
2. **Test Failures**: Run tests after each major move
3. **CI/CD Breaks**: Update workflows incrementally
4. **Documentation Links**: Use find/replace for path updates
5. **Dependency Conflicts**: Test in isolated environment first