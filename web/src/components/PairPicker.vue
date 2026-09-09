<script setup lang="ts">
import type { Pair } from '@/lib/data'

defineProps<{ pairs: Pair[]; modelValue: string }>()
defineEmits<{ 'update:modelValue': [id: string] }>()
</script>

<template>
  <span class="picker-wrap">
    <select
      class="picker"
      :value="modelValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="pair in pairs" :key="pair.id" :value="pair.id">
        {{ pair.from.name }} → {{ pair.to.name }}
      </option>
    </select>
    <span class="chevron" aria-hidden="true">▾</span>
  </span>
</template>

<style scoped>
.picker-wrap {
  position: relative;
  display: inline-block;
  width: 100%;
  max-width: 24rem;
}

.picker {
  appearance: none;
  border: none;
  border-bottom: 2px solid var(--white);
  background: transparent;
  color: var(--white);
  font: inherit;
  font-weight: 700;
  font-size: 1.15rem;
  padding: 0.5rem 1.5rem 0.5rem 0;
  width: 100%;
}

.chevron {
  position: absolute;
  right: 0;
  bottom: 0.55rem;
  font-size: 0.9rem;
  pointer-events: none;
}
</style>
