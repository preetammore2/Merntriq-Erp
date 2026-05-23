import type { NextConfig } from "next";

const isCapacitorBuild = process.env.CAPACITOR_BUILD === "true";

const nextConfig: NextConfig = {
  typedRoutes: true,
  ...(isCapacitorBuild
    ? {
        output: "export" as const,
        images: {
          unoptimized: true
        }
      }
    : {})
};

export default nextConfig;
