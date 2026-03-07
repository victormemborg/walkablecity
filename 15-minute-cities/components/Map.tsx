"use client";

// IMPORTANT: the order matters!
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";

import { MapContainer, TileLayer } from "react-leaflet";
import AccessibilityLayer from "./AccessibilityLayer";

export default function Map() {
  const initialZoom = 11;
  const baseTileUrl = process.env.NEXT_PUBLIC_TILESERV_URL ?? "http://localhost:7800/"; // default if not specificed

  return (
      <MapContainer
        center={[55.6761, 12.5683]}
        zoom={initialZoom}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
        preferCanvas={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <AccessibilityLayer 
          baseTileUrl={baseTileUrl}
          initialZoom={initialZoom}
        />
      </MapContainer>
  );
}