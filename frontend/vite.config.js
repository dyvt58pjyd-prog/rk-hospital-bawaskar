import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
  build: {
    outDir: path.resolve(__dirname, '../static/odontogram_bundle'),
    emptyOutDir: true,
    lib: {
      entry: path.resolve(__dirname, 'src/main.jsx'),
      name: 'AdvancedOdontogram',
      formats: ['iife'],
      fileName: () => 'odontogram.bundle.js',
    },
    rollupOptions: {
      // Inline all dependencies (React, react-dom, react-advanced-odontogram) into the single bundle
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'odontogram.bundle.css';
          }
          return assetInfo.name || 'asset-[hash][extname]';
        },
      },
    },
  },
});
