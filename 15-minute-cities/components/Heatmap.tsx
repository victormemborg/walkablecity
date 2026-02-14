import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";

const GRADIENT = {
  0.0: "#1d0024",
  0.2: "#440154",
  0.4: "#3b528b",
  0.6: "#21918c",
  0.8: "#5ec962",
  1.0: "#fde725",
};

export default function Heatmap({ data }: { data: any }) {
  const map = useMap();

  useEffect(() => {
    if (!data?.features) return;

    const points = data.features
      .filter((f: any) => f.geometry?.type === "Point")
      .map((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        return [lat, lng, (f.properties?.access_score ?? 0) / 5];
      });

    const heat = L.heatLayer(points, {
      radius: 15,
      blur: 15,
      maxZoom: 17,
      max: 1.0,
      gradient: GRADIENT,
    }).addTo(map);

    return () => { map.removeLayer(heat); };
  }, [data, map]);

  return null; 
}