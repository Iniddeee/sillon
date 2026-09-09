<script setup lang="ts">
import { computed } from 'vue'
import { handAngles } from '@/lib/clock'

const props = defineProps<{ hh: number; mm: number; size: number }>()

const CX = 250
const CY = 250

const ticks = Array.from({ length: 60 }, (_, i) => {
  const a = ((i * 6 - 90) * Math.PI) / 180
  const hour = i % 5 === 0
  const [r1, r2, w] = hour ? [188, 222, 8] : [208, 222, 3]
  return {
    x1: CX + r1 * Math.cos(a),
    y1: CY + r1 * Math.sin(a),
    x2: CX + r2 * Math.cos(a),
    y2: CY + r2 * Math.sin(a),
    w,
  }
})

const angles = computed(() => handAngles(props.hh, props.mm))
</script>

<template>
  <svg
    class="clock"
    :width="size"
    :height="size"
    viewBox="0 0 500 500"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="`${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`"
  >
    <circle :cx="CX" :cy="CY" r="236" fill="#ffffff" stroke="#d9d7d0" stroke-width="2" />
    <line
      v-for="(t, i) in ticks"
      :key="i"
      :x1="t.x1"
      :y1="t.y1"
      :x2="t.x2"
      :y2="t.y2"
      stroke="#111111"
      :stroke-width="t.w"
    />
    <line
      class="hand"
      x1="250"
      y1="284"
      x2="250"
      y2="114"
      stroke="#111111"
      stroke-width="18"
      :style="{ transform: `rotate(${angles.hour}deg)` }"
    />
    <line
      class="hand"
      x1="250"
      y1="290"
      x2="250"
      y2="50"
      stroke="#111111"
      stroke-width="13"
      :style="{ transform: `rotate(${angles.minute}deg)` }"
    />
    <line x1="250" y1="294" x2="250" y2="82" stroke="#eb0000" stroke-width="6" />
    <circle cx="250" cy="82" r="17" fill="#eb0000" />
    <circle :cx="CX" :cy="CY" r="8" fill="#111111" />
  </svg>
</template>

<style scoped>
.clock {
  display: block;
  width: 100%;
  height: auto;
}

.hand {
  transform-origin: 250px 250px;
  transition: transform 400ms;
}
</style>
