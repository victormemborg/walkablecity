from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db
from models import BoundingBox

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002",  "http://127.0.0.1:3002"]
)

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/api/bbox")
def get_grid(bbox: BoundingBox = Depends(), db: Session = Depends(get_db)):
    sql = text(
        f"""
        SELECT MIN(score), MAX(score)
        FROM {bbox.table}
        WHERE geometry && ST_MakeEnvelope(
            :minlon, :minlat,
            :maxlon, :maxlat,
            4326
        )
        """
    )

    params = bbox.model_dump()
    result = db.execute(sql, params).mappings().first()
    
    return result
