import { useEffect, useRef, useCallback } from "react";
import { useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet.vectorgrid";
import { json } from "stream/consumers";

type Range = [min: number, max: number];
const BASE_MAX_SCORE = 10000;

function withinMargin(a: Range, b: Range, margin: number): boolean {
    const [minA, maxA] = a;
    const [minB, maxB] = b;
    return Math.abs((maxA - minA) - (maxB - minB)) < margin;
}

async function fetchScoreRange(bounds: L.LatLngBounds, table: string, signal: AbortSignal): Promise<Range> {
    const params = new URLSearchParams({
        minlat: String(bounds.getSouthWest().lat),
        minlon: String(bounds.getSouthWest().lng),
        maxlat: String(bounds.getNorthEast().lat),
        maxlon: String(bounds.getNorthEast().lng),
        table: table,
    });

    const API_URL = process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${API_URL}/bbox?${params.toString()}`, { signal });
    const content: {min: number, max: number} = await response.json();

    return [content.min, content.max];
}

const vectorTileLayerStyles = (colorFn: (score: number) => string) => new Proxy(
    {
        // Specific layer styles:
        scored_edges_pmtiles_p0: (properties: Record<string, string>) => {
            const color = colorFn(Number(properties.score))
            return {
                weight: 3,   
                color: color,
            };
        }
    },
    {
        get: (style: any, name: string) => style[name] ?? ((properties: Record<string, string>) => {
            // Default style:
            const color = colorFn(Number(properties.score));
            return {
                weight: 1,
                color: color,
                opacity: 1,
                fill: true,
                fillColor: color,
                fillOpacity: 0.3,
            };
        }),
    }
);

export default function VectorTileLayer({ url, layerName }: { url: string; layerName: string }) {
    const map = useMap();
    const scoreRangeRef = useRef<Range>([0, BASE_MAX_SCORE]);
    const vectorGridRef = useRef<L.VectorGrid.Protobuf | null>(null);
    const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // Modified from: https://gist.github.com/mlocati/7210513
    const colorGradient = (score: number) => {
        let [min, max] = scoreRangeRef.current;

        // Convert score to a value between 0 and 100. TODO: Look into bounding score between 0-100
        const actual = score / BASE_MAX_SCORE * 100;
        const viewportAdjusted = (score - min) / (max - min) * 100;
        // Desync between tile-renders (which calls this function) and 'scoreRangeRef' updates 
        // may cause 'viewportAdjusted' to exceed 100 although the math implies it should be 
        // impossible. This usually happens when panning large distances without letting go of 
        // mouse1. TODO: Look into enforcing synchronization.
        const capped = viewportAdjusted <= 100 ? viewportAdjusted : 100;
        const effective = (actual + capped) / 2;

        let r, g;
        const b = 0;

        if (effective < 50) {
            r = 255;
            g = Math.round(5.1 * effective);
        } else {
            g = 255;
            r = Math.round(510 - 5.1 * effective);
        }
        const h = r * 0x10000 + g * 0x100 + b;
        return "#" + ("000000" + h.toString(16)).slice(-6);
    }

    // Fetch score range for current viewport and redraw
    const refreshScoreRange = useCallback(async () => {
        if (debounceTimerRef.current) {
            clearTimeout(debounceTimerRef.current);
        }

        debounceTimerRef.current = setTimeout(async () => {
            abortControllerRef.current?.abort();
            abortControllerRef.current = new AbortController();

            const bounds = map.getBounds();
            const tableName = layerName.replace("pmtiles", "postgis");
            try {
                const updatedRange = await fetchScoreRange(bounds, tableName, abortControllerRef.current.signal);
                console.log(`Visible score range: ${updatedRange}`);

                if (updatedRange && !withinMargin(updatedRange, scoreRangeRef.current, 300)) {
                    scoreRangeRef.current = updatedRange;
                    vectorGridRef.current?.redraw();
                }
            } catch (err) {
                if (err instanceof DOMException && err.name === "AbortError") return;
            }
        }, 300);
    }, [map, layerName]);

    // Mount/unmount the layer once
    useEffect(() => {
        const vectorGrid = L.vectorGrid.protobuf(url, {
            rendererFactory: L.canvas.tile,
            interactive: false,
            vectorTileLayerStyles: vectorTileLayerStyles(colorGradient),
        });
        
        vectorGrid.addTo(map);
        vectorGridRef.current = vectorGrid;
        
        // Fetch initial range
        refreshScoreRange();
        
        return () => {
            if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
            abortControllerRef.current?.abort();
            map.removeLayer(vectorGrid);
            vectorGridRef.current = null;
        };
    }, [map, url]);

    useMapEvents({
        moveend: refreshScoreRange,
    });

    return null;
}