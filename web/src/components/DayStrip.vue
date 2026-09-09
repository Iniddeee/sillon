<script setup lang="ts">
import { computed } from 'vue'
import type { DayEntry } from '@/lib/data'

const props = defineProps<{ days: DayEntry[] }>()

const SIZE = 10
const GAP = 2
const STEP = SIZE + GAP
const COLS = 30

function fill(day: DayEntry): string {
  if (day.status === 'cancelled') return '#e2231a'
  if (day.status === 'nodata') return 'transparent'
  return (day.arr ?? 0) >= 3 ? '#ffcc00' : '#ffffff'
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function label(day: DayEntry): string {
  const date = formatDate(day.date)
  if (day.status === 'cancelled') return `${date} — supprimé`
  if (day.status === 'nodata') return `${date} — pas de donnée`
  const arr = day.arr ?? 0
  return arr >= 3 ? `${date} — retard ${arr} min` : `${date} — à l'heure`
}

function col(i: number): number {
  return i % COLS
}

function row(i: number): number {
  return Math.floor(i / COLS)
}

const rows = computed(() => Math.max(1, Math.ceil(props.days.length / COLS)))
const viewBox = computed(() => `0 0 ${COLS * STEP - GAP} ${rows.value * STEP - GAP}`)
</script>

<template>
  <svg
    class="strip"
    :viewBox="viewBox"
    role="img"
    :aria-label="`Historique sur ${props.days.length} jours`"
  >
    <rect
      v-for="(day, i) in props.days"
      :key="day.date"
      :x="col(i) * STEP"
      :y="row(i) * STEP"
      :width="SIZE"
      :height="SIZE"
      :fill="fill(day)"
      :stroke="day.status === 'nodata' ? 'rgba(255,255,255,.5)' : 'none'"
      :data-status="day.status"
    >
      <title>{{ label(day) }}</title>
    </rect>
  </svg>
</template>

<style scoped>
.strip {
  display: block;
  width: 100%;
  max-width: 30rem;
  height: auto;
}
</style>
