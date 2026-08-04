from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import os

app = FastAPI(title="嗨番事件库 API", version="1.2.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryResponse(BaseModel):
    success: bool
    data: Any
    query_time: str
    total_count: Optional[int] = None

def get_db_conn():
    db_url = os.getenv('DATABASE_URL', '')
    import psycopg2, urllib.parse
    p = urllib.parse.urlparse(db_url)
    return psycopg2.connect(
        host=p.hostname, port=p.port or 5432,
        user=p.username, password=p.password,
        dbname=p.path.lstrip('/'), sslmode='require'
    )

@app.get("/")
def root():
    return {"name": "嗨番事件库 API", "version": "1.2.2", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/kpi")
def get_kpi():
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM events")
        total_events = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM issues")
        total_issues = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events WHERE is_abnormal=1")
        abnormal = cur.fetchone()[0]
        data = {
            "total_events": total_events,
            "total_issues": total_issues,
            "abnormal_events": abnormal,
            "abnormal_rate": round(abnormal / max(total_events, 1) * 100, 1)
        }
        return QueryResponse(success=True, data=data, query_time=datetime.now().isoformat())
    finally:
        cur.close(); conn.close()

@app.get("/api/v1/events")
def get_events(limit: int = 100):
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT event_id, date, event_type, priority, status, is_abnormal, content_summary FROM events LIMIT %s", [limit])
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
    finally:
        cur.close(); conn.close()
