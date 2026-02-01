import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [react(), svgr()],
  base: '/fractal-notebooks/react/',
  server: {
    port: 33000,
    open: true,
  },
  build: {
    outDir: 'build',
  },
  resolve: {
    alias: {
      // Add any path aliases here if needed
    },
  },
});
