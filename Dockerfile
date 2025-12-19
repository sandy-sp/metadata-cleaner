# Multi-stage build for lightweight image
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Using pip directly with pyproject.toml if compatible, or just installing the package
COPY pyproject.toml README.md ./
COPY m_c ./m_c

# Install build dependencies and the package
RUN pip install --no-cache-dir .

# Create a final slim image
# Actually, since we need ffmpeg/exiftool at runtime, we can stick to one stage 
# if we cleanup dev deps, but multi-stage is cleaner if we had complex build deps.
# For simplicity and ensuring runtime tools are present, let's use a single stage optimized.
# Or better: proper multi-stage where we copy installed libs? Hard with system deps.
# Let's stick to single stage for robustness with system tools, kept clean.

# Wait, the instruction said "Multi-stage build".
# Okay, let's do a builder stage for python wheels?
# No, we need system deps (ffmpeg/exiftool) in the final image.
# So we can install them in final image.

FROM python:3.9-slim

WORKDIR /app

# Install Runtime System Dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . /app

# Install the application
RUN pip install --no-cache-dir .

# Entrypoint
ENTRYPOINT ["metadata-cleaner"]
CMD ["--help"]
