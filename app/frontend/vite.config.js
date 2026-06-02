
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { VitePWA } from 'vite-plugin-pwa';
import pkg from './package.json' assert { type: 'json' }

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icon-192x192.png', 'icon-512x512.png'],
      manifest: {
        name: 'Hoop It Up',
        short_name: 'Hoop It Up',
        description: 'A PWA for coordinating basketball games with yes/no/maybe voting',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        orientation: 'portrait-primary',
        theme_color: '#667eea',
        background_color: '#ffffff',
        icons: [
          {
            src: '/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          }
        ],
        categories: ['sports', 'lifestyle'],
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173
  },
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version)
  }
});
