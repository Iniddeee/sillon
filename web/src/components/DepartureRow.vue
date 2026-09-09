<script setup lang="ts">
import { computed } from 'vue'
import type { Train } from '@/lib/data'
import { score } from '@/lib/score'

const props = defineProps<{ train: Train; selected: boolean; transferMin: number }>()
defineEmits<{ click: [] }>()

const s = computed(() => score(props.train, props.transferMin))

function time(hhmm: string): string {
  return hhmm.replace(':', '.')
}

function rateLabel(rate: number | null): string {
  return rate === null ? '—' : `${Math.round(rate * 100)} %`
}

const rateColor = computed(() => (s.value.rate !== null && s.value.rate < 0.9 ? '#eb0000' : '#111111'))
</script>

<template>
  <button class="row" :class="{ selected: props.selected }" type="button" @click="$emit('click')">
    <span class="badge">{{ train.line }}</span>
    <span class="time">{{ time(train.planned_dep) }}</span>
    <span v-if="train.line2" class="itinerary">
      <span class="via">→ {{ time(train.via_arr!) }}</span>
      <span class="badge small">{{ train.line2 }}</span>
      <span class="via">{{ time(train.via_dep!) }}</span>
    </span>
    <span v-else class="arr"><span class="arr-label">arrivée </span>{{ time(train.planned_arr) }}</span>
    <span class="rate" :style="{ color: rateColor }">{{ rateLabel(s.rate) }}</span>
  </button>
</template>

<style scoped>
.row {
  display: grid;
  grid-template-columns: 40px 76px minmax(0, 1fr) 72px;
  gap: 10px;
  align-items: baseline;
  width: 100%;
  padding: 9px 6px;
  margin: 0 -6px;
  border: none;
  border-top: 1px solid var(--rule);
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.row.selected,
.row:hover {
  background: var(--row-selected);
}

.badge {
  background: var(--red);
  color: #ffffff;
  font-weight: 700;
  font-size: 11px;
  padding: 3px 0;
  text-align: center;
}

.badge.small {
  padding: 2px 6px;
}

.time {
  font-weight: 700;
  font-size: 20px;
}

.arr,
.itinerary {
  font-size: 12px;
  color: var(--muted);
}

.arr-label {
  color: var(--muted);
}

.itinerary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4em;
  align-items: baseline;
}

.rate {
  font-weight: 700;
  font-size: 20px;
  text-align: right;
}

@media (max-width: 899px) {
  .time,
  .rate {
    font-size: 18px;
  }

  .arr-label {
    display: none;
  }
}
</style>
