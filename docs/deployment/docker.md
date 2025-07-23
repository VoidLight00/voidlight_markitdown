# Docker Deployment Guide

This guide covers deploying VoidLight MarkItDown using Docker containers.

## Table of Contents

1. [Docker Images](#docker-images)
2. [Basic Deployment](#basic-deployment)
3. [Docker Compose](#docker-compose)
4. [Configuration](#configuration)
5. [Volumes & Persistence](#volumes-persistence)
6. [Networking](#networking)
7. [Security](#security)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## Docker Images

### Official Images

```bash
# Pull the latest image
docker pull voidlight/markitdown:latest

# Pull specific version
docker pull voidlight/markitdown:0.1.13

# Pull with Korean support
docker pull voidlight/markitdown:latest-korean

# Pull MCP server image
docker pull voidlight/markitdown-mcp:latest
```

### Building Custom Images

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    tesseract-ocr \
    tesseract-ocr-kor \
    mecab \
    mecab-ko \
    mecab-ko-dic \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY packages/voidlight_markitdown /app/voidlight_markitdown
COPY packages/voidlight_markitdown-mcp /app/voidlight_markitdown-mcp

# Install packages
RUN pip install -e voidlight_markitdown[all]
RUN pip install -e voidlight_markitdown-mcp

# Create non-root user
RUN useradd -m -u 1000 converter
USER converter

# Expose ports
EXPOSE 8080

# Default command
CMD ["voidlight-markitdown-mcp", "--mode", "http", "--port", "8080"]
```

Build the image:
```bash
docker build -t voidlight/markitdown:custom .
```

## Basic Deployment

### Running the Container

```bash
# Basic run
docker run -d \
  --name voidlight-markitdown \
  -p 8080:8080 \
  voidlight/markitdown:latest

# With volume mount
docker run -d \
  --name voidlight-markitdown \
  -p 8080:8080 \
  -v /path/to/documents:/data \
  voidlight/markitdown:latest

# With environment variables
docker run -d \
  --name voidlight-markitdown \
  -p 8080:8080 \
  -e VOIDLIGHT_KOREAN_MODE=true \
  -e VOIDLIGHT_MAX_FILE_SIZE=104857600 \
  voidlight/markitdown:latest
```

### Interactive Mode

```bash
# CLI usage
docker run --rm -it \
  -v $(pwd):/data \
  voidlight/markitdown:latest \
  voidlight-markitdown /data/document.pdf -o /data/output.md

# Shell access
docker run --rm -it \
  voidlight/markitdown:latest \
  /bin/bash
```

## Docker Compose

### Basic Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  markitdown:
    image: voidlight/markitdown:latest
    container_name: voidlight-markitdown
    ports:
      - "8080:8080"
    environment:
      - VOIDLIGHT_KOREAN_MODE=true
      - VOIDLIGHT_LOG_LEVEL=INFO
      - MCP_SERVER_MODE=http
    volumes:
      - ./data:/data
      - ./config:/config
      - ./logs:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  markitdown:
    image: voidlight/markitdown:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    ports:
      - "8080-8082:8080"
    environment:
      - VOIDLIGHT_KOREAN_MODE=true
      - VOIDLIGHT_MAX_WORKERS=4
      - VOIDLIGHT_CACHE_ENABLED=true
      - REDIS_URL=redis://redis:6379
    volumes:
      - document-data:/data
      - config-data:/config
      - log-data:/logs
    networks:
      - backend
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - backend

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: voidlight
      POSTGRES_USER: voidlight
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - markitdown
    networks:
      - backend

volumes:
  document-data:
  config-data:
  log-data:
  redis-data:
  postgres-data:

networks:
  backend:
    driver: bridge
```

### Start Services

```bash
# Start all services
docker-compose up -d

# Scale service
docker-compose up -d --scale markitdown=5

# View logs
docker-compose logs -f markitdown

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

```bash
# Core settings
VOIDLIGHT_KOREAN_MODE=true
VOIDLIGHT_MAX_FILE_SIZE=104857600  # 100MB
VOIDLIGHT_TIMEOUT=300              # 5 minutes
VOIDLIGHT_MAX_WORKERS=8

# MCP server settings
MCP_SERVER_MODE=http
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0

# Logging
VOIDLIGHT_LOG_LEVEL=INFO
VOIDLIGHT_LOG_FILE=/logs/voidlight.log

# Cache settings
VOIDLIGHT_CACHE_ENABLED=true
REDIS_URL=redis://redis:6379

# Security
API_KEY_REQUIRED=true
ALLOWED_ORIGINS=https://example.com
```

### Configuration File Mount

```yaml
# docker-compose.yml
services:
  markitdown:
    image: voidlight/markitdown:latest
    volumes:
      - ./config.yaml:/app/config.yaml
    environment:
      - CONFIG_FILE=/app/config.yaml
```

Config file example:
```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 4

conversion:
  korean_mode: true
  ocr_enabled: true
  max_file_size: 104857600
  timeout: 300

cache:
  enabled: true
  redis_url: redis://redis:6379
  ttl: 3600

logging:
  level: INFO
  file: /logs/voidlight.log
  format: json
```

## Volumes & Persistence

### Volume Configuration

```yaml
volumes:
  # Document storage
  - type: volume
    source: documents
    target: /data
    
  # Configuration
  - type: bind
    source: ./config
    target: /config
    read_only: true
    
  # Logs
  - type: volume
    source: logs
    target: /logs
    
  # Temporary files
  - type: tmpfs
    target: /tmp
    tmpfs:
      size: 1gb
```

### Backup Strategy

```bash
# Backup volumes
docker run --rm \
  -v documents:/data \
  -v $(pwd)/backup:/backup \
  alpine \
  tar -czf /backup/documents-$(date +%Y%m%d).tar.gz -C /data .

# Restore volumes
docker run --rm \
  -v documents:/data \
  -v $(pwd)/backup:/backup \
  alpine \
  tar -xzf /backup/documents-20240115.tar.gz -C /data
```

## Networking

### Container Networking

```yaml
# docker-compose.yml
services:
  markitdown:
    networks:
      - frontend
      - backend
    
  nginx:
    networks:
      - frontend
    
  redis:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### Nginx Proxy Configuration

```nginx
# nginx.conf
upstream markitdown {
    least_conn;
    server markitdown_1:8080;
    server markitdown_2:8080;
    server markitdown_3:8080;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://markitdown;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long conversions
        proxy_read_timeout 300s;
        proxy_connect_timeout 30s;
        proxy_send_timeout 300s;
    }
    
    location /sse {
        proxy_pass http://markitdown;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## Security

### Security Best Practices

```dockerfile
# Secure Dockerfile
FROM python:3.9-slim

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash converter

# Install only necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install as non-root
USER converter
WORKDIR /home/converter

COPY --chown=converter:converter requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=converter:converter . .

# Read-only root filesystem
RUN chmod -R a-w /home/converter

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run as non-root
EXPOSE 8080
CMD ["python", "-m", "voidlight_markitdown_mcp"]
```

### Environment Hardening

```yaml
# docker-compose.secure.yml
services:
  markitdown:
    image: voidlight/markitdown:latest
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    environment:
      - API_KEY_REQUIRED=true
      - ALLOWED_IPS=10.0.0.0/8
```

## Monitoring

### Health Checks

```yaml
services:
  markitdown:
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Prometheus Metrics

```yaml
services:
  markitdown:
    environment:
      - METRICS_ENABLED=true
      - METRICS_PORT=9090
    ports:
      - "9090:9090"
  
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9091:9090"
```

Prometheus configuration:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'markitdown'
    static_configs:
      - targets: ['markitdown:9090']
```

### Logging

```yaml
services:
  markitdown:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=markitdown"
    
  # Or use centralized logging
  markitdown-syslog:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://logstash:5514"
        tag: "markitdown"
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker logs voidlight-markitdown
   
   # Check container status
   docker ps -a
   
   # Inspect container
   docker inspect voidlight-markitdown
   ```

2. **Permission errors**
   ```bash
   # Fix volume permissions
   docker exec voidlight-markitdown chown -R converter:converter /data
   ```

3. **Memory issues**
   ```bash
   # Check resource usage
   docker stats voidlight-markitdown
   
   # Increase memory limit
   docker update --memory="4g" voidlight-markitdown
   ```

4. **Network connectivity**
   ```bash
   # Test internal networking
   docker exec voidlight-markitdown ping redis
   
   # Check port binding
   docker port voidlight-markitdown
   ```

### Debug Mode

```bash
# Run with debug logging
docker run -it \
  -e VOIDLIGHT_LOG_LEVEL=DEBUG \
  -e PYTHONUNBUFFERED=1 \
  voidlight/markitdown:latest

# Shell access for debugging
docker exec -it voidlight-markitdown /bin/bash

# Run specific command
docker exec voidlight-markitdown voidlight-markitdown --version
```

### Performance Profiling

```bash
# Run with profiling enabled
docker run -d \
  --name markitdown-profile \
  -e PROFILING_ENABLED=true \
  -v $(pwd)/profiles:/profiles \
  voidlight/markitdown:latest

# Analyze profile data
docker exec markitdown-profile python -m pstats /profiles/profile.stats
```

---

<div align="center">
  <p>For Kubernetes deployment, see <a href="kubernetes.md">Kubernetes Guide</a></p>
  <p><a href="../">Back to Documentation Home</a></p>
</div>