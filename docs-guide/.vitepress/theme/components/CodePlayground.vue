<template>
  <div class="code-playground">
    <div class="code-playground-header">
      <span class="code-playground-title">{{ title }}</span>
      <button v-if="!live" @click="copyCode" class="copy-button">
        {{ copied ? 'Copied!' : 'Copy' }}
      </button>
    </div>
    <div class="code-playground-body">
      <Sandpack
        v-if="live"
        :template="template"
        :files="files"
        :options="sandpackOptions"
        :theme="isDark ? 'dark' : 'light'"
      />
      <pre v-else><code :class="`language-${language}`" v-html="highlightedCode"></code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Sandpack } from 'sandpack-vue3'
import { useData } from 'vitepress'
import Prism from 'prismjs'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-javascript'

const props = defineProps<{
  title: string
  code: string
  language?: string
  live?: boolean
  template?: 'vanilla' | 'react' | 'vue' | 'node'
}>()

const { isDark } = useData()
const copied = ref(false)

const files = computed(() => {
  if (props.live && props.template === 'node') {
    return {
      '/index.js': {
        code: props.code
      }
    }
  }
  return {
    '/index.html': {
      code: `<!DOCTYPE html>
<html>
<body>
  <div id="app"></div>
  <script>${props.code}</script>
</body>
</html>`
    }
  }
})

const sandpackOptions = {
  showNavigator: false,
  showTabs: false,
  showLineNumbers: true,
  editorHeight: 300
}

const highlightedCode = computed(() => {
  return Prism.highlight(
    props.code,
    Prism.languages[props.language || 'python'],
    props.language || 'python'
  )
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.copy-button {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  background-color: var(--vp-c-brand-1);
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-button:hover {
  background-color: var(--vp-c-brand-2);
}

pre {
  margin: 0;
  padding: 1rem;
  background-color: var(--vp-code-block-bg);
  border-radius: 6px;
  overflow-x: auto;
}

code {
  font-family: var(--vp-font-family-mono);
  font-size: 0.9em;
  line-height: 1.6;
}
</style>
