# ==============================================================================
# The Churninator - Dramatiq Agent Worker (with Virtual Display)
# ==============================================================================
# Start from a slim Python base image to keep the size down.
FROM python:3.11-slim-bookworm

# --- Stage 1: System Dependencies ---
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install essential packages. This is the most critical part.
# - xvfb: The virtual framebuffer.
# - curl, git: Standard utilities.
# - The long list of `lib...` packages are the REQUIRED browser dependencies for Playwright.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xvfb \
    curl \
    git \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Install UV and Python Dependencies ---
WORKDIR /app

# Install uv for fast dependency management.
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency definitions.
COPY ./pyproject.toml ./uv.lock* ./

# Create a virtual environment and install dependencies using uv.
RUN uv venv
# The source code will be mounted later, so we install our package in a second step.
RUN uv sync --locked

# --- Stage 3: The Entrypoint Script ---
# This is the magic. We create a script that starts the virtual display
# and then launches the Dramatiq worker process.
COPY ./backend/worker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# --- Final Configuration ---
# Activate the virtual environment.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
# Tell Playwright where to find the browser binaries we'll install
ENV PLAYWRIGHT_BROWSERS_PATH=/pw_browsers

# The entrypoint script will be the command that runs when the container starts.
ENTRYPOINT ["/entrypoint.sh"]
