# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

# Make pip installs more resilient on slow/unstable networks.
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_RETRIES=12
ARG PIP_INDEX_URL=https://pypi.org/simple

# Copy runtime requirements first for better Docker layer caching
COPY requirements.runtime.txt .

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary -r requirements.runtime.txt -i ${PIP_INDEX_URL}

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p app/models

# Expose port
EXPOSE 8000

# Train models during image build so the API starts with ready-to-use artifacts.
RUN python train_model.py

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
