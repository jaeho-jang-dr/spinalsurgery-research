/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  transpilePackages: ['react-icons'],
  modularizeImports: {
    'react-icons': {
      transform: 'react-icons/{{member}}',
    },
  },
  experimental: {
    optimizePackageImports: []
  }
}

module.exports = nextConfig