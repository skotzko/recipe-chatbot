import json
import datetime
from pathlib import Path
from typing import List, Dict


def save_trace(request_messages: List[Dict[str, str]], response_messages: List[Dict[str, str]]) -> Path:
    """Save conversation trace to annotation/traces directory.

    Parameters
    ----------
    request_messages:
        The request messages (conversation history before the agent response).
    response_messages:
        The response messages (full conversation history including the agent response).

    Returns
    -------
    Path
        Path to the saved trace file.
    """
    traces_dir = Path(__file__).parent.parent / "annotation" / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    trace_path = traces_dir / f"trace_{ts}.json"

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump({
            "request": {"messages": request_messages},
            "response": {"messages": response_messages}
        }, f, indent=2, ensure_ascii=False)

    return trace_path
