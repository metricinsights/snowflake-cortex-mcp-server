from dataclasses import dataclass
import requests

from .config import Config


def as_user_message(question: str) -> dict:
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": question}
        ]
    }


@dataclass
class Agent:
    config: Config

    def ask(self, question: str) -> str:
        cfg = self.config
        api_domain = f"https://{cfg.account}.snowflakecomputing.com"
        url = f"{api_domain}/api/v2/databases/{cfg.database}/schemas/{cfg.schema}/agents/{cfg.agent}:run"
        headers = {
            "Authorization": f"Bearer {cfg.token}",
            "Content-Type": "application/json"
        }
        request_body = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": question}]}
            ],
        }
        response = requests.post(url, headers=headers, json=request_body)
        return response.text
