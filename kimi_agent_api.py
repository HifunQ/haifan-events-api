from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import os

app = FastAPI(title="嗨番事件库 API", version="1.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryResponse(BaseModel):
    success: bool
    data: Any
    query_time: str
    total_count: Optional[int] = None

def get_db_conn():
    db_url = os.getenv('DATABASE_URL', '')
    import psycopg2
    import urllib.parse
    p = urllib.parse.urlparse(db_url)
    return psycopg2.connect(
        host=p.hostname, port=p.port or 5432,
        user=p.username, password=p.password,
        database=p.path.lstrip('/'), sslmode='require'
    )

def query_count(sql):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute(sql); result = cur.fetchone()[0]
    cur.close(); conn.close(); return result

def query_rows(sql, params=None):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close(); conn.close(); return rows

@app.get("/")
def root(): return {"name": "嗨番事件库 API", "version": "1.5.0"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/kpi")
def get_kpi():
    try:
        total = query_count("SELECT COUNT(*) FROM events")
        issues = query_count("SELECT COUNT(*) FROM issues")
        abnormal = query_count("SELECT COUNT(*) FROM events WHERE is_abnormal=1")
        return QueryResponse(success=True, data={"total_events": total, "total_issues": issues, "abnormal_events": abnormal, "abnormal_rate": round(abnormal/max(total,1)*100, 1)}, query_time=datetime.now().isoformat())
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/events")
def get_events(limit: int = 100):
    rows = query_rows("SELECT event_id, date, event_type, priority, status, content_summary FROM events LIMIT %s", [limit])
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
