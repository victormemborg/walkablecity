import { VectorSourceSpecification, FillLayerSpecification } from "maplibre-gl";
import { Source, Layer } from "react-map-gl/maplibre";

const gridsP6Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_grids_pmtiles_p6/{z}/{x}/{y}.pbf"],
	minzoom: 0,
	maxzoom: 9
};

const gridsP6Style: FillLayerSpecification = {
	id: "grids-p6-style",
	type: "fill",
	source: "grids-p6-source",
	"source-layer": "scored_grids_pmtiles_p6", 
	paint: {
		"fill-color": "#9b0d0d",
		"fill-opacity": 0.5
	},
	minzoom: 0,
	maxzoom: 10
};

export default function AccessibilityLayer({tileUrl, layerId}: {tileUrl: string, layerId: string}) {
    const sourceId = `test-source`;
    const styleId = `test-style`;

    const source: VectorSourceSpecification = {
        type: "vector" as const,
        tiles: [tileUrl],
    }

    const style: FillLayerSpecification = {
        id: styleId,
        type: "fill",
        source: sourceId,
        "source-layer": layerId, 
        paint: {
            "fill-color": "#9b0d0d",
            "fill-opacity": 0.5
        },
    }

    return (
        <Source id={sourceId} {...source}>
            <Layer {...style}/>
        </Source>
    )
}