import time

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

ZOOM_TO_TABLE_MAP: dict[int, str] = {
    0: "grid_precision_4",
    1: "grid_precision_4",
    2: "grid_precision_4",
    3: "grid_precision_4",
    4: "grid_precision_4",
    5: "grid_precision_4",
    6: "grid_precision_4",
    7: "grid_precision_4",
    8: "grid_precision_4",
    9: "grid_precision_5",
    10: "grid_precision_5",
    11: "grid_precision_6",
    12: "grid_precision_6",
    13: "grid_precision_6",
    14: "grid_precision_7",
    15: "grid_precision_7",
    16: "grid_precision_7",
    17: "grid_precision_7",
    18: "grid_precision_7",
}

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/api/bbox")
def get_grid(bbox: BoundingBox = Depends(), db: Session = Depends(get_db)):
    start = time.perf_counter()

    params = bbox.model_dump()
    table = ZOOM_TO_TABLE_MAP.get(params["zoom"])
    sql = text(
        f"""
        SELECT ST_AsGeoJSON(geometry), score
        FROM {table}
        WHERE geometry && ST_MakeEnvelope(
            :minlon, :minlat,
            :maxlon, :maxlat,
            4326
        )
        """
    )

    rows = db.execute(sql, params).mappings().all()

    duration = time.perf_counter() - start
    print(duration)
    
    return {"geometry": rows}