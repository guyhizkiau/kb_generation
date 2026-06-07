import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  base: '/ghostwriter/',
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8767',
      '/static': 'http://127.0.0.1:8767',
      '/status': 'http://127.0.0.1:8767',
      '/poll-now': 'http://127.0.0.1:8767',
      '/retry': 'http://127.0.0.1:8767',
    },
  },
  build: {
    outDir: '../../dist/ghostwriter',
    emptyOutDir: true,
  },
})
