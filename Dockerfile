FROM python:latest

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if they exist
COPY requirements.txt* ./

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

CMD ["code-server", "--bind-addr", "0.0.0.0:8443", "--auth", "none"]
