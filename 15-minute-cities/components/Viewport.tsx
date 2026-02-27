import React from "react";
import { useEffect, useState } from "react";
import { useMap, GeoJSON } from "react-leaflet";

export default function Viewport() {
    const map = useMap();
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null);
    const DEBOUNCE_DELAY = 300;

    const API_URL = "http://127.0.0.1:8000/api";

    const [data, setData] = useState(null);

    useEffect(() => {
        const updateBounds = () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            timeoutRef.current = setTimeout(async () => {
                const bounds = map.getBounds();

                const params = new URLSearchParams({
                    minlat: bounds.getSouth().toString(),
                    minlon: bounds.getWest().toString(),
                    maxlat: bounds.getNorth().toString(),
                    maxlon: bounds.getEast().toString(),
                });

                const resp = fetch(`${API_URL}/grid?${params.toString()}`).then(res => res.json())
                setData(await resp)

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

    console.log(data)
    if (!data) return null;

    return (
      <GeoJSON
        data={data}
        style={{
          color: "#3388ff",
          weight: 1
        }}
      />
    );
}