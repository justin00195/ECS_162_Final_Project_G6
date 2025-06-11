import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [svelte()],
  test: {
    globals: true,
    environment: 'jsdom', 
    setupFiles: ['./src/setupTests.ts'],
  },
  //reference for debugging fix https://github.com/sveltejs/svelte/issues/11394
  resolve: mode === 'test' ? {
    conditions: ['browser'],
  } : {},
  server: mode === 'development' ? {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying request:', req.url)
          })
        }
      },
    },
  } : undefined,
}))