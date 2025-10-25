# Perplexity MCP Server

MCP server providing Perplexity AI-powered web search and research capabilities. All tools return JSON responses directly from the Perplexity API.

## Available Tools

### Basic Tools
- `save_tool_notes` - Save usage notes for any MCP tool
- `read_tool_notes` - Read historical notes for a tool

### Perplexity Search Tools
- `perplexity_sonar` - Fast search with citations (128K context)
- `perplexity_sonar_pro` - Advanced search with 2x more results (200K context)
- `perplexity_sonar_reasoning` - Quick reasoning with CoT analysis (128K context)
- `perplexity_sonar_reasoning_pro` - Advanced reasoning with 2x more results (128K context)
- `perplexity_sonar_deep_research` - Exhaustive research across hundreds of sources (supports `reasoning_effort` parameter)

## Installation

### Requirements
- Docker and Docker Compose
- Perplexity API key from https://www.perplexity.ai/settings/api

### Configuration

Create `.env.local`:
```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
MCP_NAME=perplexity
PORT=8011
CONTAINER_NAME=mcp-perplexity-local
```

### Run

```bash
# Start server
./compose.local.sh

# View logs
./logs.sh

# Stop server
docker compose -f docker-compose.local.yml down
```

Server runs at `http://localhost:8011/perplexity/`

### Claude Desktop Setup

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8011/perplexity/"]
    }
  }
}
```

## Response Format

All tools return JSON containing:
- `choices[0].message.content` - AI response text
- `citations` - Source URLs
- `search_results` - Search metadata
- `usage` - Token counts and costs

## Development

### Project Structure
```
backend/
├── main.py              # Main MCP server
├── mcp_service.py       # Core utilities
├── mcp_resources.py     # Documentation
└── requirements.txt     # Dependencies
```

### Adding Tools
1. Implement in `backend/`
2. Register in `backend/main.py`
3. Update docs in `backend/mcp_resources.py`

## License

MIT
