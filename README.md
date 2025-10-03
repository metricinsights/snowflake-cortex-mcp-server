# Snowflake Intelligence MCP Server

## Installation
1. Clone this repository
```bash
git clone git@github.com:metricinsights/snowflake-cortex-mcp-server.git
```
2. copy [config.example.py](https://github.com/metricinsights/snowflake-cortex-mcp-server/blob/main/config.example.py) to config.py and fill in your Snowflake details.
3. Run the service via docker 
```bash
docker-compose up -d
```

## Usage Example
```python
import asyncio
import microcore as mc
from rich.pretty import pprint


async def main():
    mc.configure(LLM_API_TYPE=mc.ApiType.NONE)
    mcp = await mc.mcp.MCPServer("http://localhost:8009/mcp").connect()
    print("Available MCP Tools:")
    pprint(mcp.tools)

    def onprogress(progress, total, message):
        print(mc.ui.cyan(f"Progress: {progress}/{total} - {message}"))

    print("Asking MCP...")
    res = await mcp.call(
        "ask",
        agent="RETAIL_SALES",
        question="What is total sales?",
        progress_handler=onprogress,
        timeout=300,
    )
    print(mc.ui.blue(res))

asyncio.run(main())

```
