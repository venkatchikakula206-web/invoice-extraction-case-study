#!/bin/bash

# Invoice Extraction App - Production Startup Script
# This script ensures clean startup by stopping any existing processes

set -e

echo "🧹 Cleaning up existing processes..."

# Stop any Docker containers
docker compose down 2>/dev/null || true

# Kill any processes on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Kill any Python or Node processes that might be running the app
pkill -f "python -m app" 2>/dev/null || true
pkill -f "next" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

echo "✅ Cleanup complete"

echo ""
echo "🔨 Building Docker images..."
docker compose build

echo ""
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Backend may still be starting..."
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200\|307"; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Invoice Extraction App is ready!"
echo ""
echo "   Open in browser: http://localhost:3000"
echo ""
echo "   To view logs:    docker compose logs -f"
echo "   To stop:         docker compose down"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
