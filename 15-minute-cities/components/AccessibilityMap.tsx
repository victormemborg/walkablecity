"use client";

import Map, { Layer, Source, ViewStateChangeEvent} from "react-map-gl/maplibre";
import type { FillLayerSpecification, LineLayerSpecification, VectorSourceSpecification } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";

const gridsP5Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_grids_pmtiles_p5/{z}/{x}/{y}.pbf"],
	minzoom: 0,
	maxzoom: 8
};

const gridsP5Style: FillLayerSpecification = {
	id: "grids-p5-style",
	type: "fill",
	source: "grids-p5-source",
	"source-layer": "scored_grids_pmtiles_p5", 
	paint: {
		"fill-color": "#9b0d0d",
		"fill-opacity": 0.5
	},
	minzoom: 0,
	maxzoom: 8
};

const gridsP6Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_grids_pmtiles_p6/{z}/{x}/{y}.pbf"],
	minzoom: 8,
	maxzoom: 12
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
	minzoom: 8,
	maxzoom: 12
};

const gridsP7Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_grids_pmtiles_p7/{z}/{x}/{y}.pbf"],
	minzoom: 12,
	maxzoom: 14
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
	minzoom: 12,
	maxzoom: 14
};

const edgesP0Source: VectorSourceSpecification = {
	type: "vector" as const,
	tiles: ["http://localhost:3001/scored_edges_pmtiles_p0/{z}/{x}/{y}.pbf"],
	minzoom: 14,
	maxzoom: 18
};

const edgesP0Style: LineLayerSpecification = {
	id: "edges-p0-style",
	type: "line",
	source: "edges-p0-source",
	"source-layer": "scored_edges_pmtiles_p0", 
	paint: {
		"line-color": "#2c0d9b",
		"line-width": 2
	},
	minzoom: 14,
	maxzoom: 19 // max + 1
};

export default function AccessibilityMap() {
	const initialZoom = 11;

	const onZoomEnd = (e: ViewStateChangeEvent) => {
		const zoom = e.target.getZoom();
		console.log(`Zoom: ${zoom}`);
	};

	return (
		<Map 
			initialViewState={{
				longitude: 12.5683,
				latitude: 55.6761,
				zoom: initialZoom
			}}
			mapStyle="https://tiles.openfreemap.org/styles/bright"
			maxZoom={18}
			onZoomEnd={onZoomEnd}
		>
			<Source id="grids-p5-source" {...gridsP5Source}>
				<Layer {...gridsP5Style} />
			</Source>
			<Source id="grids-p6-source" {...gridsP6Source}>
				<Layer {...gridsP6Style} />
			</Source>
			<Source id="grids-p7-source" {...gridsP7Source}>
				<Layer {...gridsP7Style} />
			</Source>	
			<Source id="edges-p0-source" {...edgesP0Source}>
				<Layer {...edgesP0Style} />
			</Source>	
		</Map>
	);
}
