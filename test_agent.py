import json
import textwrap

from microcore import ui
from rich.pretty import pprint

from config import agent_configs
from snowflake_mcp.async_agent import Agent
from snowflake_mcp.bootstrap import setup_logging


setup_logging()
a = Agent(config=agent_configs["CUSTOMER_SUPPORT"])
gen = a.ask("show customer support cases by year as table and chart")
for i in gen:
    if i.event_type == "response.text.delta":
        res = i.data['text']
        print(ui.blue(res), end='', flush=True)
    elif i.event_type == "response.tool_result.status":
        print(ui.yellow(f"[Status: {i.data['status']}]: {i.data.get('message','')}"))
    elif i.event_type == "response.status":
        print(ui.yellow(f"[Status: {i.data['status']}]: {i.data.get('message','')}"))
    elif i.event_type == "response.thinking.delta":
        res = i.data['text']
        print(ui.gray(res), end='', flush=True)
    elif i.event_type == "response.tool_use":
        print(ui.magenta(f"\n<{i.event_type}: {i.data['type']}"))
        print(ui.gray(textwrap.indent(json.dumps(i.data['input']), f'|  ')))
        print(ui.magenta(f">"))
    elif i.event_type in ["response.thinking","execution_trace", "response", "done", "response.text"]:
        print(ui.magenta(f"<{i.event_type}>"))
    else:
        print('\n', end='')
        pprint(i)