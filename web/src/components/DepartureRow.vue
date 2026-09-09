<script setup lang="ts">
import { computed } from 'vue'
import type { Station, Train } from '@/lib/data'
import { trainDays } from '@/lib/data'
import { score } from '@/lib/score'
import DayStrip from './DayStrip.vue'

const props = defineProps<{ train: Train; selected: boolean; transferMin: number; via: Station | null }>()
defineEmits<{ click: [] }>()

const days = computed(() => trainDays(props.train))
const s = computed(() => score(props.train, props.transferMin))
const whiteBadge = computed(() => props.train.line.startsWith('S'))
const whiteBadge2 = computed(() => props.train.line2?.startsWith('S') ?? false)

function time(hhmm: string): string {
  return hhmm.replace(':', '.')
}

function rateLabel(rate: number | null): string {
  return rate === null ? '—' : `${Math.round(rate * 100)} %`
}
</script>

<template>
  <button class="row" :class="{ selected: props.selected }" type="button" @click="$emit('click')">
    <span v-if="train.line2" class="line itinerary">
      <span class="badge" :class="{ white: whiteBadge }">{{ train.line }}</span>
      <span class="time">{{ time(train.planned_dep) }}</span>
      <span class="arrow">→</span>
      <span class="via">{{ via?.name }} {{ time(train.via_arr!) }}</span>
      <span class="arrow">→</span>
      <span class="badge" :class="{ white: whiteBadge2 }">{{ train.line2 }}</span>
      <span class="time small">{{ time(train.via_dep!) }}</span>
      <span class="arrow">→</span>
      <span class="time">{{ time(train.planned_arr) }}</span>
      <span class="rate" :class="{ warn: s.rate !== null && s.rate < 0.9 }">{{
        rateLabel(s.rate)
      }}</span>
    </span>
    <span v-else class="line">
      <span class="badge" :class="{ white: whiteBadge }">{{ train.line }}</span>
      <span class="time">{{ time(train.planned_dep) }}</span>
      <span class="arrow">→</span>
      <span class="time">{{ time(train.planned_arr) }}</span>
      <span class="rate" :class="{ warn: s.rate !== null && s.rate < 0.9 }">{{
        rateLabel(s.rate)
      }}</span>
    </span>
    <DayStrip class="strip" :days="days" :train="train" :transfer-min="transferMin" :via="via" />
  </button>
</template>

<style scoped>
.row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 0;
  border: none;
  border-top: 1px solid var(--hairline);
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.row:hover,
.row.selected {
  background: rgba(255, 255, 255, 0.08);
}

.line {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.4rem 0.6rem;
}

.badge {
  background: var(--red);
  color: var(--white);
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  line-height: 1;
}

.badge.white {
  background: var(--white);
  color: var(--blue);
}

.time {
  font-weight: 700;
  font-size: 1.3rem;
}

.time.small {
  font-size: 1rem;
  opacity: 0.85;
}

.via {
  font-size: 0.8rem;
  opacity: 0.7;
}

.arrow {
  opacity: 0.7;
}

.rate {
  margin-left: auto;
  font-weight: 700;
  font-size: 1.5rem;
}

.rate.warn {
  color: var(--yellow);
}

.strip {
  width: 100%;
}
</style>
