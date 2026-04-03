"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap";
import { Suspense } from "react";
import { parseMapView } from "@/types/queryParams";

function Map() {
  const searchParams = useSearchParams();
	const mapView = parseMapView(searchParams);

	return <AccessibilityMap {...mapView} />;
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