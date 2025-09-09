from dataclasses import dataclass
import requests
import json
from typing import Generator, Dict, Any, Optional

from .config import Config

def as_user_message(question: str) -> dict:
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": question}
        ]
    }


@dataclass
class StreamEvent:
    """Represents a single event from the SSE stream"""
    event_type: str
    data: Dict[str, Any]
    # raw_data: str


@dataclass
class Agent:
    config: Config

    def ask(self, question: str) -> Generator[StreamEvent, None, None]:
        """
        Ask a question and yield structured events from the SSE response stream.

        Args:
            question: The question to ask the agent

        Yields:
            StreamEvent: Parsed events from the server-sent events stream
        """
        cfg = self.config
        api_domain = f"https://{cfg.account}.snowflakecomputing.com"
        url = f"{api_domain}/api/v2/databases/{cfg.database}/schemas/{cfg.schema}/agents/{cfg.agent}:run"
        headers = {
            "Authorization": f"Bearer {cfg.token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        request_body = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": question}]}
            ],
        }

        # Use streaming request to handle SSE
        with requests.post(url, headers=headers, json=request_body, stream=True) as response:
            response.raise_for_status()

            for event in self._parse_sse_stream(response.iter_lines(decode_unicode=True)):
                yield event

    def _parse_sse_stream(self, lines: Generator[str, None, None]) -> Generator[StreamEvent, None, None]:
        """
        Parse Server-Sent Events stream into structured events.

        Args:
            lines: Iterator of lines from the SSE response

        Yields:
            StreamEvent: Parsed events with structured data
        """
        event_type = None
        event_data = None

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # End of event block
            if line == '':
                if event_type and event_data:
                    yield self._create_stream_event(event_type, event_data)
                    event_type = None
                    event_data = None
                continue

            # Parse event field
            if line.startswith('event: '):
                event_type = line[7:]
                continue

            # Parse data field
            if line.startswith('data: '):
                event_data = line[6:]

                # Yield event immediately for each data line
                if event_type and event_data:
                    yield self._create_stream_event(event_type, event_data)
                continue

        # Handle final event if stream doesn't end with empty line
        if event_type and event_data:
            yield self._create_stream_event(event_type, event_data)

    def _create_stream_event(self, event_type: str, raw_data: str) -> StreamEvent:
        """
        Create a StreamEvent with parsed data.

        Args:
            event_type: The SSE event type
            raw_data: The raw data string from the SSE event

        Returns:
            StreamEvent: Structured event with parsed data
        """
        parsed_data = {}

        # Try to parse JSON data
        if raw_data:
            try:
                parsed_data = json.loads(raw_data)
            except json.JSONDecodeError:
                # If not JSON, store as plain text
                parsed_data = raw_data

        return StreamEvent(
            event_type=event_type,
            data=parsed_data,
        )

    def get_final_response(self, question: str) -> Optional[str]:
        """
        Get the final text response from the agent, filtering out intermediate events.

        Args:
            question: The question to ask the agent

        Returns:
            str: The final response text, or None if no response found
        """
        final_text = ""

        for event in self.answer_async(question):
            # Collect text deltas for the final response
            if event.event_type == "response.text.delta" and "text" in event.data:
                final_text += event.data["text"]
            # Or get complete text if available
            elif event.event_type == "response.text" and "text" in event.data:
                final_text = event.data["text"]

        return final_text.strip() if final_text else None

    def get_tool_results(self, question: str) -> Generator[Dict[str, Any], None, None]:
        """
        Get tool execution results from the agent response.

        Args:
            question: The question to ask the agent

        Yields:
            dict: Tool result data
        """
        for event in self.answer_async(question):
            if event.event_type == "response.tool_result" and event.data:
                yield event.data

    def get_status_updates(self, question: str) -> Generator[str, None, None]:
        """
        Get status updates during agent processing.

        Args:
            question: The question to ask the agent

        Yields:
            str: Status message
        """
        for event in self.answer_async(question):
            if event.event_type == "response.status" and "message" in event.data:
                yield event.data["message"]