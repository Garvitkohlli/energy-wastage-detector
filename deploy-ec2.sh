#!/bin/bash

# AWS EC2 Deployment Script for Energy Monitoring System

echo "=========================================="
echo "  AWS EC2 Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "Docker installed. Please log out and log back in for group changes to take effect."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed."
fi

# Create data directory
mkdir -p data

# Generate secret key if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "SECRET_KEY=$SECRET_KEY" > .env
    echo "FLASK_ENV=production" >> .env
    echo ".env file created with random SECRET_KEY"
fi

# Build Docker image
echo ""
echo "Building Docker image..."
docker-compose build

# Start the application
echo ""
echo "Starting application..."
docker-compose up -d

# Wait for application to start
echo ""
echo "Waiting for application to start..."
sleep 10

# Check if application is running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "=========================================="
    echo "  ✅ Deployment Successful!"
    echo "=========================================="
    echo ""
    echo "Application is running on:"
    echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop app:     docker-compose down"
    echo "  Restart app:  docker-compose restart"
    echo "  Update app:   git pull && docker-compose up -d --build"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Check logs with: docker-compose logs"
fi
