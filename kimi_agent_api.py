from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import os, httpx

app = FastAPI(title="嗨番事件库 API", version="1.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = "https://fgacscqjkksvnzbxtkbo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnYWNzY3Fqa2tzdm56Ynh0a2JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI3NTY0MDAsImV4cCI6MjAzODMzMjQwMH0.demo_key"

class QueryResponse(BaseModel):
    success: bool
    data: Any
    query_time: str
    total_count: Optional[int] = None

async def supabase_query(table: str, select: str = "*", limit: int = 100):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={"select": select, "limit": limit}
        )
        return resp.json()

@app.get("/")
def root(): return {"name": "嗨番事件库 API", "version": "1.3.0"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/kpi")
async def get_kpi():
    import asyncio
    events = await supabase_query("events", "event_id", 1000)
    issues = await supabase_query("issues", "event_id", 1000)
    return QueryResponse(success=True, data={"total_events": len(events), "total_issues": len(issues)}, query_time=datetime.now().isoformat())

@app.get("/api/v1/events")
async def get_events(limit: int = 100):
    rows = await supabase_query("events", "*", limit)
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
