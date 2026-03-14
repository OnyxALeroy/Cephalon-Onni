# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libselinux1-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to cleanly isolate packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runner (Final Image)
# ==========================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Make sure we use the virtual environment's Python
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Create log directory with correct ownership
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

# Install only runtime dependencies (if any are strictly required by your packages, e.g., libpq for postgres)
# RUN apt-get update && apt-get install -y --no-install-recommends <runtime-deps> && rm -rf /var/lib/apt/lists/*

# Copy ONLY the fully built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code and assign ownership to the non-root user
COPY --chown=appuser:appgroup app/ ./app

# Switch to the non-root user
USER appuser

CMD ["python", "app/main.py"]
