#!/bin/bash

echo "Building and starting Cephalon-Onni Docker containers..."

# Build and start all services
docker-compose up --build -d

echo "Waiting for services to be ready..."
sleep 10

# Check if containers are running
echo "Checking container status:"
docker-compose ps

echo ""
echo "Testing backend health..."
curl -f http://localhost:8000/docs || echo "Backend not responding on port 8000"

echo ""
echo "Testing frontend..."
curl -f http://localhost:8080 || echo "Frontend not responding on port 8080"

echo ""
echo "Docker setup test completed!"