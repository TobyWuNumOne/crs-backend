#!/bin/bash

# ===========================================
# Clinic Registration System - Test Runner
# ===========================================
# This script runs tests in an isolated Docker environment
# Uses docker-compose.test.yml with different ports and container names
# to avoid conflicts with the development environment
#
# Dev Environment:  Port 5432 (DB), Port 8000 (Backend), crs-dev-* containers
# Test Environment: Port 5433 (DB), Port 8001 (Backend), crs-test-* containers
# ===========================================

set -e

COMPOSE_FILE="docker-compose.test.yml"
PROJECT_NAME="crs-test"

echo "=========================================="
echo "  Running Tests in Isolated Environment  "
echo "=========================================="

# Check if development containers are running (info only)
echo ""
echo "[Info] Checking development environment status..."
if docker ps | grep -q "crs-dev"; then
    echo "[Info] Development containers are running (will not be affected)"
fi

# Clean up any previous test containers
echo ""
echo "[Step 1/5] Cleaning up previous test containers..."
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --volumes --remove-orphans 2>/dev/null || true

# Build and start Docker services for testing
echo ""
echo "[Step 2/5] Building and starting test environment..."
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --build

# Wait for database to be ready (using healthcheck)
echo ""
echo "[Step 3/5] Waiting for database to be ready..."
timeout=60
counter=0
until docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T db pg_isready -U testuser -d testdb > /dev/null 2>&1; do
    counter=$((counter + 1))
    if [ $counter -ge $timeout ]; then
        echo "[Error] Database failed to start within $timeout seconds"
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --volumes
        exit 1
    fi
    echo "  Waiting for database... ($counter/$timeout)"
    sleep 1
done
echo "[OK] Database is ready!"

# Wait a bit more for the backend to be fully ready
echo ""
echo "[Step 4/5] Waiting for backend to be ready..."
sleep 5

# Run tests
echo ""
echo "[Step 5/5] Running tests..."
echo "----------------------------------------"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T backend uv run pytest -v
TEST_EXIT_CODE=$?
echo "----------------------------------------"

# Clean up test containers
echo ""
echo "[Cleanup] Stopping and removing test containers..."
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --volumes

# Report result
echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "=========================================="
    echo "  ✅ All tests passed!                   "
    echo "=========================================="
else
    echo "=========================================="
    echo "  ❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
    echo "=========================================="
fi

exit $TEST_EXIT_CODE