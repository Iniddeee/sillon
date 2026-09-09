<script setup lang="ts">
import { computed } from 'vue'
import type { DayEntry, Station, Train } from '@/lib/data'
import { missed } from '@/lib/score'

const props = defineProps<{
  days: DayEntry[]
  train?: Train
  transferMin?: number
  via?: Station | null
}>()

const SIZE = 10
const GAP = 2
const STEP = SIZE + GAP
const COLS = 30

function isMissed(day: DayEntry): boolean {
  return props.train !== undefined && missed(props.train, day, props.transferMin ?? 0)
}

function fill(day: DayEntry): string {
  if (day.status === 'cancelled') return '#e2231a'
  if (day.status === 'nodata') return 'transparent'
  if (isMissed(day)) return '#ffcc00'
  return (day.arr ?? 0) >= 3 ? '#ffcc00' : '#ffffff'
}

function stroke(day: DayEntry): string {
  if (isMissed(day)) return '#e2231a'
  if (day.status === 'nodata') return 'rgba(255,255,255,.5)'
  return 'none'
}

function strokeWidth(day: DayEntry): number {
  return isMissed(day) ? 2 : 1
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function label(day: DayEntry): string {
  const date = formatDate(day.date)
  if (day.status === 'cancelled') return `${date} — supprimé`
  if (day.status === 'nodata') return `${date} — pas de donnée`
  if (isMissed(day)) {
    const by = day.legs?.[0].arr ?? 0
    const at = props.via?.name ?? 'la correspondance'
    return `${date} — correspondance ratée (+${by} min à ${at})`
  }
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
      :stroke="stroke(day)"
      :stroke-width="strokeWidth(day)"
      :data-status="day.status"
      :data-missed="isMissed(day)"
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
