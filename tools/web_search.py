"""Web search via DuckDuckGo — no API key required."""


def search(query: str, max_results: int = 5) -> str:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "Missing dependency — run:  pip install duckduckgo-search"

    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"**{r['title']}**\n{r['href']}\n{r['body']}")
        return "\n\n---\n\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {e}"
