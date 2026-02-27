from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db
from models import BoundingBox

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
)

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/api/edges")
def get_edges(
    bbox: BoundingBox = Depends(),
    db: Session = Depends(get_db),
):
    sql = text("""
        SELECT ST_AsGeoJSON(linestring), score_from, score_to
        FROM edges
        WHERE linestring && ST_MakeEnvelope(
            :minlon, :minlat,
            :maxlon, :maxlat,
            4326
        )
    """)
    
    rows = db.execute(sql, bbox.model_dump()).mappings().all()
    return {"edges": rows}

@app.get("/api/grid")
def get_grid(
    bbox: BoundingBox = Depends(),
    db: Session = Depends(get_db),
):
    sql = text("""
        SELECT ST_AsGeoJSON(rectangle), score
        FROM grid
        WHERE rectangle && ST_MakeEnvelope(
            :minlon, :minlat,
            :maxlon, :maxlat,
            4326
        )
    """)
    
    rows = db.execute(sql, bbox.model_dump()).mappings().all()
    return {"grid": rows}