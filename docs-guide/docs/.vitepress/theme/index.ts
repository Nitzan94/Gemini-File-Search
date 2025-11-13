import DefaultTheme from 'vitepress/theme'
import './styles/index.css'
import './styles/rtl.css'

import InteractiveDiagram from './components/InteractiveDiagram.vue'
import VideoPlayer from './components/VideoPlayer.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // Register global components
    app.component('InteractiveDiagram', InteractiveDiagram)
    app.component('VideoPlayer', VideoPlayer)
  }
}
