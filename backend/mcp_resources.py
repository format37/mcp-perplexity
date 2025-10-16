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

## Future Tools

The following tools will be implemented in future iterations:

- `perplexity_search` - AI-powered web search with cited sources
- `perplexity_research` - Deep research on specific topics
- Additional analysis and research tools

Stay tuned for updates!
"""
