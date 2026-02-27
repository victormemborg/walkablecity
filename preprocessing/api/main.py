from fastapi import Depends, FastAPI, Query

from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db

app = FastAPI()

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/api/edges")
def get_edges(
    minLon: float = Query(...),
    minLat: float = Query(...),
    maxLon: float = Query(...),
    maxLat: float = Query(...),
    db: Session = Depends(get_db),
):
    sql = text("""
        SELECT *
        FROM edges
        WHERE linestring && ST_MakeEnvelope(
            :minLon, :minLat,
            :maxLon, :maxLat,
            4326
        )
    """)
    
    rows = db.execute(sql, {
        "minLon": minLon,
        "minLat": minLat,
        "maxLon": maxLon,
        "maxLat": maxLat,
    }).mappings().all()
    return {"count": len(rows), "edges": rows}

@app.get("/api/grid")
def get_grid(
    minLon: float = Query(...),
    minLat: float = Query(...),
    maxLon: float = Query(...),
    maxLat: float = Query(...),
    db: Session = Depends(get_db),
):
    sql = text("""
        SELECT *
        FROM grid
        WHERE rectangle && ST_MakeEnvelope(
            :minLon, :minLat,
            :maxLon, :maxLat,
            4326
        )
    """)
    
    rows = db.execute(sql, {
        "minLon": minLon,
        "minLat": minLat,
        "maxLon": maxLon,
        "maxLat": maxLat,
    }).mappings().all()
    return {"count": len(rows), "grid": rows}
