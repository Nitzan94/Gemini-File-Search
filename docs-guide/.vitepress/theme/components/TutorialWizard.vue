<template>
  <div class="tutorial-wizard">
    <div class="wizard-progress">
      <div class="wizard-steps">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="wizard-step"
          :class="{
            'step-active': index === currentStep,
            'step-completed': index < currentStep
          }"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-label">{{ step.title }}</div>
        </div>
      </div>
      <div class="wizard-progress-bar">
        <div
          class="wizard-progress-fill"
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>
    </div>

    <div class="wizard-content">
      <transition name="fade" mode="out-in">
        <div :key="currentStep" class="step-content">
          <h3>{{ steps[currentStep].title }}</h3>
          <div v-html="steps[currentStep].content"></div>

          <CodePlayground
            v-if="steps[currentStep].code"
            :title="steps[currentStep].codeTitle || 'Example'"
            :code="steps[currentStep].code"
            :language="steps[currentStep].language || 'python'"
            :live="steps[currentStep].live || false"
          />

          <div v-if="steps[currentStep].task" class="step-task">
            <h4>✓ Your Task:</h4>
            <p>{{ steps[currentStep].task }}</p>
            <label class="task-checkbox">
              <input
                type="checkbox"
                v-model="completedTasks[currentStep]"
              />
              <span>I've completed this step</span>
            </label>
          </div>
        </div>
      </transition>
    </div>

    <div class="wizard-navigation">
      <button
        class="wizard-button wizard-button-secondary"
        @click="previousStep"
        :disabled="currentStep === 0"
      >
        ← Previous
      </button>
      <div class="step-indicator">
        Step {{ currentStep + 1 }} of {{ steps.length }}
      </div>
      <button
        v-if="currentStep < steps.length - 1"
        class="wizard-button wizard-button-primary"
        @click="nextStep"
        :disabled="requireCompletion && !completedTasks[currentStep]"
      >
        Next →
      </button>
      <button
        v-else
        class="wizard-button wizard-button-primary"
        @click="finish"
      >
        Finish 🎉
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CodePlayground from './CodePlayground.vue'

interface TutorialStep {
  title: string
  content: string
  code?: string
  codeTitle?: string
  language?: string
  live?: boolean
  task?: string
}

const props = withDefaults(defineProps<{
  steps: TutorialStep[]
  requireCompletion?: boolean
}>(), {
  requireCompletion: false
})

const emit = defineEmits(['finish'])

const currentStep = ref(0)
const completedTasks = ref<Record<number, boolean>>({})

const progressPercentage = computed(() => {
  return ((currentStep.value + 1) / props.steps.length) * 100
})

const nextStep = () => {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
    scrollToTop()
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    scrollToTop()
  }
}

const finish = () => {
  emit('finish')
  // Show completion message or redirect
  alert('Congratulations! You\'ve completed the tutorial! 🎉')
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.wizard-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.wizard-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 0.5rem;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--vp-c-bg);
  border: 2px solid var(--vp-c-divider);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step-active .step-number {
  background-color: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  transform: scale(1.1);
}

.step-completed .step-number {
  background-color: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.step-label {
  font-size: 0.85rem;
  text-align: center;
  color: var(--vp-c-text-2);
  transition: color 0.3s ease;
}

.step-active .step-label {
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

.step-content h3 {
  margin-top: 0;
  color: var(--vp-c-brand-1);
}

.step-task {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: var(--vp-c-brand-soft);
  border-radius: 8px;
  border-left: 4px solid var(--vp-c-brand-1);
}

.step-task h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: var(--vp-c-brand-1);
}

.task-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  cursor: pointer;
  user-select: none;
}

.task-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.step-indicator {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 500;
}

@media (max-width: 768px) {
  .wizard-steps {
    flex-wrap: wrap;
  }

  .step-label {
    font-size: 0.75rem;
  }

  .step-number {
    width: 30px;
    height: 30px;
    font-size: 0.85rem;
  }
}
</style>
