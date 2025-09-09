import asyncio
import microcore as mc
from rich.pretty import pprint


async def main():
    mc.configure(LLM_API_TYPE=mc.ApiType.NONE)
    mcp = await mc.mcp.MCPServer('http://localhost:8009/mcp').connect()
    print("Available MCP Tools:")
    pprint(mcp.tools)
    def onprogress(progress, total, message):
        print(mc.ui.cyan(f"Progress: {progress}/{total} - {message}"))
    print('Asking MCP...')
    res = await mcp.call(
        'ask',
        agent='CUSTOMER_SUPPORT',
        question='show customer support cases by year as table and chart',
        progress_handler=onprogress,
        timeout=300
    )
    print(mc.ui.blue(res))

asyncio.run(main())
