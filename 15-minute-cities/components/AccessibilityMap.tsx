"use client";

import Map, { Layer, Source } from "react-map-gl/maplibre";
import type { VectorSourceSpecification, LayerSpecification, MapLibreEvent } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";
import { AssertionError } from "assert";
import { useRef } from "react";

type ScoreRange = [min: number, max: number];
type AccessibilityMapProps = {center: {lat: number, lon: number}, zoom: number};
type SourceDefinition = {
	id: string;
	maxZoom: number;
	style: Pick<LayerSpecification, "type" | "paint">;
};

const MAX_SCORE_RANGE = [0, 10000] as ScoreRange;

// Returns MapLibre expression syntax: https://maplibre.org/maplibre-style-spec/expressions/
function colorInterpolate(currentRange: ScoreRange) {
	const minSpreadFraction = 0.5
    const globalSpread = MAX_SCORE_RANGE[1] - MAX_SCORE_RANGE[0];
    const minSpread = globalSpread * minSpreadFraction;
    const mid = (currentRange[0] + currentRange[1]) / 2;
    const halfSpread = Math.max((currentRange[1] - currentRange[0]) / 2, minSpread / 2);
    const min = Math.max(MAX_SCORE_RANGE[0], mid - halfSpread);
    const max = Math.min(MAX_SCORE_RANGE[1], mid + halfSpread);

	return [
		"interpolate", ["linear"],
		["get", "score"],
		min, "#d73027",
		(min + max) / 2, "#f3f37d",
		max, "#1a9850"
	]
}

const GRID_STYLE = {
	type: "fill",
	paint: {
		"fill-color": colorInterpolate(MAX_SCORE_RANGE),
		"fill-opacity": 0.5
	}
} as Pick<LayerSpecification, "type" | "paint">;

const EDGE_STYLE = {
	type: "line",
	paint: {
		"line-color": colorInterpolate(MAX_SCORE_RANGE),
		"line-width": 2
	}
} as Pick<LayerSpecification, "type" | "paint">;

// Must be ordered by 'maxZoom' (smallest first)
const SOURCE_DEFINITIONS: SourceDefinition[] = [
	{id: "scored_grids_pmtiles_p5", maxZoom: 9, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p6", maxZoom: 12, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p7", maxZoom: 15, style: GRID_STYLE},
	{id: "scored_edges_pmtiles_p0", maxZoom: 18, style: EDGE_STYLE}
];
	
function toJSX(sourceDef: SourceDefinition) {
	const sourceId = `${sourceDef.id}-source`;
	const layerId = `${sourceDef.id}-layer`;
	const minzoom = SOURCE_DEFINITIONS.findLast(l => l.maxZoom < sourceDef.maxZoom)?.maxZoom ?? 0;
	const baseTileUrl = process.env.NODE_ENV === "development" ? "http://localhost:8080/tiles" : "https://walkablecity.app/tiles";

	const source = {
		type: "vector",
		tiles: [`${baseTileUrl}/${sourceDef.id}/{z}/{x}/{y}`],
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

export default function AccessibilityMap({center, zoom}: AccessibilityMapProps) {
	const cooldownTimerRef = useRef<NodeJS.Timeout>(null);
	
	const refreshScoreRange = (event: MapLibreEvent) => {
		if (cooldownTimerRef.current) return;

		const map = event.target;
		const sourceDef = SOURCE_DEFINITIONS.find(l => l.maxZoom >= map.getZoom());
		if (!sourceDef) throw new AssertionError({ message: "Invalid zoom level" });

		const layerId = `${sourceDef.id}-layer`;
		const scores = map.queryRenderedFeatures(undefined, { layers: [layerId]})
			.map(f => f.properties.score as number)
			.sort((a, b) => a - b);
		
		if (scores.length <= 0) return;

		const lowIdx = Math.floor(scores.length * 0.05);
		const highIdx = Math.ceil(scores.length * 0.95);
		const range = [scores[lowIdx], scores[highIdx]] as ScoreRange;

		const property = `${sourceDef.style.type}-color`;
		map.setPaintProperty(layerId, property, colorInterpolate(range));

		cooldownTimerRef.current = setTimeout(() => {
			cooldownTimerRef.current = null;
		}, 200);
	}

	return (
		<Map 
		initialViewState={{
			latitude: center.lat,
			longitude: center.lon,
			zoom: zoom
		}}
		mapStyle="https://tiles.openfreemap.org/styles/positron"
		maxZoom={18}
		onMove={refreshScoreRange}
		onMoveEnd={refreshScoreRange}
		>
			{SOURCE_DEFINITIONS.map(toJSX)}
		</Map>
	);
}
	
