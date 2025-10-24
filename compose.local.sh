source env.local

echo "🐳 Starting Perplexity MCP Server with Docker Compose (Local Mode)..."

# Check if mcp-shared network exists, create if not
if ! docker network ls | grep -q "mcp-shared"; then
    echo "📡 Creating mcp-shared network..."
    docker network create mcp-shared
fi

# Ensure data directory exists with correct permissions
echo "📁 Setting up data directory..."
mkdir -p ./data/mcp-perplexity
# Fix ownership to match the current user (who should match container UID 1000)
if [ -w ./data ]; then
    echo "✓ Data directory is writable"
else
    echo "⚠️  Fixing data directory permissions..."
    sudo chown -R $USER:$USER ./data
fi

# Stop and remove existing containers to ensure fresh deployment
echo "🛑 Stopping and removing existing containers..."
docker compose -f docker-compose.local.yml down

# Remove existing images to force rebuild
echo "🗑️  Removing existing images to force rebuild..."
docker rmi -f mcp-perplexity-mcp-perplexity 2>/dev/null || true

# Build and start services
echo "🏗️  Building and starting services..."
docker compose -f docker-compose.local.yml up -d --build --remove-orphans

echo "✅ Perplexity MCP Server is running in local mode!"
echo "🔧 MCP Endpoint: http://localhost:8011/perplexity/"
echo "🏥 Health Check: http://localhost:8011/health"
echo ""
echo "For reverse proxy configuration, add to your Caddyfile:"
echo "    handle_path /perplexity/* {"
echo "        reverse_proxy mcp-perplexity-local:8011"
echo "    }"
echo ""
echo "To check logs:"
echo "  docker compose -f docker-compose.local.yml logs -f"
echo ""
echo "To stop:"
echo "  docker compose -f docker-compose.local.yml down"
