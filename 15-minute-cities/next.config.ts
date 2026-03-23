import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // don't rewrite in prod as we want to serve the tiles directly from nginx
    if (process.env.NODE_ENV === "production") {
      return [];
    }

    const destination =
      process.env.MARTIN_URL ?? "http://localhost:3001";

    return [
      {
        source: "/tiles/:path*",
        destination: `${destination}/:path*`,
      },
    ];
  },
};

export default nextConfig;
