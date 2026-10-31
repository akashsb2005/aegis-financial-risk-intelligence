import type { NextConfig } from "next";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    if (!apiBaseUrl) {
      return [];
    }

    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiBaseUrl}/:path*`,
      },
    ];
  },
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
