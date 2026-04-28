"""Web search via ollama.web_search — requires an Ollama API key."""

from ollama import Client

_NEEDS_KEY = (
    "MISSING_OLLAMA_API_KEY: No Ollama API key is configured. "
    "Ask the user for their Ollama API key and save it with set_config key=ollama_api_key."
)


def search(query: str, config=None, max_results: int = 5) -> str:
    api_key = config.ollama_api_key if config else None
    if not api_key:
        return _NEEDS_KEY

    try:
        client = Client(host=config.ollama_host, headers={"Authorization": f"Bearer {api_key}"})
        response = client.web_search(query, max_results=max_results)
        if not response.results:
            return "No results found."
        parts = [
            f"**{r.title}**\n{r.url}\n{r.content or ''}"
            for r in response.results
        ]
        return "\n\n---\n\n".join(parts)
    except Exception as e:
        return f"Search error: {e}"
