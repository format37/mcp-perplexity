# Perplexity MCP Server

MCP server providing Perplexity AI-powered web search and research capabilities through the Model Context Protocol. Build intelligent agents that can search, analyze, and reason about web content.

## Architecture

**Data-First Design**

All tools save results to structured files in the server's `data/mcp-perplexity/` folder:

- **CSV for Tabular Data**: Basic tools save tabular data as CSV files
- **JSON for Hierarchical Data**: Perplexity tools save rich, nested responses as JSON files
- **Analysis**: Use `py_eval` tool with pandas/numpy/json for data analysis
- **Pattern**: Fetch data → Receive file path → Analyze with Python → Make decisions
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
# 1. Use Perplexity search
perplexity_sonar(request="Latest developments in quantum computing")
# Returns: "✓ Perplexity response saved to JSON\nFile: sonar_20251016_abc123.json..."

# 2. Analyze the results with Python
py_eval(code="""
import json
import pandas as pd

# Load Perplexity response
with open('data/mcp-perplexity/sonar_20251016_abc123.json', 'r') as f:
    response = json.load(f)

# Extract key information
citations = response['citations']
search_results = response['search_results']
content = response['choices'][0]['message']['content']

print(f"=== PERPLEXITY SEARCH ANALYSIS ===")
print(f"Total citations: {len(citations)}")
print(f"Search results: {len(search_results)}")
print(f"\\nFirst 3 citations:")
for c in citations[:3]:
    print(f"  - {c}")

# Convert search results to DataFrame for analysis
df = pd.DataFrame(search_results)
print(f"\\nTop 5 sources:")
print(df[['title', 'url', 'date']].head())
""")

# 3. Make data-driven decisions based on analysis
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
- **Data Privacy**: All CSV files are stored locally on the server

## Data Persistence

All data files (CSV and JSON) are stored in `data/mcp-perplexity/` with unique identifiers, enabling:
- Historical research data tracking
- Performance analysis over time
- Systematic research workflows
- Reproducible analysis and audit trails
- Multi-session data accumulation
- JSON for Perplexity responses preserves rich metadata (citations, search results, usage stats)

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

- **Web Research**: AI-powered search with cited sources across 5 Perplexity models
- **Quick Facts**: Fast lookups with `perplexity_sonar` for definitions, news, summaries
- **Complex Analysis**: Deep research with `perplexity_sonar_pro` for comparative analysis
- **Reasoning Tasks**: Chain-of-Thought analysis with reasoning models for problem-solving
- **Exhaustive Research**: Academic-level research with `perplexity_sonar_deep_research`
- **Data Analysis**: Analyze search results and responses with pandas/numpy/json
- **Knowledge Management**: Save and retrieve tool usage notes
- **Research Workflows**: Systematic data collection and analysis
- **Content Discovery**: Find and analyze web content programmatically

## License

MIT License - See LICENSE file for details.
