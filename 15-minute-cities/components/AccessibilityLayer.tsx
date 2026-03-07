import { useState } from "react";
import { useMapEvent } from "react-leaflet";
import VectorTileLayer from "./VectorTileLayer";
import { AssertionError } from "assert";

function zoomToTable(zoom: number): string {
    if (zoom <= 8) return "public.grid_precision_5";
    if (zoom <= 11) return "public.grid_precision_6";
    if (zoom <= 14) return "public.grid_precision_7";
    if (zoom <= 18) return "public.edges";
    throw new AssertionError({message: "unhandled zoom level"});
};

export default function AccessibilityLayer({ initialZoom }: { initialZoom: number }) {
    const [table, setTable] = useState(() => zoomToTable(initialZoom));

    useMapEvent("zoomend", e => {
        const newTable = zoomToTable(e.target.getZoom());
        setTable(newTable);
    });

    const url = `/tiles/${table}/{z}/{x}/{y}.pbf`;

    return (
        <VectorTileLayer
          url={url}
          layerName={table}
        />
    )
}