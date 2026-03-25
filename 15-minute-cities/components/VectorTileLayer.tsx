import { useEffect, useRef, useCallback } from "react";
import { useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet.vectorgrid";

type Range = [min: number, max: number];
const BASE_MAX_SCORE = 10000;

async function fetchScoreRange(bounds: L.LatLngBounds, table: string): Promise<Range> {
    const params = new URLSearchParams({
        minlat: String(bounds.getSouth()),
        minlon: String(bounds.getWest()),
        maxlat: String(bounds.getNorth()),
        maxlon: String(bounds.getEast()),
        table: table,
    });

    const API_URL = process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${API_URL}/bbox?${params.toString()}`);
    const content: {min: number, max: number} = await response.json();

    return [content.min, content.max];
}

// Taken from: https://gist.github.com/mlocati/7210513
function colorGradient(score: number, scoreRange: Range): string {
    const [min, max] = scoreRange;
    const perc = (score - min) / (max - min) * 100;

    let r, g;
    const b = 0;
    if (perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
    } else {
        g = 255;
        r = Math.round(510 - 5.1 * perc);
    }
    const h = r * 0x10000 + g * 0x100 + b;
    return "#" + ("000000" + h.toString(16)).slice(-6);
}

export default function VectorTileLayer({ url, layerName }: { url: string; layerName: string }) {
    const map = useMap();
    const scoreRangeRef = useRef<Range>([0, 10000]);
    const vectorGridRef = useRef<L.VectorGrid.Protobuf | null>(null);

    // Style functions close over maxScoreRef — always read the latest value
    const makeStyle = useCallback((properties: Record<string, string>, weight: number) => {
        const score = Number(properties.score);
        const color = colorGradient(score, scoreRangeRef.current);
        return { weight, color, opacity: 1, fill: true, fillColor: color, fillOpacity: 0.3 };
    }, []);

    const vectorTileLayerStyles = new Proxy(
        {
            scored_edges_pmtiles_p0: (properties: Record<string, string>) =>
                makeStyle(properties, 3),
        },
        {
            get: (style: any, name: string) =>
                style[name] ?? ((props: Record<string, string>) => makeStyle(props, 1)),
        }
    );

    // Fetch max score for current viewport and redraw
    const refreshScoreRange = useCallback(async () => {
        const bounds = map.getBounds();
        const tableName = layerName.replace("pmtiles", "postgis");
        try {
            const scoreRange = await fetchScoreRange(bounds, tableName);
            console.log(scoreRange);
            if (scoreRange && scoreRange !== scoreRangeRef.current) {
                scoreRangeRef.current = scoreRange;
                // Imperatively redraw — no React re-render needed
                vectorGridRef.current?.redraw();
            }
        } catch (err) {
            console.error("Failed to fetch max score", err);
        }
    }, [map]);

    // Mount/unmount the layer once
    useEffect(() => {
        const vectorGrid = L.vectorGrid.protobuf(url, {
            rendererFactory: L.canvas.tile,
            interactive: false,
            vectorTileLayerStyles: vectorTileLayerStyles,
        });
        vectorGrid.addTo(map);
        vectorGridRef.current = vectorGrid;
        return () => {
            map.removeLayer(vectorGrid);
            vectorGridRef.current = null;
        };
    }, [map, url]);

    useMapEvents({
        moveend: refreshScoreRange,
    });

    return null;
}