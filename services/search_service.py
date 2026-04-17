from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def search_market_data(sector: str) -> str:
    """
    Searches the web for latest market data and news
    for the given sector in India.
    """
    queries = [
        f"{sector} sector India trade opportunities 2025",
        f"{sector} India export import market trends 2025",
        f"{sector} India business growth forecast",
    ]

    collected_data = []

    with DDGS() as ddgs:
        for query in queries:
            try:
                results = ddgs.text(query, max_results=4)
                for result in results:
                    collected_data.append(
                        f"Source: {result['title']}\n"
                        f"Info: {result['body']}\n"
                    )
                logger.info(f"Search successful for: {query}")
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue

    if not collected_data:
        return f"No live data found for {sector}. Using general knowledge."

    return "\n".join(collected_data)