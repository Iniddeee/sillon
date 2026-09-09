<script setup lang="ts">
import type { Day, Station, Train } from '@/lib/data'
import { missed } from '@/lib/score'

const props = defineProps<{
  days: string[]
  train: Train
  transferMin?: number
  via?: Station | null
}>()

function dayOf(date: string): Day | undefined {
  return props.train.days[date]
}

function isMissed(date: string): boolean {
  const day = dayOf(date)
  return day !== undefined && missed(props.train, day, props.transferMin ?? 0)
}

function fill(date: string): string {
  const day = dayOf(date)
  if (day === undefined) return 'transparent'
  if (day.status === 'cancelled') return '#eb0000'
  if (day.status === 'nodata') return 'transparent'
  if (isMissed(date)) return '#f0b400'
  return (day.arr ?? 0) >= 3 ? '#f0b400' : '#111111'
}

function outlined(date: string): boolean {
  const day = dayOf(date)
  return day !== undefined && (day.status === 'nodata' || isMissed(date))
}

function borderColor(date: string): string {
  return isMissed(date) ? '#eb0000' : '#111111'
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function label(date: string): string {
  const day = dayOf(date)
  const formatted = formatDate(date)
  if (day === undefined) return 'pas de train ce jour'
  if (day.status === 'cancelled') return `${formatted} — supprimé`
  if (day.status === 'nodata') return `${formatted} — pas de donnée`
  if (isMissed(date)) {
    const by = day.legs?.[0].arr ?? 0
    const at = props.via?.name ?? 'la correspondance'
    return `${formatted} — correspondance ratée (+${by} min à ${at})`
  }
  const arr = day.arr ?? 0
  return arr >= 3 ? `${formatted} — retard ${arr} min` : `${formatted} — à l'heure`
}
</script>

<template>
  <div class="strip" role="img" :aria-label="`Historique sur ${props.days.length} jours`">
    <div
      v-for="date in props.days"
      :key="date"
      class="cell"
      :class="{ outlined: outlined(date) }"
      :style="{
        background: fill(date),
        borderColor: outlined(date) ? borderColor(date) : 'transparent',
      }"
      :title="label(date)"
      :data-status="dayOf(date)?.status ?? 'none'"
      :data-missed="isMissed(date)"
    >
      <span v-if="dayOf(date) === undefined" class="dot" />
    </div>
  </div>
</template>

<style scoped>
.strip {
  display: grid;
  grid-template-columns: repeat(25, 14px);
  gap: 4px;
  width: fit-content;
}

.cell {
  width: 14px;
  height: 14px;
  box-sizing: border-box;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #c9c6bc;
}

@media (max-width: 899px) {
  .strip {
    grid-template-columns: repeat(25, 10px);
  }

  .cell {
    width: 10px;
    height: 10px;
  }
}
</style>
