FROM python:3.13

WORKDIR /app

# Install system tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2 for ARM64 (Apple Silicon)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Copy CodeArtifact auth script
COPY scripts/pip-auth-codeartifact.sh /app/scripts/
RUN chmod +x /app/scripts/pip-auth-codeartifact.sh

# Copy entrypoint script
COPY scripts/entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/entrypoint.sh

# Copy requirements file
COPY requirements.txt .

COPY render_rig2 /app/render_rig2

# Set entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command (override in docker-compose)
CMD ["bash"]