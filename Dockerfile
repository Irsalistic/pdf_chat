FROM python:3.11-slim AS base

# Install system dependencies including Python and pip
RUN apt-get update -y && apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the FastAPI application code
COPY . .

# Install production dependencies.
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8003

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
