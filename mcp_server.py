import json
import logging
import os
import textwrap
from dataclasses import replace

from snowflake_mcp.bootstrap import setup_logging
from snowflake_mcp.async_agent import Agent
from config import agent_configs

from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers
from microcore import ui

setup_logging()

mcp = FastMCP(
    name="Snowflake MCP",
    debug=True,
    host="0.0.0.0",
    port=int(os.getenv("MCP_PORT", 8009)),
)


@mcp.tool(description="Ask Snowflake agent")
async def ask(agent: str, question: str, ctx: Context) -> str:
    if agent not in agent_configs:
        raise ValueError(f"Agent '{agent}' is not available.")

    request_headers = get_http_headers()

    agent_config = agent_configs[agent]
    if token := request_headers.get("token"):
        agent_config = replace(agent_config, token=token)
    result = Agent(config=agent_config).ask(question)
    out = ""
    for i in result:
        if i.event_type == "response.text.delta":
            res = i.data["text"]
            out += res
            print(ui.blue(res), end="", flush=True)
        elif i.event_type in ("response.tool_result.status", "response.status"):
            await ctx.report_progress(
                progress=1, total=3, message=i.data.get("message", i.data["status"])
            )
            logging.info(f"[Status: {i.data['status']}]: {i.data.get('message', '')}")
        elif i.event_type == "response.thinking.delta":
            print(ui.gray(i.data["text"]), end="", flush=True)
        elif i.event_type == "response.tool_use":
            print(ui.magenta(f"\n<{i.event_type}: {i.data['type']}"))
            print(ui.gray(textwrap.indent(json.dumps(i.data["input"]), "|  ")))
            print(ui.magenta(f">"))
        elif i.event_type in [
            "response.thinking",
            "execution_trace",
            "response",
            "done",
            "response.text",
        ]:
            print(ui.magenta(f"<{i.event_type}>"))
        elif i.event_type == "response.table":
            out_table = dict(data_type="table", columns=[], data=[])
            if title := i.data.get("title"):
                out += f"\n### {title}\n"  # By default, use <H3> for table headers
            columns = (
                i.data.get("result_set", {})
                .get("resultSetMetaData", {})
                .get("rowType", [])
            )
            for column in columns:
                out_table["columns"].append(
                    {
                        "key": column["name"],
                        "label": column["name"]
                        .replace("_", " ")
                        .replace("-", " ")
                        .title(),
                    }
                )
            rows = i.data.get("result_set", {}).get("data", [])
            for row in rows:
                new_row = {}
                for i, column in enumerate(out_table["columns"]):
                    if i < len(row):  # Ensure the index exists in the row
                        new_row[column["key"]] = row[i]
                out_table["data"].append(new_row)
            out += f"\n%BEGIN_JSON%\n{json.dumps(out_table, indent=2)}\n%END_JSON%\n"
        elif i.event_type == "response.chart":
            json_serialized_data = json.dumps(
                dict(
                    data_type="chart",
                    data=(
                        json.loads(i.data["chart_spec"])
                        if isinstance(i.data["chart_spec"], str)
                        else i.data["chart_spec"]
                    ),
                ),
                indent=2,
            )
            out += f"\n%BEGIN_JSON%\n{json_serialized_data}\n%END_JSON%\n"
    return out


mcp.run(transport=os.getenv("MCP_TRANSPORT", "streamable-http"))
