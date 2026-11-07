import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: [
    "@chat-adapter/state-memory",
    "@chat-adapter/web",
    "chat",
  ],
};

export default nextConfig;
