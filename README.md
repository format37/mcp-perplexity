# Perplexity MCP Server

MCP server providing Perplexity AI-powered web search and research capabilities through the Model Context Protocol. Build intelligent agents that can search, analyze, and reason about web content.

## Architecture

**CSV-First Data Design**

All tools return structured CSV files instead of raw JSON responses, encouraging systematic data analysis workflows:

- **Output**: Every tool saves results to CSV files in the server's `data/mcp-perplexity/` folder
- **Analysis**: CSV files are analyzed using the `py_eval` tool with pandas/numpy pre-loaded
- **Pattern**: Fetch data → Receive CSV path → Analyze with Python → Make decisions
- **Benefits**: Promotes data-driven reasoning, enables complex multi-step analysis, supports historical tracking

**Modular Design**

Each tool is implemented with comprehensive parameter documentation, minimizing token usage and improving maintainability.

## Available Tools

### Basic Tools

#### py_eval
Execute Python code with pandas/numpy pre-loaded and access to CSV folder.

**Parameters:**
- `code` (required): Python code to execute
- `timeout_sec` (optional): Execution timeout in seconds (default: 5.0)

**Available Variables:**
- `pd`: pandas library
- `np`: numpy library
- `CSV_PATH`: path to `data/mcp-perplexity/` folder

**Example:**
```python
py_eval(code='''
import os
files = [f for f in os.listdir(CSV_PATH) if f.endswith('.csv')]
print(f"Found {len(files)} CSV files")
''')
```

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

### Future Tools

The following tools will be implemented in future iterations:

- `perplexity_search` - AI-powered web search with cited sources
- `perplexity_research` - Deep research on specific topics
- Additional analysis and research tools

## Typical Workflow

```python
# 1. Use Perplexity search (coming soon)
perplexity_search(query="Latest developments in quantum computing")
# Returns: "✓ Data saved to CSV\nFile: search_results_abc123.csv..."

# 2. Analyze the results with Python
py_eval(code="""
import pandas as pd

# Load search results
df = pd.read_csv('data/mcp-perplexity/search_results_abc123.csv')

print(f"=== SEARCH RESULTS ANALYSIS ===")
print(f"Total results: {len(df)}")
print(f"\nTop 5 sources:")
print(df[['title', 'url']].head())
""")

# 3. Make data-driven decisions based on analysis
```

## Setup

### Requirements
- Docker and Docker Compose
- Perplexity API key (if implementing search tools)

### Environment Configuration

Create `.env.local` file:

```bash
# Perplexity API Credentials (for future tools)
# PERPLEXITY_API_KEY=your_perplexity_api_key_here

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
- **Data Privacy**: All CSV files are stored locally on the server

## CSV Data Persistence

All CSV files are stored in `data/mcp-perplexity/` with unique identifiers, enabling:
- Historical research data tracking
- Performance analysis over time
- Systematic research workflows
- Reproducible analysis and audit trails
- Multi-session data accumulation

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
3. Use `format_csv_response()` for standardized output
4. Update documentation in `backend/mcp_resources.py`
5. Test with `py_eval` for data analysis workflows

## Use Cases

- **Web Research**: AI-powered search with cited sources (coming soon)
- **Data Analysis**: Analyze search results with pandas/numpy
- **Knowledge Management**: Save and retrieve tool usage notes
- **Research Workflows**: Systematic data collection and analysis
- **Content Discovery**: Find and analyze web content programmatically

## License

MIT License - See LICENSE file for details.
