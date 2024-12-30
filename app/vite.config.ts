import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: [
      {
        find: '@',
        replacement: path.resolve(__dirname, 'src')
      },
      {
        find: '_c',
        replacement: path.resolve(__dirname, 'components')
      },
      {
        find: '_conf',
        replacement: path.resolve(__dirname, 'config')
      },
    ]
  },
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    // connect to a remote backend during web-only development
    proxy: {
      '/api': {
        target: "http://localhost:8000/",
        secure: false,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        ws: true,
      },
    },
  },
})
