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

## Authentication

The server supports authentication tokens in two ways:

### 1. Via Request Headers
You can pass the authentication token directly in your request headers. This method takes **priority** over the config file token.

```python
headers = {
    "token": "Bearer YOUR_TOKEN_HERE"
}
```

When using request header authentication, you don't need to set the token in `config.py`.

### 2. Via Configuration File
Alternatively, you can set the authentication token in your `config.py` file. This is useful for development or when the token doesn't change frequently.

**Note:** If you provide both a token in the request headers and in `config.py`, the **request header token will be used**.

## Usage Example
```python
import asyncio
import microcore as mc
from rich.pretty import pprint


async def main():
    mc.configure(LLM_API_TYPE=mc.ApiType.NONE)
    
    # Optional: Pass authentication token via headers
    headers = {
        "token": "YOUR_TOKEN_HERE"
    }
    
    mcp = await mc.mcp.MCPServer(
        "http://localhost:8009/mcp",
        auth=headers,
    ).connect()
    
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
