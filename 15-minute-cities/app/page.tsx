"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap";
import ColorButton from "@/components/ColorButton";
import { Suspense, useState } from "react";
import { parseMapView } from "@/utils/queryParams";

function Map() {
  const searchParams = useSearchParams();
	const [colorBlindMode, setColorBlindMode] = useState(false);
	const mapView = parseMapView(searchParams);

	return (
		<>
			<ColorButton
				colorBlindMode={colorBlindMode}
				onToggle={() => setColorBlindMode((current) => !current)}
			/>
			<AccessibilityMap {...mapView} colorBlindMode={colorBlindMode} />
		</>
	);
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