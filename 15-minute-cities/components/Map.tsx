"use client";

// IMPORTANT: the order matters!
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import hexData from "@/accessibility.json";

import { MapContainer, TileLayer } from "react-leaflet";
import Scatter from "./Scatter";
import Heatmap from "./Heatmap";
import GeohashCells from "./GeohashCell";

export default function Map() {

  return (
      <MapContainer
        center={[55.6761, 12.5683]}
        zoom={11}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeohashCells data={hexData} />
      </MapContainer>
  );
}