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

const vectorTileLayerStyles = (colorFn: (score: number) => string) => new Proxy(
    {
        // Specific styles:
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

    // Taken from: https://gist.github.com/mlocati/7210513
    const colorGradient = (score: number) => {
        const [min, max] = scoreRangeRef.current;

        const actual = score / BASE_MAX_SCORE * 100;
        const normalized = (score - min) / (max - min) * 100;
        const effective = (actual + normalized*2) / 3

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
        const bounds = map.getBounds();
        const tableName = layerName.replace("pmtiles", "postgis");

        const scoreRange = await fetchScoreRange(bounds, tableName);
        console.log(scoreRange);

        if (scoreRange && scoreRange !== scoreRangeRef.current) {
            scoreRangeRef.current = scoreRange;
            vectorGridRef.current?.redraw();
        }
    }, [map]);

    // Mount/unmount the layer once
    useEffect(() => {
        const vectorGrid = L.vectorGrid.protobuf(url, {
            rendererFactory: L.canvas.tile,
            interactive: false,
            vectorTileLayerStyles: vectorTileLayerStyles(colorGradient),
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