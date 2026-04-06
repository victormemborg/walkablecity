"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap";
import ColorButton from "@/components/ColorButton";
import LegendCard from "@/components/LegendCard";
import { Suspense, useState } from "react";
import { parseMapView } from "@/utils/queryParams";
import type { ScoreRange } from "@/types/mapTypes";
import { Box, Stack } from "@mui/material";

function Map() {
  const searchParams = useSearchParams();
	const [colorBlindMode, setColorBlindMode] = useState(false);
	const [scoreRange, setScoreRange] = useState<ScoreRange | null>(null);
	const mapView = parseMapView(searchParams);

	return (
		<>
			<Box sx={{ position: "absolute", top: 16, right: 16, zIndex: 10 }}>
				<Stack spacing={1.5}>
					<LegendCard colorBlindMode={colorBlindMode} currentRange={scoreRange} />
					<ColorButton colorBlindMode={colorBlindMode} onToggle={() => setColorBlindMode((current) => !current)} />
				</Stack>
			</Box>
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