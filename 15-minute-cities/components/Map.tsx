"use client";

// IMPORTANT: the order matters!
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";

import { MapContainer, TileLayer } from "react-leaflet";
import AccessibilityLayer from "./AccessibilityLayer";

export default function Map({ center, zoom }: { center: [number, number]; zoom: number }) {
  const baseTileUrl = "/tiles/";

  return (
      <MapContainer
        center={center}
        zoom={zoom}
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
          initialZoom={zoom}
        />
      </MapContainer>
  );
}