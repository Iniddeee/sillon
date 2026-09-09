<script setup lang="ts">
import type { Pair } from '@/lib/data'

defineProps<{ pairs: Pair[]; modelValue: string }>()
defineEmits<{ 'update:modelValue': [id: string] }>()
</script>

<template>
  <label class="picker">
    <select
      class="select"
      :value="modelValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="pair in pairs" :key="pair.id" :value="pair.id">
        {{ pair.from.name }} → {{ pair.to.name }}
      </option>
    </select>
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M3 6l5 5 5-5" />
    </svg>
  </label>
</template>

<style scoped>
.picker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--ink);
  cursor: pointer;
}

.select {
  appearance: none;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  padding: 0;
  cursor: pointer;
}

@media (max-width: 899px) {
  .picker {
    font-size: 14px;
  }
}
</style>
