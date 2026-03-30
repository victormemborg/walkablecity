"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap"
import { Suspense } from "react";

function Map() {
  const searchParams = useSearchParams();

  const lat = parseFloat(searchParams.get("lat") ?? "55.6761");
  const lon = parseFloat(searchParams.get("lon") ?? "12.5683");
  const zoom = parseInt(searchParams.get("zoom") ?? "11");

  const map = { center: { lat, lon }, zoom };

  return <AccessibilityMap {...map} />;
}

export default function Home() {
	return (
		<main style={{ height: "100vh", margin: 0 }}>
		<Suspense fallback={<div>Loading map...</div>}>
			<Map />
		</Suspense>
		</main>
	);
}