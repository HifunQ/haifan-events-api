from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import requests

app = FastAPI(title="嗨番事件库 API", version="1.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = "https://fgacscqjkksvnzbxtkbo.supabase.co"
SUPABASE_KEY = "sb_publishable_g7j2t6WhTScEve_VgwRDoA_4EV1qzwa"

class QueryResponse(BaseModel):
    success: bool
    data: Any
    query_time: str
    total_count: Optional[int] = None

def supabase_get(table: str, select: str = "*", limit: int = 100):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?select={select}&limit={limit}", headers=headers, timeout=10)
    return resp.json()

@app.get("/")
def root(): return {"name": "嗨番事件库 API", "version": "1.4.0"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/kpi")
def get_kpi():
    try:
        events = supabase_get("events", "event_id", 5000)
        issues = supabase_get("issues", "event_id", 5000)
        return QueryResponse(success=True, data={"total_events": len(events), "total_issues": len(issues)}, query_time=datetime.now().isoformat())
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/events")
def get_events(limit: int = 100):
    rows = supabase_get("events", "*", limit)
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
