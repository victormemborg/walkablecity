"use client";

// IMPORTANT: the order matters!
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";

import { MapContainer, TileLayer } from "react-leaflet";
import Viewport from "./Viewport";
import VectorTileLayer from "./VectorTileLayer";

export default function Map() {

  return (
      <MapContainer
        center={[55.6761, 12.5683]}
        zoom={11}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
        preferCanvas={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <VectorTileLayer 
          url={"http://localhost:7800/public.grid_precision_6/{z}/{x}/{y}.pbf"}
          layerName={"public.grid_precision_6"}
        />
      </MapContainer>
  );
}