import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const tileservInternalUrl =
      process.env.TILESERV_INTERNAL_URL ?? "http://localhost:7800";

    return [
      {
        source: "/tiles/:path*",
        destination: `${tileservInternalUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
