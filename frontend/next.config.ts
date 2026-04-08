import type { NextConfig } from "next";

/** Used when building on Vercel Production if `NEXT_PUBLIC_API_URL` is not set there. Preview often has the var; Production is easy to miss in the dashboard. */
const DEFAULT_PRODUCTION_API_URL = "https://kubewise.onrender.com/api/v1";

const nextConfig: NextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.VERCEL_ENV === "production"
        ? DEFAULT_PRODUCTION_API_URL
        : ""),
  },
};

export default nextConfig;
