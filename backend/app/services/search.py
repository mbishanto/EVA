import logging

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class SearchService:
    def web_search(self, query, max_results=5):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return ""

            parts = []
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                parts.append(f"Title: {title}\n\nSnippet: {body}")

            return "\n\n".join(parts)

        except Exception as e:
            logger.error("Web search failed: %s", e)
            return ""


search_service = SearchService()
