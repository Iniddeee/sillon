import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// Serves web/dev-data/ under /sillon/data/* in dev only; prod copies the `data` branch
// into dist/data instead (pages.yml), this plugin never touches the build.
function devData(): Plugin {
  const root = fileURLToPath(new URL('./dev-data', import.meta.url))
  return {
    name: 'sillon-dev-data',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/sillon/data', (req, res, next) => {
        const file = path.join(root, (req.url ?? '').split('?')[0]!)
        if (!existsSync(file)) return next()
        res.setHeader('Content-Type', 'application/json')
        res.end(readFileSync(file))
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  base: '/sillon/',
  plugins: [
    vue(),
    vueDevTools(),
    devData(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
