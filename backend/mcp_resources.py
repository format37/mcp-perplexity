import logging

logger = logging.getLogger(__name__)


def register_mcp_resources(local_mcp_instance, safe_name):
    """Register MCP resources (documentation, etc.)"""

    @local_mcp_instance.resource(
        f"{safe_name}://documentation",
        name="Perplexity MCP Documentation",
        description="Documentation for Perplexity web search and research MCP server",
        mime_type="text/markdown"
    )
    def get_documentation_resource() -> str:
        """Expose Perplexity MCP documentation as an MCP resource."""
        return """# Perplexity MCP Documentation

## Overview

Perplexity MCP server provides AI-powered web search and research capabilities through the Model Context Protocol. All tools follow a CSV-first architecture for systematic data analysis.

## Available Tools

### py_eval
Execute Python code with pandas/numpy pre-loaded and access to CSV folder.

**Parameters:**
- `code` (required): Python code to execute
- `timeout_sec` (optional): Execution timeout in seconds (default: 5.0)

**Available Variables:**
- `pd`: pandas library (version 2.0.0+)
- `np`: numpy library (version 1.24.0+)
- `CSV_PATH`: string path to `data/mcp-perplexity/` folder

**Important Notes:**
- Each py_eval call starts fresh - variables do NOT persist between calls
- You must reload CSV files in each py_eval call that needs them
- Standard library modules are available for import

**Example Usage:**
```python
py_eval(code=\"\"\"
import os
files = [f for f in os.listdir(CSV_PATH) if f.endswith('.csv')]
print(f"Found {len(files)} CSV files")
for f in files[:5]:
    print(f"  - {f}")
\"\"\")
```

### save_tool_notes
Save usage notes and lessons learned about any MCP tool.

**Parameters:**
- `tool_name` (required): Name of the tool to document
- `markdown_notes` (required): Markdown-formatted notes about tool usage

**Returns:** Confirmation message with file path

**Use Cases:**
- Document parameter issues or gotchas discovered
- Record successful usage patterns
- Create troubleshooting guides for common issues
- Build knowledge base of tool usage patterns

**Example Usage:**
```python
save_tool_notes(
    tool_name="perplexity_search",
    markdown_notes="**Best Practice:** Keep queries specific and focused for optimal results."
)
```

### read_tool_notes
Read all historical usage notes for a specific MCP tool.

**Parameters:**
- `tool_name` (required): Name of the tool to read notes for

**Returns:** Full markdown content of all historical notes

**Use Cases:**
- Review known issues before calling complex tools
- Learn from past successful usage patterns
- Troubleshoot errors by checking historical solutions

**Example Usage:**
```python
read_tool_notes(tool_name="perplexity_search")
```

---

## CSV-First Architecture

**Design Philosophy:**

All tools save results to CSV files instead of returning raw responses, promoting systematic data analysis:

- **Output**: Tools save results to `data/mcp-perplexity/` folder
- **Analysis**: Use `py_eval` tool to analyze CSV files with pandas/numpy
- **Pattern**: Fetch data → Receive CSV path → Analyze with Python → Make decisions
- **Benefits**: Data-driven reasoning, complex multi-step analysis, historical tracking

**CSV File Structure:**

All CSV responses include:
- File path and name
- Row count and file size
- JSON schema with inferred data types
- Sample data (first row)
- Python code snippet to load the file

---

## Python Analysis Examples

### 1. Discover Available CSV Files

```python
py_eval(code=\"\"\"
import os

# List all CSV files
files = [f for f in os.listdir(CSV_PATH) if f.endswith('.csv')]
print(f"=== AVAILABLE CSV FILES ({len(files)}) ===")

# Group by pattern
for f in sorted(files):
    size = os.path.getsize(f"{CSV_PATH}/{f}")
    size_kb = size / 1024
    print(f"  {f} ({size_kb:.1f} KB)")
\"\"\")
```

### 2. Load and Analyze CSV Data

```python
py_eval(code=\"\"\"
import pandas as pd
import os

# Load the most recent CSV file
files = sorted([f for f in os.listdir(CSV_PATH) if f.endswith('.csv')])
if files:
    latest_file = files[-1]
    df = pd.read_csv(f"{CSV_PATH}/{latest_file}")

    print(f"=== ANALYSIS: {latest_file} ===")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\\nFirst 3 rows:")
    print(df.head(3))
    print(f"\\nData types:")
    print(df.dtypes)
else:
    print("No CSV files found")
\"\"\")
```

### 3. Error Handling and Robust Loading

```python
py_eval(code=\"\"\"
import pandas as pd
import os

def load_csv_safe(pattern):
    '''Load CSV file with error handling'''
    try:
        files = [f for f in os.listdir(CSV_PATH) if pattern in f and f.endswith('.csv')]
        if not files:
            print(f"No files found matching: {pattern}")
            return None

        latest = sorted(files)[-1]
        df = pd.read_csv(f"{CSV_PATH}/{latest}")
        print(f"✓ Loaded {latest}: {df.shape}")
        return df
    except Exception as e:
        print(f"✗ Error loading {pattern}: {e}")
        return None

# Use robust loading
df = load_csv_safe("search_results")
if df is not None:
    print("\\nData summary:")
    print(df.describe())
\"\"\")
```

---

## Best Practices

1. **Always reload data** - Start each py_eval with file discovery and loading
2. **Use error handling** - Check if files exist before loading
3. **Save intermediate results** - Use temporary CSV files for complex analysis
4. **Keep analysis focused** - Each py_eval call should accomplish one goal
5. **Print progress** - Use print statements to show what your code is doing
6. **Document learnings** - Use save_tool_notes to record insights

---

## Perplexity Search & Research Tools

### perplexity_sonar
Fast answers with reliable search results.

**Parameters:**
- `request` (required): Your search query or question

**Model Features:**
- Lightweight, cost-effective search
- 128K context length
- Optimized for speed and cost
- Real-time web search with citations

**Use Cases:**
- Quick facts and definitions
- Summarizing content
- News, sports, health, finance updates

**Example:**
```python
perplexity_sonar(request="What is the latest news in AI research?")
```

### perplexity_sonar_pro
Advanced search with enhanced results (2x more than standard Sonar).

**Parameters:**
- `request` (required): Your search query (can be complex)

**Model Features:**
- Advanced search model
- 200K context length
- 2x more search results than Sonar
- Enhanced information retrieval

**Use Cases:**
- Complex research questions
- Comparative analysis across sources
- Information synthesis and reporting

**Example:**
```python
perplexity_sonar_pro(
    request="Analyze the competitive positioning of AI search engines"
)
```

### perplexity_sonar_reasoning
Quick reasoning with Chain-of-Thought analysis.

**Parameters:**
- `request` (required): Your query requiring reasoning

**Model Features:**
- Reasoning model with CoT reasoning
- 128K context length
- Structured analysis with real-time search
- Shows reasoning process in <think> tags

**Use Cases:**
- Multi-step problem solving
- Logical analysis and reasoning
- Strategic planning

**Example:**
```python
perplexity_sonar_reasoning(
    request="Analyze the impact of AI on job markets over the next decade"
)
```

### perplexity_sonar_reasoning_pro
Advanced reasoning with enhanced multi-step analysis (2x more results).

**Parameters:**
- `request` (required): Your query requiring advanced reasoning

**Model Features:**
- Advanced reasoning with enhanced CoT
- 128K context length
- 2x more search results than Sonar Reasoning
- Complex multi-step analysis

**Use Cases:**
- Complex multi-step reasoning
- Advanced research with deep analysis
- Strategic decision making

**Example:**
```python
perplexity_sonar_reasoning_pro(
    request="Analyze feasibility of fusion energy becoming mainstream by 2040"
)
```

### perplexity_sonar_deep_research
Exhaustive research across hundreds of sources with expert-level insights.

**Parameters:**
- `request` (required): Your comprehensive research query
- `reasoning_effort` (optional): "low", "medium" (default), or "high"
  - "low": Faster answers, reduced tokens
  - "medium": Balanced approach
  - "high": Deeper responses, more thorough

**Model Features:**
- Deep research model
- Searches hundreds of sources
- 128K context length
- Expert-level analysis and detailed reports

**Use Cases:**
- Academic research and reports
- Market analysis and competitive intelligence
- Due diligence and investigative research

**Example:**
```python
perplexity_sonar_deep_research(
    request="Conduct comprehensive analysis of quantum computing industry through 2035",
    reasoning_effort="high"
)
```

---

## JSON-First Architecture for Perplexity Tools

**Why JSON instead of CSV?**

Perplexity responses contain rich, hierarchical data that's better preserved in JSON:

- **Nested structure**: Citations, search results, usage stats
- **Rich metadata**: Dates, URLs, snippets, titles
- **Analysis-friendly**: Easy to parse with Python's json module

**JSON Response Structure:**

All Perplexity tools save responses with:
- File path to saved JSON
- Citations list (source URLs)
- Search results preview (titles, URLs, snippets)
- Usage stats (tokens, costs)
- Response content preview
- Python code snippet to load

---

## Analyzing Perplexity JSON Responses

### 1. Load and Explore JSON Response

```python
py_eval(code='''
import json
import os

# Find latest Perplexity response
files = [f for f in os.listdir(CSV_PATH) if f.startswith('sonar') and f.endswith('.json')]
if files:
    latest = sorted(files)[-1]

    with open(f"{CSV_PATH}/{latest}", 'r') as f:
        response = json.load(f)

    print(f"=== ANALYSIS: {latest} ===")
    print(f"Model: {response['model']}")
    print(f"Citations: {len(response['citations'])}")
    print(f"Search results: {len(response['search_results'])}")
    print(f"\\\\nFirst 3 citations:")
    for c in response['citations'][:3]:
        print(f"  - {c}")
else:
    print("No Perplexity responses found")
''')
```

### 2. Extract and Analyze Search Results

```python
py_eval(code='''
import json
import pandas as pd

# Load response and convert search results to DataFrame
files = [f for f in os.listdir(CSV_PATH) if f.startswith('sonar') and f.endswith('.json')]
latest = sorted(files)[-1]

with open(f"{CSV_PATH}/{latest}", 'r') as f:
    response = json.load(f)

# Convert search results to DataFrame for analysis
search_results = response['search_results']
df = pd.DataFrame(search_results)

print(f"=== SEARCH RESULTS ANALYSIS ===")
print(f"Total results: {len(df)}")
print(f"\\\\nColumns: {list(df.columns)}")
print(f"\\\\nTop 5 sources:")
print(df[['title', 'url', 'date']].head())
print(f"\\\\nDate range: {df['date'].min()} to {df['date'].max()}")
''')
```

### 3. Extract Content and Save to Text

```python
py_eval(code='''
import json
import os

# Load response and extract main content
files = [f for f in os.listdir(CSV_PATH) if f.startswith('sonar') and f.endswith('.json')]
latest = sorted(files)[-1]

with open(f"{CSV_PATH}/{latest}", 'r') as f:
    response = json.load(f)

# Extract the response content
content = response['choices'][0]['message']['content']

# Save to text file for easier reading
text_filename = latest.replace('.json', '.txt')
with open(f"{CSV_PATH}/{text_filename}", 'w') as f:
    f.write(content)

print(f"✓ Content extracted to: {text_filename}")
print(f"Content length: {len(content)} characters")
print(f"\\\\nFirst 500 characters:")
print(content[:500])
''')
```

### 4. Compare Multiple Perplexity Responses

```python
py_eval(code='''
import json
import os

# Load all Perplexity responses
files = [f for f in os.listdir(CSV_PATH) if f.endswith('.json') and f.startswith('sonar')]

print(f"=== COMPARING {len(files)} PERPLEXITY RESPONSES ===\\\\n")

for file in sorted(files)[-5:]:  # Last 5 responses
    with open(f"{CSV_PATH}/{file}", 'r') as f:
        response = json.load(f)

    model = response['model']
    usage = response['usage']
    citations = len(response['citations'])
    cost = usage.get('cost', {}).get('total_cost', 0)

    print(f"{file}:")
    print(f"  Model: {model}")
    print(f"  Citations: {citations}")
    print(f"  Tokens: {usage['total_tokens']}")
    print(f"  Cost: ${cost:.4f}")
    print()
''')
```

---

## Best Practices

1. **Choose the right model**:
   - Use `sonar` for quick facts and simple queries
   - Use `sonar-pro` for complex analysis needing more sources
   - Use `sonar-reasoning` for problems requiring logical analysis
   - Use `sonar-reasoning-pro` for complex multi-step reasoning
   - Use `sonar-deep-research` for exhaustive research reports

2. **Analyzing responses**:
   - JSON responses are saved to `data/mcp-perplexity/`
   - Use `py_eval` with Python's `json` module to analyze
   - Extract search results to pandas DataFrame for analysis
   - Save extracted content to .txt files for readability

3. **Cost optimization**:
   - Start with `sonar` for simple queries (lowest cost)
   - Use `reasoning_effort="low"` for deep research when appropriate
   - Check usage stats in responses to monitor costs

4. **Document learnings**:
   - Use `save_tool_notes` to record successful query patterns
   - Note which models work best for specific use cases
"""
