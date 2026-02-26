import { useEffect } from "react";
import { useMap } from "react-leaflet";

export default function BoundingBox() {
    const map = useMap();

    useEffect(() => {
        const updateBounds = () => {
            const bounds = map.getBounds();
            const bbox = {
                minLat: bounds.getWest(),
                minLng: bounds.getSouth(),
                maxLat: bounds.getEast(),
                maxLng: bounds.getNorth(),
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