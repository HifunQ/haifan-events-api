from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
import os

app = FastAPI(title="嗨番事件库 API", version="1.2.3")
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
    return psycopg2.connect(host=p.hostname, port=p.port or 5432, user=p.username, password=p.password, dbname=p.path.lstrip('/'), sslmode='require')

def query_db(sql, params=None, fetch_one=False):
    conn = get_db_conn()
    import psycopg2.extras
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql, params or [])
    if fetch_one:
        row = cursor.fetchone()
        result = dict(row) if row else {}
    else:
        result = [dict(row) for row in cursor.fetchall()]
    cursor.close(); conn.close()
    return result

@app.get("/")
def root(): return {"name": "嗨番事件库 API", "version": "1.2.3"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/kpi")
def get_kpi():
    try:
        total = query_db("SELECT COUNT(*) as c FROM events", fetch_one=True).get('c', 0)
        issues = query_db("SELECT COUNT(*) as c FROM issues", fetch_one=True).get('c', 0)
        abnormal = query_db("SELECT COUNT(*) as c FROM events WHERE is_abnormal=1", fetch_one=True).get('c', 0)
        data = {"total_events": total, "total_issues": issues, "abnormal_events": abnormal, "abnormal_rate": round(abnormal/max(total,1)*100,1)}
        return QueryResponse(success=True, data=data, query_time=datetime.now().isoformat())
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/v1/events")
def get_events(limit: int = 100):
    rows = query_db("SELECT event_id, date, event_type, priority, status, content_summary FROM events LIMIT %s", [limit])
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))

@app.get("/api/v1/query/{query_type}")
def get_query_by_type(query_type: str):
    queries = {
        "event_types_dist": "SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type ORDER BY count DESC",
        "key_metrics": "SELECT metric_name, metric_value FROM key_metrics",
    }
    if query_type not in queries: raise HTTPException(status_code=400, detail=f"不支持: {query_type}")
    rows = query_db(queries[query_type])
    return QueryResponse(success=True, data=rows, query_time=datetime.now().isoformat(), total_count=len(rows))
