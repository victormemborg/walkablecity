"use client";

import dynamic from "next/dynamic";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

const LazyMap = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => <p>Loading...</p>,
});

// defaults to copenhagen if no query params are provided
function Map() {
  const searchParams = useSearchParams();
  const lat = parseFloat(searchParams.get("lat") ?? "55.6761");
  const lon = parseFloat(searchParams.get("lon") ?? "12.5683");
  const zoom = parseInt(searchParams.get("zoom") ?? "11");

  return <LazyMap center={[lat, lon]} zoom={zoom} />;
}

// NOTE: Suspense is required, otherwise we can't build the app. 
export default function Home() {
  return (
    <main style={{ height: "100vh", margin: 0 }}>
      <Suspense fallback={<p>Loading...</p>}> 
        <Map />
      </Suspense>
    </main>
  );
}