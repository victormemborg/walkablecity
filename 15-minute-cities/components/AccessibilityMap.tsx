"use client";

import Map, { Layer, Source } from "react-map-gl/maplibre";
import type { VectorSourceSpecification, LayerSpecification, MapLibreEvent } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { AssertionError } from "assert";

type ScoreRange = [min: number, max: number];
type SourceDefinition = {
	id: string;
	maxZoom: number;
	style: Pick<LayerSpecification, "type" | "paint">;
};

const DEFAULT_SCORE_RANGE = [0, 10000] as ScoreRange;

// Returns MapLibre expression syntax: https://maplibre.org/maplibre-style-spec/expressions/
function makeScoreToColorInterpolation(range: ScoreRange = DEFAULT_SCORE_RANGE) {
	const [min, max] = range;
	return [
		"interpolate", ["linear"],
		["get", "score"],
		min, "#d73027",
		(min + max) / 2, "#ffffbf",
		max, "#1a9850"
	]
}

const GRID_STYLE = {
	type: "fill",
	paint: {
		"fill-color": makeScoreToColorInterpolation(),
		"fill-opacity": 0.5
	}
} as Pick<LayerSpecification, "type" | "paint">;

const EDGE_STYLE = {
	type: "line",
	paint: {
		"line-color": makeScoreToColorInterpolation(),
		"line-width": 2
	}
} as Pick<LayerSpecification, "type" | "paint">;

// Must be ordered by 'maxZoom' (smallest first)
const SOURCE_DEFINITIONS: SourceDefinition[] = [
	{id: "scored_grids_pmtiles_p5", maxZoom: 8, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p6", maxZoom: 12, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p7", maxZoom: 14, style: GRID_STYLE},
	{id: "scored_edges_pmtiles_p0", maxZoom: 18, style: EDGE_STYLE}
];
	
function toJSX(sourceDef: SourceDefinition) {
	const sourceId = `${sourceDef.id}-source`;
	const layerId = `${sourceDef.id}-layer`;
	const minzoom = SOURCE_DEFINITIONS.findLast(l => l.maxZoom < sourceDef.maxZoom)?.maxZoom ?? 0;

	const source = {
		type: "vector",
		tiles: [`http://localhost:3001/${sourceDef.id}/{z}/{x}/{y}`],
		minzoom: minzoom,
		maxzoom: sourceDef.maxZoom
	} as VectorSourceSpecification;

	const layer = {
		id: layerId,
		type: sourceDef.style.type,
		source: sourceId,
		"source-layer": sourceDef.id,
		paint: sourceDef.style.paint,
		minzoom: minzoom,
		maxzoom: sourceDef.maxZoom
	} as LayerSpecification;

	return (
		<Source key={sourceId} id={sourceId} {...source}>
			<Layer {...layer}/>
		</Source>
	);
}

function refreshScoreRange(event: MapLibreEvent) {
	const map = event.target;
	const sourceDef = SOURCE_DEFINITIONS.find(l => l.maxZoom >= map.getZoom());
	if (!sourceDef) throw new AssertionError({ message: "Invalid zoom level" });

	const layerId = `${sourceDef.id}-layer`;
	const range = map.queryRenderedFeatures(undefined, { layers: [layerId]})
		.map(f => f.properties.score as number)
		.reduce(
			(prev, curr) => [Math.min(prev[0], curr), Math.max(prev[1], curr)], 
			[Infinity, -Infinity]
		) as ScoreRange;

	const property = `${sourceDef.style.type}-color`;
	map.setPaintProperty(layerId, property, makeScoreToColorInterpolation(range));
}

export default function AccessibilityMap() {
	return (
		<Map 
		initialViewState={{
			longitude: 12.5683,
			latitude: 55.6761,
			zoom: 11
		}}
		mapStyle="https://tiles.openfreemap.org/styles/bright"
		maxZoom={18}
		onMoveEnd={refreshScoreRange}
		>
			{SOURCE_DEFINITIONS.map(toJSX)}
		</Map>
	);
}
	