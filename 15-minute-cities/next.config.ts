import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const destination =
      process.env.TILESERV_INTERNAL_URL ?? "http://localhost:7800";

    return [
      {
        source: "/tiles/:path*",
        destination: `${destination}/:path*`,
      },
    ];
  },
};

export default nextConfig;
