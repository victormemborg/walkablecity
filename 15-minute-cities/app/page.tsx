"use client";

import { useSearchParams } from "next/navigation";
import AccessibilityMap from "@/components/AccessibilityMap"

export default function Home() {
	const searchParams = useSearchParams();
	const lat = parseFloat(searchParams.get("lat") ?? "55.6761");
	const lon = parseFloat(searchParams.get("lon") ?? "12.5683");
	const zoom = parseInt(searchParams.get("zoom") ?? "11");

	const map = { center: {lat: lat, lon: lon}, zoom: zoom }

	return (
		<main style={{ height: "100vh", margin: 0 }}>
			<AccessibilityMap {...map}/>
		</main>
	);
}