import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.vectorgrid";

const GRADIENT: Record<number, string> = {
  0.0:  "#1d0024",
  0.08: "#440154",
  0.20: "#3b528b",
  0.38: "#21918c",
  0.65: "#5ec962",
  1.0:  "#fde725",
};

const stops = Object.keys(GRADIENT).map(Number);

function getNearestGradientColor(value: number): string {
  const nearest = stops.reduce((prev, curr) =>
    Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev
  );
  return GRADIENT[nearest];
}

export default function VectorTileLayer({ url, layerName}: {url: string, layerName: string}) {
    const map = useMap();

    useEffect(() => {
        const vectorTileOptions = {
            rendererFactory: L.canvas.tile, // L.canvas.tile | L.svg.tile
            interactive: false,
            vectorTileLayerStyles: {
                [layerName]: (properties: Record<string, string>) => {
                    const score = Number(properties.score)
                    const color = getNearestGradientColor(score / 5)
                    return {
                        weight: 1,
                        color: color,
                        opacity: 1,
                        fill: true,
                        fillColor: color,
                        fillOpacity: 0.3,
                    };
                },
            },
        };

        const vectorGrid = L.vectorGrid.protobuf(url, vectorTileOptions);
        vectorGrid.addTo(map);

        return () => {
            map.removeLayer(vectorGrid);
        };
    }, [map, url, layerName]);

    return null;
}