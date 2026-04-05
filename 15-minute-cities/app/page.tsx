"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap";
import ColorButton from "@/components/ColorButton";
import { Suspense, useState } from "react";
import { parseMapView } from "@/utils/queryParams";
import type { ScoreRange } from "@/types/mapTypes";

function Map() {
  const searchParams = useSearchParams();
	const [colorBlindMode, setColorBlindMode] = useState(false);
	const [scoreRange, setScoreRange] = useState<ScoreRange | null>(null);
	const mapView = parseMapView(searchParams);

	return (
		<>
			<ColorButton
				colorBlindMode={colorBlindMode}
				currentRange={scoreRange}
				onToggle={() => setColorBlindMode((current) => !current)}
			/>
			<AccessibilityMap {...mapView} colorBlindMode={colorBlindMode} onScoreRangeChange={setScoreRange} />
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