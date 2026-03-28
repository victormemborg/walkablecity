"use client";

import { useState } from "react";
import Map, { Layer, Source, ViewStateChangeEvent} from "react-map-gl/maplibre";
import type { FillLayerSpecification, VectorSourceSpecification } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { AssertionError } from "assert";
import AccessibilityLayer from "./AccessibilityLayer";

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

function zoomToLayerId(zoom: number): string {
    if (zoom <= 8) return "scored_grids_pmtiles_p5";
    if (zoom <= 12) return "scored_grids_pmtiles_p6";
    if (zoom <= 14) return "scored_grids_pmtiles_p7";
    if (zoom <= 18) return "scored_edges_pmtiles_p0";
    throw new AssertionError({message: "unhandled zoom level"});
};

export default function AccessibilityMap() {
	const initialZoom = 11;
	const [layerId, setLayerId] = useState(zoomToLayerId(initialZoom));
	const tileUrl = `http://localhost:3001/${layerId}/{z}/{x}/{y}.pbf`;

	const onZoomEnd = (e: ViewStateChangeEvent) => {
		const zoom = e.target.getZoom();
		console.log(`Zoom: ${zoom}`);
		setLayerId(zoomToLayerId(zoom));
	};

	return (
		<Map 
			initialViewState={{
				longitude: 12.5683,
				latitude: 55.6761,
				zoom: initialZoom
			}}
			mapStyle="https://tiles.openfreemap.org/styles/bright"
			onZoomEnd={onZoomEnd}
		>
			<AccessibilityLayer 
				tileUrl={tileUrl}
				layerId={layerId}
			/>
		</Map>
	);
}
