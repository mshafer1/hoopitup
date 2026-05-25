import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
app.mount('#app')

// Register Service Worker for PWA capabilities
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('Service Worker registered successfully:', registration)
      })
      .catch(error => {
        console.error('Service Worker registration failed:', error)
      })
  })
}

