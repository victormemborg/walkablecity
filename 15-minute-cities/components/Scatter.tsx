import { GeoJSON } from "react-leaflet";
import React from "react";
import L from "leaflet";

interface ScatterProps {
  data: any; // data from geojson
}

const SCORE_COLORS: Record<number, string> = {
  5: "#fde725",
  4: "#5ec962", 
  3: "#21918c", 
  2: "#3b528b", 
  1: "#440154", 
  0: "#1d0024",
};

function getColor(score: number): string {
  return SCORE_COLORS[score] || "#ff0000"; // if score is out of range (no data), return red
}

// Called on each point feature.
function makeCircle(feature: any, latlng: L.LatLng): L.CircleMarker {
  const score = feature.properties?.access_score ?? 0;

  return L.circleMarker(latlng, {
    radius: 6,
    fillColor: getColor(score),
    fillOpacity: 0.7,
    color: "white",   // border color
    weight: 0.5,      // border width
    opacity: 1,       // border opacity
  });
}


function addPopup(feature: any, layer: L.Layer): void {
  const score = feature.properties?.access_score;
  const label = score != null ? score : "N/A";
    layer.bindPopup(`Accessibility score: ${label}`);
}

const Scatter: React.FC<ScatterProps> = ({ data }) => {
  return (
    <GeoJSON
      data={data}
      pointToLayer={makeCircle}
      onEachFeature={addPopup}
    />
  );
};

export default Scatter;