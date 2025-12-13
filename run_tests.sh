#!/bin/bash

# Build and start Docker services
echo "Building and starting Docker services..."
docker-compose up -d --build

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Run tests
echo "Running tests..."
docker-compose exec app uv run pytest

# Stop services
echo "Stopping services..."
docker-compose down