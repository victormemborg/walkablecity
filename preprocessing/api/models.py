from pydantic import BaseModel

class BoundingBox(BaseModel):
    minlat: float
    minlon: float
    maxlat: float
    maxlon: float
    zoom: int

    @property
    def level(self):
        """Translates leaflet zoom level to geohash precision."""
        if self.zoom <= 6:
            return 3
        elif self.zoom <= 9:
            return 4
        elif self.zoom <= 11:
            return 5
        elif self.zoom <= 13:
            return 6
        else:
            return 7