import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import i18nextLoader from 'vite-plugin-i18next-loader'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    i18nextLoader({
      paths: ['./src/locales'],
      logLevel: 'debug'
    })
  ],
  server: {
    host: true,
    allowedHosts: ['newdevit.fundacionctic.org'],
    watch: {
      usePolling: true
    },
  }
})
