# Perplexity MCP Server

MCP server providing Perplexity AI-powered web search and research capabilities through the Model Context Protocol. Build intelligent agents that can search, analyze, and reason about web content.

## Architecture

**Direct JSON Response Design**

All Perplexity tools return complete JSON responses directly from the API:

- **Perplexity Tools**: Return full JSON responses from the Perplexity API
- **Rich Metadata**: JSON includes content, citations, search results, and usage statistics
- **Client-Side Processing**: Process responses as needed in your application
- **Pattern**: Make request → Receive JSON → Parse and use data
- **Benefits**: Simple, direct access to all response data without intermediate file storage

**Modular Design**

Each tool is implemented with comprehensive parameter documentation, minimizing token usage and improving maintainability.

## Available Tools

### Basic Tools

#### save_tool_notes
Save usage notes and lessons learned about any MCP tool.

**Parameters:**
- `tool_name` (required): Name of the tool to document
- `markdown_notes` (required): Markdown-formatted notes

**Example:**
```python
save_tool_notes(
    tool_name="perplexity_search",
    markdown_notes="**Best Practice:** Keep queries specific for optimal results."
)
```

#### read_tool_notes
Read all historical usage notes for a specific MCP tool.

**Parameters:**
- `tool_name` (required): Name of the tool to read notes for

---

### Perplexity Search & Research Tools

#### perplexity_sonar
Fast answers with reliable search results.

**Parameters:**
- `request` (required): Your search query or question

**Features:**
- Lightweight, cost-effective search
- 128K context length
- Real-time web search with citations

**Example:**
```python
perplexity_sonar(request="What is the latest news in AI research?")
```

#### perplexity_sonar_pro
Advanced search with 2x more search results than standard Sonar.

**Parameters:**
- `request` (required): Your search query (can be complex)

**Features:**
- Advanced search model
- 200K context length
- 2x more search results for comprehensive analysis

**Example:**
```python
perplexity_sonar_pro(
    request="Analyze the competitive positioning of AI search engines"
)
```

#### perplexity_sonar_reasoning
Quick reasoning with Chain-of-Thought analysis.

**Parameters:**
- `request` (required): Your query requiring reasoning

**Features:**
- Reasoning model with CoT reasoning
- 128K context length
- Structured logical analysis with real-time search

**Example:**
```python
perplexity_sonar_reasoning(
    request="Analyze the impact of AI on job markets over the next decade"
)
```

#### perplexity_sonar_reasoning_pro
Advanced reasoning with enhanced multi-step analysis and 2x more results.

**Parameters:**
- `request` (required): Your query requiring advanced reasoning

**Features:**
- Advanced reasoning with enhanced CoT
- 128K context length
- 2x more search results for complex analysis

**Example:**
```python
perplexity_sonar_reasoning_pro(
    request="Analyze feasibility of fusion energy becoming mainstream by 2040"
)
```

#### perplexity_sonar_deep_research
Exhaustive research across hundreds of sources with expert-level insights.

**Parameters:**
- `request` (required): Your comprehensive research query
- `reasoning_effort` (optional): "low", "medium" (default), or "high"

**Features:**
- Deep research model
- Searches hundreds of sources
- 128K context length
- Expert-level analysis and detailed reports

**Example:**
```python
perplexity_sonar_deep_research(
    request="Analyze quantum computing industry through 2035",
    reasoning_effort="high"
)
```

## Typical Workflow

```python
# 1. Use Perplexity search - returns JSON directly
result = perplexity_sonar(request="Latest developments in quantum computing")

# The result is a JSON string containing:
# - choices[0].message.content: The AI response
# - citations: List of cited sources
# - search_results: Detailed search result metadata
# - usage: Token usage and cost information

# 2. Parse and use the JSON response
import json
response = json.loads(result)

# Extract information
content = response['choices'][0]['message']['content']
citations = response['citations']
search_results = response['search_results']
usage = response['usage']

print(f"Response: {content}")
print(f"Citations: {len(citations)}")
print(f"Search results: {len(search_results)}")
print(f"Tokens used: {usage['total_tokens']}")
```

## Setup

### Requirements
- Docker and Docker Compose
- Perplexity API key (get yours at https://www.perplexity.ai/settings/api)

### Environment Configuration

Create `.env.local` file:

```bash
# Perplexity API Credentials (required for Perplexity tools)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# MCP Configuration
MCP_NAME=perplexity
MCP_TOKENS=your_secure_token_here
MCP_REQUIRE_AUTH=false
MCP_ALLOW_URL_TOKENS=true
PORT=8011

# Optional: Sentry error tracking
# SENTRY_DSN=your_sentry_dsn
CONTAINER_NAME=mcp-perplexity-local
```

### Deployment

```bash
# Local development
./compose.local.sh

# Service runs on http://localhost:8011/perplexity/

# View logs
./logs.sh

# Stop service
docker compose -f docker-compose.local.yml down
```

### Claude Desktop Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8011/perplexity/"
      ]
    }
  }
}
```

**Health check endpoint:** `http://localhost:8011/health`

## Security Notes

- **API Key Management**: Store API keys securely in environment variables
- **Read-Only Tools**: All tools are read-only data fetching operations
- **Token Authentication**: Configure via MCP_REQUIRE_AUTH for production
- **Data Privacy**: No data is stored server-side; all responses are returned directly to the client

## Response Format

All Perplexity tools return JSON responses directly containing:
- **Content**: The AI-generated response text
- **Citations**: List of source URLs cited in the response
- **Search Results**: Detailed metadata about search results (title, URL, date, etc.)
- **Usage Stats**: Token counts and cost information
- **Model Info**: Model name and version used

This enables:
- Direct access to all response data
- Flexible client-side processing
- Easy integration with existing systems
- No server-side file management required

## Tool Documentation

Each tool includes comprehensive inline documentation with:
- Detailed parameter descriptions and valid ranges
- Return value schemas with data types
- Use cases and examples
- Best practices

Run tools without parameters to see full documentation.

## Development

### Project Structure

```
mcp-perplexity/
├── backend/
│   ├── main.py              # Main MCP server
│   ├── mcp_service.py       # Core service utilities
│   ├── mcp_resources.py     # Documentation resources
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile.local     # Docker build configuration
├── data/                    # CSV storage (git-ignored)
│   └── mcp-perplexity/     # Tool output data
├── docker-compose.local.yml # Docker compose configuration
├── compose.local.sh         # Build and start script
├── logs.sh                  # View container logs
├── mount.sh                 # Mount data directory (optional)
└── README.md               # This file
```

### Adding New Tools

1. Create tool implementation in `backend/` or a new module
2. Register tool in `backend/main.py`
3. Return JSON responses directly for API-based tools
4. Update documentation in `backend/mcp_resources.py`
5. Test thoroughly with various inputs

## Use Cases

- **Web Research**: AI-powered search with cited sources across 5 Perplexity models
- **Quick Facts**: Fast lookups with `perplexity_sonar` for definitions, news, summaries
- **Complex Analysis**: Deep research with `perplexity_sonar_pro` for comparative analysis
- **Reasoning Tasks**: Chain-of-Thought analysis with reasoning models for problem-solving
- **Exhaustive Research**: Academic-level research with `perplexity_sonar_deep_research`
- **Knowledge Management**: Save and retrieve tool usage notes
- **Content Discovery**: Find and analyze web content programmatically
- **Agent Integration**: Direct JSON responses for easy integration with AI agents and workflows

## License

MIT License - See LICENSE file for details.
