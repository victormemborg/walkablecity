import { VectorSourceSpecification, FillLayerSpecification } from "maplibre-gl";
import { Source, Layer } from "react-map-gl/maplibre";

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