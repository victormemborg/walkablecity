import { useEffect } from "react";
import { useMap } from "react-leaflet";

export default function Viewport() {
    const map = useMap();

    useEffect(() => {
        const updateBounds = () => {
            const bounds = map.getBounds();
            const bbox = {
            minLat: bounds.getSouth(),
            minLng: bounds.getWest(),
            maxLat: bounds.getNorth(),
            maxLng: bounds.getEast(),
            };
            console.log("Current bbox", bbox);
        };
        // Initial log
        updateBounds();

        map.on("moveend", updateBounds);

        return () => {
            map.off("moveend", updateBounds);
        };
    }, [map]);

    return null;
}