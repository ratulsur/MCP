from __future__ import annotations

import asyncio
from typing import Optional, List, Dict, Any

import arxiv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("arxiv MCP")


def _find_papers_sync(query: str, max_results: int, categories: Optional[List[str]]) -> List[Dict[str, Any]]:
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    results = []
    for paper in search.results():
        # Normalize categories
        primary = getattr(paper, "primary_category", None)
        primary_str = getattr(primary, "term", None) if primary is not None else None
        if primary_str is None:
            primary_str = str(primary) if primary is not None else ""

        all_cats = set(getattr(paper, "categories", []) or [])
        all_cats.add(primary_str)

        if categories:
            # match if primary OR any category matches
            if not any(cat in all_cats for cat in categories):
                continue

        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "published": paper.published.isoformat() if paper.published else None,
            "summary": paper.summary,  # optionally truncate
            "url": paper.entry_id,
            "category": primary_str,
        })

    return results


@mcp.tool()
async def find_papers(
    query: str,
    max_results: int = 5,
    categories: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search arXiv papers.

    :param query: Search query (e.g. "transformer architecture")
    :param max_results: Number of papers to return
    :param categories: Optional arXiv categories (e.g. ["cs.AI", "cs.LG"])
    """
    return await asyncio.to_thread(_find_papers_sync, query, max_results, categories)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
