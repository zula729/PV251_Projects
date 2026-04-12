import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import ViteYaml from '@modyfi/vite-plugin-yaml'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), ViteYaml()],
})
