from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import httpx

app = FastAPI(title="嗨番事件库 API", version="1.3.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = "https://fgacscqjkksvnzbxtkbo.supabase.co"
SUPABASE_KEY = "sb_publishable_g7j2t6WhTScEve_VgwRDoA_4EV1qzwa"

class QueryResponse(BaseModel):
    success: bool
    data: Any
    query_time: str
    total_count: Optional[int] = None

async def supabase_get(table: str, select: str = "*", limit: int = 100):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={"select": select, "limit": limit}
        )
        return resp.json()

@app.get("/")
def root(): return {"name": "嗨番事件库 API", "version": "1.3.1"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/kpi")
async def get_kpi():
    events = await supabase_get("events", "event_id", 5000)
    issues = await supabase_get("issues", "event_id", 5000)
    data = {"total_events": len(events), "total_issues": len(issues)}
    return QueryResponse(success=True, data=data, query_time=datetime.now().isoformat())

@app.get("/api/v1/events")
async def get_events(limit: int = 100):
    rows = await supabase_get("events", "*", limit)
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
