"use client";

import Map, { Layer, Source, useMap} from "react-map-gl/maplibre";
import type { FillLayerSpecification, VectorSourceSpecification } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";

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

const gridsP7Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_grids_pmtiles_p7/{z}/{x}/{y}.pbf"],
	minzoom: 10,
	maxzoom: 18
};

const gridsP7Style: FillLayerSpecification = {
	id: "grids-p7-style",
	type: "fill",
	source: "grids-p7-source",
	"source-layer": "scored_grids_pmtiles_p7", 
	paint: {
		"fill-color": "#2c0d9b",
		"fill-opacity": 0.5
	},
	minzoom: 10,
	maxzoom: 18
};

export default function AccessibilityMap() {
	return (
		<Map 
			initialViewState={{
				longitude: 12.5683,
				latitude: 55.6761,
				zoom: 11
			}}
			mapStyle="https://tiles.openfreemap.org/styles/bright"
		>
			<Source id="grids-p6-source" {...gridsP6Source}>
				<Layer {...gridsP6Style} />
			</Source>
			<Source id="grids-p7-source" {...gridsP7Source}>
				<Layer {...gridsP7Style} />
			</Source>
		</Map>
	);
}
