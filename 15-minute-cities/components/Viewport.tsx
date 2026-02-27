import { LatLngBounds } from "leaflet";
import React from "react";
import { useEffect, useState } from "react";
import { useMap, GeoJSON } from "react-leaflet";
import type { FeatureCollection } from "geojson"

async function fetchData(bounds: LatLngBounds): Promise<FeatureCollection> {
    const API_URL = "http://127.0.0.1:8000/api";
    const params = new URLSearchParams({
        minlat: bounds.getSouth().toString(),
        minlon: bounds.getWest().toString(),
        maxlat: bounds.getNorth().toString(),
        maxlon: bounds.getEast().toString(),
    });

    const res = await fetch(`${API_URL}/grid?${params.toString()}`);
    const resp: { grid: { st_asgeojson: string }[]; } = await res.json();

    return {type: "FeatureCollection", features: resp.grid.map(rect => JSON.parse(rect.st_asgeojson))};
}

export default function Viewport() {
    const map = useMap();
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null);
    const DEBOUNCE_DELAY = 300;

    const [data, setData] = useState<FeatureCollection | null>(null);

    useEffect(() => {
        const updateBounds = () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            timeoutRef.current = setTimeout(async () => {
                const bounds = map.getBounds();
                const data = await fetchData(bounds);
                setData(data)
            }, DEBOUNCE_DELAY);
        };
        // initial update
        updateBounds();

        map.on("moveend", updateBounds);

        return () => {
            map.off("moveend", updateBounds);
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [map]);

    console.log(data);
    if (!data) return null;

    return (
      <GeoJSON
        key={data.features.length}
        data={data}
        style={{
          color: "#3388ff",
          weight: 1
        }}
      />
    );
}