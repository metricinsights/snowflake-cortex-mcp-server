from snowflake_mcp.config import Config

_defaults = Config(
    account="TTXXXXX.us-east-2.aws",
    database="SNOWFLAKE_INTELLIGENCE",
    schema="AGENTS",
    token="<TOKEN>",
)
agent_configs = {
    "CUSTOMER_SUPPORT": Config(agent="CUSTOMER_SUPPORT", defaults=_defaults),
    "INVENTORY": Config(agent="INVENTORY", defaults=_defaults),
    "RETAIL_SALES": Config(agent="RETAIL_SALES", defaults=_defaults),
    "*": Config(agent="*", defaults=_defaults),
}