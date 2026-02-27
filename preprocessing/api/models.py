from pydantic import BaseModel

class BoundingBox(BaseModel):
    minlat: float
    minlon: float
    maxlat: float
    maxlon: float