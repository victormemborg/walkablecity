import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.vectorgrid";

export default function VectorTileLayer({ url, layerName}: {url: string, layerName: string}) {
    const map = useMap();

    useEffect(() => {
        const vectorTileOptions = {
            rendererFactory: L.canvas.tile,
            interactive: true,
            vectorTileLayerStyles: {
                // layerName must match pg_tileserv table/layer name (according to some random source)
                [layerName]: {
                    weight: 1,
                    color: "#3388ff",
                    opacity: 1,
                    fill: true,
                    fillColor: "#3388ff",
                    fillOpacity: 0.3,
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