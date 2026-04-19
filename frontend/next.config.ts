import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configure for static export to serve from FastAPI
  output: "export",
  // Disable dynamic routes for static export (all routes must be pre-renderable)
  trailingSlash: true,
};

export default nextConfig;
