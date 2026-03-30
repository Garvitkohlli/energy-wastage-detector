#!/bin/bash

# Quick Deploy Script for AWS EC2
# Run this on your EC2 instance after uploading the code

set -e

echo "=========================================="
echo "  Quick Deploy - Energy Monitoring System"
echo "=========================================="
echo ""

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
PORT=5000
EOF
    echo "✅ .env file created"
fi

# Create data directory
mkdir -p data

# Build and start
echo ""
echo "🏗️  Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting application..."
docker-compose up -d

# Wait for startup
echo ""
echo "⏳ Waiting for application to start..."
sleep 15

# Check status
if docker-compose ps | grep -q "Up"; then
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
    
    echo ""
    echo "=========================================="
    echo "  ✅ DEPLOYMENT SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "🌐 Access your application:"
    echo "   http://$PUBLIC_IP:5000"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop:          docker-compose down"
    echo "   Restart:       docker-compose restart"
    echo "   Update:        git pull && docker-compose up -d --build"
    echo ""
    echo "🔐 Default login:"
    echo "   Username: demo"
    echo "   Password: demo123"
    echo ""
    echo "⚠️  Remember to:"
    echo "   1. Change SECRET_KEY in .env file"
    echo "   2. Create your own user account"
    echo "   3. Setup Nginx for production (optional)"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check logs: docker-compose logs"
fi
