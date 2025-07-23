# Multi-stage Dockerfile for voidlight-markitdown
# Optimized for production with security and performance in mind

# Build stage
FROM python:3.11-slim as builder

# Build arguments
ARG PYTHON_VERSION=3.11
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels
LABEL maintainer="VoidLight <voidlight@example.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="voidlight-markitdown" \
      org.label-schema.description="Document converter with Korean language support" \
      org.label-schema.url="https://github.com/voidlight/voidlight_markitdown" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/voidlight/voidlight_markitdown" \
      org.label-schema.vendor="VoidLight" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements/production.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
COPY . /app
WORKDIR /app

# Install the package
RUN pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For PDF processing
    poppler-utils \
    # For image processing
    tesseract-ocr \
    tesseract-ocr-kor \
    # For audio processing
    ffmpeg \
    # For Korean NLP
    default-jre \
    # Health check
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r markitdown && useradd -r -g markitdown markitdown

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp /app/cache && \
    chown -R markitdown:markitdown /app

# Switch to non-root user
USER markitdown

WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import voidlight_markitdown; print('healthy')" || exit 1

# Default command
CMD ["python", "-m", "voidlight_markitdown"]