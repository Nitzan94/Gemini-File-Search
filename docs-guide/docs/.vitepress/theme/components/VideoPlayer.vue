<template>
  <div class="video-player">
    <video
      v-if="type === 'mp4'"
      :src="src"
      :poster="poster"
      controls
      :autoplay="autoplay"
      :loop="loop"
      :muted="muted"
    >
      Your browser does not support the video tag.
    </video>
    <img
      v-else-if="type === 'gif'"
      :src="src"
      :alt="caption || 'Demo animation'"
    />
    <div v-if="caption" class="video-player-caption">
      {{ caption }}
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  src: string
  type?: 'mp4' | 'gif'
  caption?: string
  poster?: string
  autoplay?: boolean
  loop?: boolean
  muted?: boolean
}>(), {
  type: 'mp4',
  autoplay: false,
  loop: false,
  muted: false
})
</script>

<style scoped>
/* Styles already defined in main CSS */
</style>
