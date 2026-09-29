#!/usr/bin/env bash
# healthcheck.sh

echo "=========================================="
echo "Incident-to-Regression Health Check"
echo "=========================================="

echo -e "\n1. Checking API Liveness..."
if curl -s -f http://localhost:8000/api/v1/health | grep -q '"status":"ok"'; then
    echo "✅ API is operational"
else
    echo "❌ API is unreachable or returned error"
fi

echo -e "\n2. Checking Database Connectivity (via API)..."
if curl -s -f http://localhost:8000/api/v1/health/database | grep -q '"status":"ok"'; then
    echo "✅ Database connection is healthy"
else
    echo "❌ Database is unavailable"
fi

echo -e "\n3. Checking Frontend..."
if curl -s -I http://localhost:5173 | grep -q "HTTP/1.1 200"; then
    echo "✅ Frontend is reachable"
else
    echo "❌ Frontend is unreachable"
fi

echo -e "\nDone."
