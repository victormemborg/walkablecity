"use client";

import Map, { Layer, Source, ViewStateChangeEvent} from "react-map-gl/maplibre";
import type { LineLayerSpecification, VectorSourceSpecification, LayerSpecification } from 'maplibre-gl';
import "maplibre-gl/dist/maplibre-gl.css";

type TileLayer = {
	id: string;
	maxZoom: number;
	style: Pick<LayerSpecification, "type" | "paint">;
};

const GRID_STYLE = {
	type: "fill",
	paint: {
		"fill-color": "#2c0d9b",
		"fill-opacity": 0.5
	}
} as Pick<LayerSpecification, "type" | "paint">;

const EDGE_STYLE = {
	type: "line",
	paint: {
		"line-color": "#2c0d9b",
		"line-width": 2
	}
} as Pick<LayerSpecification, "type" | "paint">;

const TILE_LAYERS: TileLayer[] = [
	{id: "scored_grids_pmtiles_p5", maxZoom: 8, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p6", maxZoom: 12, style: GRID_STYLE},
	{id: "scored_grids_pmtiles_p7", maxZoom: 14, style: GRID_STYLE},
	{id: "scored_edges_pmtiles_p0", maxZoom: 18, style: EDGE_STYLE}
];
	
function toVectorSource(tileLayer: TileLayer) {
	const sourceId = `${tileLayer.id}-source`;
	const styleId = `${tileLayer.id}-style`;
	const minzoom = TILE_LAYERS.findLast(l => l.maxZoom < tileLayer.maxZoom)?.maxZoom ?? 0;

	const source = {
		type: "vector",
		tiles: [`http://localhost:3001/${tileLayer.id}/{z}/{x}/{y}.pbf`],
		minzoom: minzoom,
		maxzoom: tileLayer.maxZoom
	} as VectorSourceSpecification;

	const layerStyle = {
		id: styleId,
		type: tileLayer.style.type,
		source: sourceId,
		"source-layer": tileLayer.id,
		paint: tileLayer.style.paint,
		minzoom: minzoom,
		maxzoom: tileLayer.maxZoom
	} as LayerSpecification;

	return (
		<Source key={sourceId} id={sourceId} {...source}>
			<Layer {...layerStyle}/>
		</Source>
	);
}

export default function AccessibilityMap() {
	const onZoomEnd = (e: ViewStateChangeEvent) => {
		const zoom = e.target.getZoom();
		console.log(`Zoom: ${zoom}`);
	};
	
	return (
		<Map 
		initialViewState={{
			longitude: 12.5683,
			latitude: 55.6761,
			zoom: 11
		}}
		mapStyle="https://tiles.openfreemap.org/styles/bright"
		maxZoom={18}
		onZoomEnd={onZoomEnd}
		>
			{TILE_LAYERS.map(toVectorSource)}
		</Map>
	);
}
	