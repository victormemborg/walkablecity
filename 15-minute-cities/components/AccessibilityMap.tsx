"use client";

import Map, { Layer, MapRef, Source } from "react-map-gl/maplibre";
import type { VectorSourceSpecification, LayerSpecification, MapLibreEvent } from 'maplibre-gl';
import { AssertionError } from "assert";
import { useEffect, useRef } from "react";
import type { ScoreRange } from "../types/mapTypes";
import { getColorExpression, MAX_SCORE_RANGE } from "../utils/scoreColor";
import type { MapView } from "../types/mapTypes";

type SourceDefinition = {
	id: string;
	maxZoom: number;
	style: Pick<LayerSpecification, "type" | "paint">;
};

function getGridStyle(colorBlindMode: boolean) {
	return {
		type: "fill",
		paint: {
			"fill-color": getColorExpression(MAX_SCORE_RANGE, colorBlindMode),
			"fill-opacity": 0.5
		}
	} as Pick<LayerSpecification, "type" | "paint">;
}

function getEdgeStyle(colorBlindMode: boolean) {
	return {
		type: "line",
		paint: {
			"line-color": getColorExpression(MAX_SCORE_RANGE, colorBlindMode),
			"line-width": 2
		}
	} as Pick<LayerSpecification, "type" | "paint">;
}

// Must be ordered by 'maxZoom' (smallest first)
function getSourceDefinitions(colorBlindMode: boolean): SourceDefinition[] {
	const gridStyle = getGridStyle(colorBlindMode);
	const edgeStyle = getEdgeStyle(colorBlindMode);
	return [
		{id: "interpolated_grids_pmtiles_p5", maxZoom: 9, style: gridStyle},
		{id: "interpolated_grids_pmtiles_p6", maxZoom: 12, style: gridStyle},
		{id: "interpolated_grids_pmtiles_p7", maxZoom: 15, style: gridStyle},
		{id: "scored_edges_pmtiles_p0", maxZoom: 18, style: edgeStyle}
	];
}

function toJSX(sourceDef: SourceDefinition, sourceDefinitions: SourceDefinition[]) {
	const sourceId = `${sourceDef.id}-source`;
	const layerId = `${sourceDef.id}-layer`;
	const minzoom = sourceDefinitions.findLast(def => def.maxZoom < sourceDef.maxZoom)?.maxZoom ?? 0;
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

export default function AccessibilityMap({center, zoom, colorBlindMode}: MapView & {colorBlindMode: boolean}) {
	const cooldownTimerRef = useRef<NodeJS.Timeout>(null);
	const sourceDefinitions = getSourceDefinitions(colorBlindMode);
	const mapRef = useRef<MapRef>(null);

	const refreshScoreRange = () => {
		if (cooldownTimerRef.current) return;

		const map = mapRef.current?.getMap();
		if (!map || !map.isStyleLoaded()) return;

		const sourceDef = sourceDefinitions.find(def => def.maxZoom >= map.getZoom());
		if (!sourceDef) throw new AssertionError({ message: "Invalid zoom level" });

		const layerId = `${sourceDef.id}-layer`;
		const scores = map.queryRenderedFeatures(undefined, { layers: [layerId]})
			.map(f => f.properties.score as number)
			.sort((a, b) => a - b);
		if (scores.length <= 0) return;

		const lowIdx = Math.floor(scores.length * 0.05);
		const highIdx = Math.floor(scores.length * 0.95);
		const range = [scores[lowIdx], scores[highIdx]] as ScoreRange;

		const property = `${sourceDef.style.type}-color`;
		map.setPaintProperty(layerId, property, getColorExpression(range, colorBlindMode));

		cooldownTimerRef.current = setTimeout(() => {
			cooldownTimerRef.current = null;
		}, 200);
	}

	useEffect(() => {
		const map = mapRef.current;
		const unsubsribeAndRefresh = () => {
			map?.off("idle", unsubsribeAndRefresh);
			refreshScoreRange();
		}

		map?.on("idle", unsubsribeAndRefresh);
	}, [colorBlindMode])

	return (
		<Map
		ref={mapRef}
		initialViewState={{
			latitude: center.lat,
			longitude: center.lon,
			zoom: zoom
		}}
		mapStyle="https://tiles.openfreemap.org/styles/positron"
		maxZoom={18}
		onMove={refreshScoreRange}
		onMoveEnd={refreshScoreRange}
		onLoad={refreshScoreRange}
		>
			{sourceDefinitions.map(def => toJSX(def, sourceDefinitions))}
		</Map>
	);
}