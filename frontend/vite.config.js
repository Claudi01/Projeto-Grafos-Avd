import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    // Isso cria a variável fantasma que o Plotly precisa para funcionar!
    'process.env': {}
  }
})