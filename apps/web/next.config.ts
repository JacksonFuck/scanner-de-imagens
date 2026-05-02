import type { NextConfig } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const config: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_BASE}/api/:path*` },
      { source: "/ws/:path*", destination: `${API_BASE}/ws/:path*` },
    ];
  },
};

export default config;
