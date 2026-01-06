import os
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import arxiv

load_dotenv()

app = FastAPI(title="Deploy Test API", version="1.0.0")

# Allow frontend (local or hosted) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MathRequest(BaseModel):
    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class ArxivRequest(BaseModel):
    query: str = Field(..., description='Search query, e.g. "transformer architecture"')
    max_results: int = Field(5, ge=1, le=25)
    categories: Optional[List[str]] = None


@app.get("/health")
def health():
    return {"ok": True, "service": "deploy-test-api"}


@app.post("/api/add")
def add(req: MathRequest):
    return {"result": req.a + req.b}


@app.post("/api/multiply")
def multiply(req: MathRequest):
    return {"result": req.a * req.b}


@app.post("/api/arxiv")
def arxiv_search(req: ArxivRequest):
    search = arxiv.Search(
        query=req.query,
        max_results=req.max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    results = []
    for paper in search.results():
        primary = getattr(paper, "primary_category", "")
        primary_str = getattr(primary, "term", None) or str(primary)

        all_cats = set(getattr(paper, "categories", []) or [])
        all_cats.add(primary_str)

        if req.categories:
            if not any(cat in all_cats for cat in req.categories):
                continue

        results.append(
            {
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "published": paper.published.isoformat() if paper.published else None,
                "summary": paper.summary[:800] + ("…" if len(paper.summary) > 800 else ""),
                "url": paper.entry_id,
                "category": primary_str,
            }
        )

    return {"count": len(results), "results": results}
