import { useState } from "react";
import { useMapEvent } from "react-leaflet";
import VectorTileLayer from "./VectorTileLayer";
import { AssertionError } from "assert";

function zoomToLayer(zoom: number): string {
    if (zoom <= 8) return "scored_grids_pmtiles_p5";
    if (zoom <= 12) return "scored_grids_pmtiles_p6";
    if (zoom <= 14) return "scored_grids_pmtiles_p7";
    if (zoom <= 18) return "scored_edges_pmtiles_p0";
    throw new AssertionError({message: "unhandled zoom level"});
};

export default function AccessibilityLayer({baseTileUrl, initialZoom}: {baseTileUrl: string, initialZoom: number}) {
    const [layer, setLayer] = useState(() => zoomToLayer(initialZoom));

    useMapEvent("zoomend", e => {
        const newLayer = zoomToLayer(e.target.getZoom());
        console.log(e.target.getZoom())
        setLayer(newLayer);
    });

    const url = `${baseTileUrl}${layer}/{z}/{x}/{y}`;
    return (
        <VectorTileLayer
          url={url}
          layerName={layer}
        />
    )
}