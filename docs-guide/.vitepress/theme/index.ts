import DefaultTheme from 'vitepress/theme'
import './styles/index.css'
import './styles/rtl.css'

import CodePlayground from './components/CodePlayground.vue'
import InteractiveDiagram from './components/InteractiveDiagram.vue'
import TutorialWizard from './components/TutorialWizard.vue'
import VideoPlayer from './components/VideoPlayer.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // Register global components
    app.component('CodePlayground', CodePlayground)
    app.component('InteractiveDiagram', InteractiveDiagram)
    app.component('TutorialWizard', TutorialWizard)
    app.component('VideoPlayer', VideoPlayer)
  }
}
