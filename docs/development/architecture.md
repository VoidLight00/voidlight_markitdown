# VoidLight MarkItDown - Enterprise Architecture

## Overview

VoidLight MarkItDown is an enterprise-grade document-to-markdown conversion system designed for high scalability, maintainability, and extensibility. This document outlines the architectural decisions, design patterns, and structure of the project.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Project Structure](#project-structure)
3. [Design Principles](#design-principles)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Development Guidelines](#development-guidelines)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Clients                          │
│  (CLI, Python API, MCP Clients, REST API, Message Queue)       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  (Rate Limiting, Authentication, Request Routing)                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Orchestration Layer                   │
│  (Workflow Management, Request Distribution, Load Balancing)     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│    Core Conversion Engine    │     │    MCP Protocol Server      │
│  (Document Processing Core)  │     │  (Model Context Protocol)   │
└─────────────────────────────┘     └─────────────────────────────┘
                    │                               │
                    ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Converter Plugin System                      │
│  (PDF, DOCX, HTML, Audio, Image, Korean NLP, etc.)             │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Storage & Cache Layer                      │
│  (Redis Cache, Object Storage, Database)                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring & Observability                    │
│  (Metrics, Logging, Tracing, Health Checks)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

### Enterprise-Grade Directory Layout

```
voidlight_markitdown/
├── .github/                      # GitHub configuration
│   ├── workflows/                # CI/CD workflows
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md # PR template
│
├── docs/                         # Documentation root
│   ├── architecture/            # Architecture documentation
│   ├── api/                     # API documentation
│   ├── deployment/              # Deployment guides
│   ├── development/             # Developer guides
│   └── user-guide/              # User documentation
│
├── src/                         # Source code root
│   ├── voidlight_markitdown/    # Core library
│   │   ├── core/               # Core business logic
│   │   ├── converters/         # Converter implementations
│   │   ├── interfaces/         # Abstract interfaces
│   │   ├── models/             # Data models
│   │   ├── utils/              # Utility functions
│   │   └── config/             # Configuration management
│   │
│   └── voidlight_markitdown_mcp/ # MCP server
│       ├── server/             # MCP server implementation
│       ├── handlers/           # Request handlers
│       ├── protocols/          # Protocol implementations
│       └── middleware/         # Server middleware
│
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   ├── performance/            # Performance tests
│   ├── security/               # Security tests
│   └── fixtures/               # Test fixtures
│
├── infrastructure/              # Infrastructure as Code
│   ├── terraform/              # Terraform configurations
│   ├── kubernetes/             # Kubernetes manifests
│   ├── docker/                 # Docker configurations
│   └── scripts/                # Infrastructure scripts
│
├── config/                      # Configuration files
│   ├── environments/           # Environment-specific configs
│   ├── logging/                # Logging configurations
│   └── security/               # Security configurations
│
├── scripts/                     # Development & operations scripts
│   ├── build/                  # Build scripts
│   ├── deploy/                 # Deployment scripts
│   ├── test/                   # Test automation scripts
│   └── tools/                  # Development tools
│
├── benchmarks/                  # Performance benchmarks
│   ├── converters/             # Converter benchmarks
│   ├── load/                   # Load testing
│   └── reports/                # Benchmark reports
│
├── examples/                    # Usage examples
│   ├── basic/                  # Basic usage examples
│   ├── advanced/               # Advanced scenarios
│   └── integrations/           # Integration examples
│
├── .docker/                     # Docker development environment
├── .vscode/                     # VS Code configuration
├── .idea/                       # IntelliJ IDEA configuration
│
├── pyproject.toml              # Project configuration
├── setup.cfg                   # Setup configuration
├── requirements/               # Requirements files
│   ├── base.txt               # Base requirements
│   ├── dev.txt                # Development requirements
│   ├── test.txt               # Test requirements
│   └── prod.txt               # Production requirements
│
├── Makefile                    # Build automation
├── LICENSE                     # License file
├── README.md                   # Project README
├── CHANGELOG.md                # Version changelog
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy
└── CODE_OF_CONDUCT.md          # Code of conduct
```

## Design Principles

### 1. Clean Architecture
- **Dependency Rule**: Dependencies point inward. Core business logic has no dependencies on external frameworks
- **Layer Separation**: Clear boundaries between layers (Domain, Application, Infrastructure, Presentation)
- **Testability**: All components are designed to be easily testable in isolation

### 2. SOLID Principles
- **Single Responsibility**: Each class/module has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes must be substitutable for base classes
- **Interface Segregation**: Many specific interfaces are better than one general interface
- **Dependency Inversion**: Depend on abstractions, not concretions

### 3. Domain-Driven Design
- **Bounded Contexts**: Clear boundaries between different domains
- **Ubiquitous Language**: Consistent terminology throughout the codebase
- **Aggregate Roots**: Well-defined entry points to domain logic

### 4. Twelve-Factor App
- **Codebase**: One codebase tracked in revision control
- **Dependencies**: Explicitly declare and isolate dependencies
- **Config**: Store config in the environment
- **Backing Services**: Treat backing services as attached resources
- **Build, Release, Run**: Strictly separate build and run stages
- **Processes**: Execute the app as stateless processes
- **Port Binding**: Export services via port binding
- **Concurrency**: Scale out via the process model
- **Disposability**: Maximize robustness with fast startup and graceful shutdown
- **Dev/Prod Parity**: Keep development, staging, and production as similar as possible
- **Logs**: Treat logs as event streams
- **Admin Processes**: Run admin/management tasks as one-off processes

## Component Architecture

### Core Components

#### 1. Conversion Engine
```python
# src/voidlight_markitdown/core/engine.py
class ConversionEngine:
    """Core conversion orchestration engine"""
    def __init__(self, config: EngineConfig):
        self.converter_registry = ConverterRegistry()
        self.pipeline_manager = PipelineManager()
        self.cache_manager = CacheManager()
        
    async def convert(self, source: Source) -> ConversionResult:
        """Main conversion entry point"""
        pass
```

#### 2. Converter Registry
```python
# src/voidlight_markitdown/core/registry.py
class ConverterRegistry:
    """Plugin registry for converters"""
    def register(self, converter: BaseConverter) -> None:
        """Register a new converter"""
        pass
        
    def get_converter(self, mime_type: str) -> BaseConverter:
        """Get appropriate converter for mime type"""
        pass
```

#### 3. Pipeline Manager
```python
# src/voidlight_markitdown/core/pipeline.py
class PipelineManager:
    """Manages conversion pipelines"""
    def create_pipeline(self, steps: List[PipelineStep]) -> Pipeline:
        """Create a new conversion pipeline"""
        pass
```

### Converter Architecture

Each converter follows a standard interface:

```python
# src/voidlight_markitdown/interfaces/converter.py
from abc import ABC, abstractmethod

class BaseConverter(ABC):
    """Base converter interface"""
    
    @abstractmethod
    async def convert(self, source: bytes, options: ConversionOptions) -> ConversionResult:
        """Convert source to markdown"""
        pass
    
    @abstractmethod
    def supports(self, mime_type: str) -> bool:
        """Check if converter supports mime type"""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of supported formats"""
        pass
```

## Data Flow

### Conversion Pipeline

1. **Input Reception**
   - Receive document via API/CLI/MCP
   - Validate input parameters
   - Generate request ID for tracking

2. **Format Detection**
   - Use Magika for file type detection
   - Fall back to extension-based detection
   - Select appropriate converter

3. **Pre-Processing**
   - Security scanning
   - Size validation
   - Encoding detection (especially for Korean)

4. **Conversion**
   - Load converter plugin
   - Apply conversion options
   - Execute conversion pipeline

5. **Post-Processing**
   - Format validation
   - Metadata extraction
   - Korean text normalization (if applicable)

6. **Output Delivery**
   - Cache results
   - Return to client
   - Log metrics

## Security Architecture

### Security Layers

1. **Input Validation**
   - File size limits
   - Format validation
   - Malware scanning

2. **Process Isolation**
   - Sandboxed converter execution
   - Resource limits (CPU, memory, time)
   - Network isolation for converters

3. **Authentication & Authorization**
   - API key management
   - Rate limiting
   - Access control lists

4. **Data Protection**
   - Encryption in transit (TLS)
   - Encryption at rest
   - Secure temporary file handling

## Deployment Architecture

### Container Architecture

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    image: voidlight-markitdown:latest
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://cache:6379
    depends_on:
      - cache
      
  mcp-server:
    image: voidlight-markitdown-mcp:latest
    ports:
      - "3001:3001"
    environment:
      - CONVERTER_API_URL=http://api:8080
      
  cache:
    image: redis:7-alpine
    volumes:
      - cache_data:/data
      
  monitoring:
    image: prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
volumes:
  cache_data:
```

### Kubernetes Architecture

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voidlight-markitdown
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voidlight-markitdown
  template:
    metadata:
      labels:
        app: voidlight-markitdown
    spec:
      containers:
      - name: api
        image: voidlight-markitdown:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "2000m"
```

## Development Guidelines

### Code Style
- Follow PEP 8 with type hints
- Use Black for formatting
- Use isort for import sorting
- Maintain >90% test coverage

### Git Workflow
- Feature branches from `develop`
- Pull requests require 2 approvals
- Automated CI/CD pipeline
- Semantic versioning

### Testing Strategy
- Unit tests for all business logic
- Integration tests for converters
- E2E tests for critical paths
- Performance benchmarks

### Documentation
- Docstrings for all public APIs
- Architecture Decision Records (ADRs)
- API documentation with OpenAPI
- User guides with examples