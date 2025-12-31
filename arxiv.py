from mcp.server.fastmcp import FastMCP
import arxiv
mcp = FastMCP("arxiv MCP")

@mcp.tool()
async def find_papers(
    query: str,
    max_results: int = 5,
    categories: list[str] | None = None,
) -> list[dict]:
    """
    Search arXiv papers.

    :param query: Search query (e.g. "transformer architecture")
    :param max_results: Number of papers to return
    :param categories: Optional arXiv categories (e.g. ["cs.AI", "cs.LG"])
    """

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    results = []
    for paper in search.results():
        if categories and paper.primary_category not in categories:
            continue

        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "published": paper.published.isoformat(),
            "summary": paper.summary,
            "url": paper.entry_id,
            "category": paper.primary_category,
        })

    return results


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
