"""Ollama tool schema definitions and call handlers."""

from . import web_search as _ws

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current information, news, documentation, "
                "or anything that may not be in the model's training data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_model",
            "description": "Switch the active Ollama model when the user asks to change or use a different model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Ollama model name, e.g. llama3.2, mistral, gemma3",
                    }
                },
                "required": ["model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_config",
            "description": (
                "Save a configuration value. Use this when the user wants to set "
                "an API key, change the Ollama host URL, or store any setting. "
                "Known keys: ollama_api_key, ollama_host."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Config key, e.g. ollama_api_key or ollama_host",
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to store",
                    },
                },
                "required": ["key", "value"],
            },
        },
    },
]


def dispatch(name: str, args: dict, config) -> str:
    if name == "web_search":
        return _ws.search(args["query"], config=config)
    if name == "switch_model":
        config.model = args["model"]
        return f"Model switched to {args['model']}."
    if name == "set_config":
        config.set(args["key"], args["value"])
        return f"Saved {args['key']}."
    return f"Unknown tool: {name}"
