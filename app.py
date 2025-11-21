from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import main
import os

app = FastAPI(title="GitHub Neural Search")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class NLPQuery(BaseModel):
    query: str
    page: int = 1

class ManualFilters(BaseModel):
    language: Optional[str] = None
    stars_min: Optional[int] = None
    stars_max: Optional[int] = None
    topics: Optional[List[str]] = None
    license: Optional[str] = None
    good_first_issue: bool = False
    help_wanted: bool = False
    updated_after: Optional[str] = None
    sort: str = "stars"
    order: str = "desc"
    limit: int = 15
    page: int = 1

# API Endpoints
@app.post("/api/search/nlp")
async def search_nlp(request: NLPQuery):
    try:
        # Use the existing parser from main.py
        filters = main.parse_query(request.query)
        filters["page"] = request.page
        results = main.search_github(filters)
        
        if results is None:
            raise HTTPException(status_code=500, detail="GitHub API failed")
            
        return {
            "filters": filters,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/manual")
async def search_manual(filters: ManualFilters):
    try:
        # Construct filters dict expected by main.py
        query_filters = {
            "language": filters.language,
            "topics": filters.topics or [],
            "license": filters.license,
            "updated_after": filters.updated_after,
            "issues": {
                "good_first_issue": filters.good_first_issue,
                "help_wanted": filters.help_wanted
            },
            "sort": filters.sort,
            "order": filters.order,
            "limit": filters.limit,
            "page": filters.page,
            "include_forks": False,
            "archived": False
        }
        
        if filters.stars_min is not None or filters.stars_max is not None:
            query_filters["stars"] = {}
            if filters.stars_min is not None:
                query_filters["stars"]["min"] = filters.stars_min
            if filters.stars_max is not None:
                query_filters["stars"]["max"] = filters.stars_max
        
        results = main.search_github(query_filters)
        
        if results is None:
            raise HTTPException(status_code=500, detail="GitHub API failed")
            
        return {
            "filters": query_filters,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
