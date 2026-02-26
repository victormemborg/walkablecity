import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import ngeohash from "ngeohash";

const GRADIENT: Record<number, string> = {
  0.0:  "#1d0024",
  0.08: "#440154",
  0.20: "#3b528b",
  0.38: "#21918c",
  0.65: "#5ec962",
  1.0:  "#fde725",
};

const stops = Object.keys(GRADIENT).map(Number);

function getNearestGradientColor(value: number): string {
  const nearest = stops.reduce((prev, curr) =>
    Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev
  );
  return GRADIENT[nearest];
}

export default function GeohashCells({ data }: { data: any }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    const layerGroup = L.layerGroup();
    const renderer = L.canvas({ padding: 0.5 });
    const geohashes = data.features.map((f: any) => f.properties.hash)
    const scores = data.features.map((f: any) => f.properties.score)

    for (let i = 0; i < geohashes.length; i++) {
      const [minLat, minLng, maxLat, maxLng] = ngeohash.decode_bbox(geohashes[i]);

      const rect = L.rectangle(
        [
          [minLat, minLng],
          [maxLat, maxLng],
        ],
        {
          renderer,
          color: getNearestGradientColor(scores[i]/5),
          weight: 1,
          fillOpacity: 0.15,
          interactive: false, // IMPORTANT for performance
        }
      );

      layerGroup.addLayer(rect);
    }

    layerGroup.addTo(map);

    return () => {
      map.removeLayer(layerGroup);
    };
  }, [data, map]);

  return null;
}