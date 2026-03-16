import { useState } from "react";
import { useMapEvent } from "react-leaflet";
import VectorTileLayer from "./VectorTileLayer";
import { AssertionError } from "assert";

function zoomToTable(zoom: number): string {
    if (zoom <= 8) return "scored_grids_pmtiles_p5";
    if (zoom <= 11) return "scored_grids_pmtiles_p6";
    if (zoom <= 14) return "scored_grids_pmtiles_p7";
    if (zoom <= 18) return "public.edges";
    throw new AssertionError({message: "unhandled zoom level"});
};

export default function AccessibilityLayer({baseTileUrl, initialZoom}: {baseTileUrl: string, initialZoom: number}) {
    const [table, setTable] = useState(() => zoomToTable(initialZoom));

    useMapEvent("zoomend", e => {
        const newTable = zoomToTable(e.target.getZoom());
        console.log(e.target.getZoom())
        setTable(newTable);
    });

    const url = `${baseTileUrl}${table}/{z}/{x}/{y}.mvt`;
    return (
        <VectorTileLayer
          url={url}
          layerName={table}
        />
    )
}