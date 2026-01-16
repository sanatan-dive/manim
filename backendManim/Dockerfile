FROM manimcommunity/manim:v0.18.1

USER root

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for cache
COPY requirements.txt .

# Install python dependencies
# Using --user to avoid permission issues if we switch user, or just install as root.
# Root is fine in container for this purpose usually, but manim image expects manimuser.
# Let's install globally as root.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Fix permissions for Prisma
# Allow the non-root user (manimuser) to write to the site-packages directory
# This is necessary because 'prisma generate' writes the schema.prisma file to the package directory
RUN chmod -R 777 /usr/local/lib/python3.11/site-packages/prisma

# Create directories and fix permissions
RUN mkdir -p media/videos generated && \
    chown -R manimuser:manimuser /app

# Switch to non-root user
USER manimuser

# Expose API port
EXPOSE 8000

# Default command (will be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
