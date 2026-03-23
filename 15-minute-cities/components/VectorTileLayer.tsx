import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.vectorgrid";

const MAX_DIST = 10000;

// Taken from: https://gist.github.com/mlocati/7210513
function colorGradient(score: number): string {
    const perc = score / MAX_DIST * 100
	var r, g, b = 0;

	if(perc < 50) {
		r = 255;
		g = Math.round(5.1 * perc);
	}
	else {
		g = 255;
		r = Math.round(510 - 5.10 * perc);
	}
	var h = r * 0x10000 + g * 0x100 + b * 0x1;
	return '#' + ('000000' + h.toString(16)).slice(-6);
}

const defaultStyle = (properties: Record<string, string>) => {
    const score = Number(properties.score)
    const color = colorGradient(score)
    return {
        weight: 1,
        color: color,
        opacity: 1,
        fill: true,
        fillColor: color,
        fillOpacity: 0.3,
    };
};

const vectorTileLayerStyles = new Proxy(
    {
        scored_edges_pmtiles_p0: (properties: Record<string, string>) => {
            const score = Number(properties.score)
            const color = colorGradient(score)
            return {
                weight: 3,   
                color: color,
            };
        },
    },
    {
        get: (style: any, layerName: string) => {
            return style[layerName] || defaultStyle;
        }
    }
);


export default function VectorTileLayer({url, layerName}: {url: string, layerName: string}) {
    const map = useMap();

    useEffect(() => {
        const vectorTileOptions = {
            rendererFactory: L.canvas.tile, // L.canvas.tile | L.svg.tile
            interactive: false,
            vectorTileLayerStyles: vectorTileLayerStyles,
        };

        const vectorGrid = L.vectorGrid.protobuf(url, vectorTileOptions);
        vectorGrid.addTo(map);

        return () => {
            map.removeLayer(vectorGrid);
        };
    }, [map, url, layerName]);

    return null;
}