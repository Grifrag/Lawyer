import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// In production nginx serves /blog/ -> /blog/index.html via try_files;
// mirror that in the dev server so static blog pages work locally too.
function blogIndexFallback() {
  return {
    name: 'blog-index-fallback',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        if (req.url === '/blog' || req.url === '/blog/') {
          req.url = '/blog/index.html'
        }
        next()
      })
    }
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), blogIndexFallback()],
  server: {
    proxy: { '/api': 'http://localhost:5000' }
  }
})
