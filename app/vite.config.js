import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import jsconfigPaths from 'vite-jsconfig-paths' // <-- 1. Importa el plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    jsconfigPaths() // <-- 2. Añádelo a la lista de plugins
  ],
})