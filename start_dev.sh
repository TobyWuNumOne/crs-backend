#!/bin/bash

# ===========================================
# Clinic Registration System - Development Environment Startup
# ===========================================
# This script starts the complete local development environment
# including PostgreSQL database and FastAPI backend
#
# Usage: ./start_dev.sh [start|stop|restart|logs|status]
# ===========================================

set -e

COMPOSE_FILE="docker-compose.dev.yml"
PROJECT_NAME="crs-dev"

function show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start   - Start development environment (default)"
    echo "  stop    - Stop development environment"
    echo "  restart - Restart development environment"
    echo "  logs    - Show logs (use Ctrl+C to exit)"
    echo "  status  - Show container status"
    echo "  clean   - Stop and remove all containers and volumes"
    echo ""
}

function start_dev() {
    echo "=========================================="
    echo "  Starting Development Environment       "
    echo "=========================================="
    echo ""
    echo "Services:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --build
    
    echo ""
    echo "✅ Development environment started!"
    echo ""
    echo "To view logs: $0 logs"
    echo "To stop: $0 stop"
}

function stop_dev() {
    echo "Stopping development environment..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    echo "✅ Development environment stopped!"
}

function restart_dev() {
    stop_dev
    start_dev
}

function show_logs() {
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
}

function show_status() {
    echo "Container Status:"
    echo "----------------------------------------"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
}

function clean_dev() {
    echo "Stopping and removing all development containers and volumes..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --volumes --remove-orphans
    echo "✅ Development environment cleaned!"
}

# Main script
case "${1:-start}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_dev
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
