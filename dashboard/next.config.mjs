/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output mode for Docker
  output: 'standalone',

  // Settings from your old .mjs file
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  devIndicators: {
    buildActivity: false,
  },

  // Settings from your old .js file
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: true,
      },
    ]
  },
}

export default nextConfig