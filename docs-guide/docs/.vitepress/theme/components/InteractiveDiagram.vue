<template>
  <div class="interactive-diagram">
    <div v-if="title" class="diagram-title">{{ title }}</div>
    <div ref="diagramEl" class="diagram-content"></div>
    <div v-if="description" class="diagram-description">{{ description }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'
import { useData } from 'vitepress'

const props = defineProps<{
  title?: string
  description?: string
  chart: string
}>()

const { isDark } = useData()
const diagramEl = ref<HTMLElement>()

// Initialize mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: isDark.value ? 'dark' : 'default',
  securityLevel: 'loose',
  fontFamily: 'inherit'
})

// Render diagram
const renderDiagram = async () => {
  if (!diagramEl.value) return

  try {
    // Clear previous content
    diagramEl.value.innerHTML = ''

    // Generate unique ID
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`

    // Render mermaid diagram
    const { svg } = await mermaid.render(id, props.chart)

    // Insert SVG
    diagramEl.value.innerHTML = svg

    // Make diagram interactive - add click handlers
    const svgElement = diagramEl.value.querySelector('svg')
    if (svgElement) {
      svgElement.style.maxWidth = '100%'
      svgElement.style.height = 'auto'

      // Add hover effects to nodes
      const nodes = svgElement.querySelectorAll('.node, .edgeLabel')
      nodes.forEach((node) => {
        node.addEventListener('mouseenter', () => {
          node.style.cursor = 'pointer'
          node.style.opacity = '0.8'
        })
        node.addEventListener('mouseleave', () => {
          node.style.opacity = '1'
        })
      })
    }
  } catch (error) {
    console.error('Failed to render diagram:', error)
    diagramEl.value.innerHTML = '<p style="color: red;">Failed to render diagram</p>'
  }
}

// Re-render on theme change
watch(isDark, () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: isDark.value ? 'dark' : 'default',
    securityLevel: 'loose',
    fontFamily: 'inherit'
  })
  renderDiagram()
})

onMounted(() => {
  renderDiagram()
})
</script>

<style scoped>
.diagram-title {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--vp-c-brand-1);
}

.diagram-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.diagram-description {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  line-height: 1.6;
}

/* Mermaid overrides */
.diagram-content :deep(.node rect),
.diagram-content :deep(.node circle),
.diagram-content :deep(.node ellipse),
.diagram-content :deep(.node polygon) {
  transition: all 0.2s ease;
}

.diagram-content :deep(.node:hover rect),
.diagram-content :deep(.node:hover circle),
.diagram-content :deep(.node:hover ellipse),
.diagram-content :deep(.node:hover polygon) {
  filter: brightness(1.1);
}
</style>
