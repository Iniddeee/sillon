<script setup lang="ts">
import { computed } from 'vue'
import type { Train } from '@/lib/data'
import { trainDays } from '@/lib/data'
import { score } from '@/lib/score'
import { neighbours, verdict } from '@/lib/neighbours'

const props = defineProps<{ train: Train; trains: Train[] }>()
defineEmits<{ select: [train: Train] }>()

const s = computed(() => score(props.train))
const lateDays = computed(() =>
  trainDays(props.train).filter((d) => d.status === 'real' && (d.arr ?? 0) >= 3),
)

const ranked = computed(() => neighbours(props.trains, props.train))
const nearby = computed(() => ranked.value.slice(0, 3))
const verdictText = computed(() => verdict(props.train, ranked.value))

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function rateLabel(rate: number | null): string {
  return rate === null ? '—' : `${Math.round(rate * 100)} %`
}
</script>

<template>
  <section class="detail">
    <h2>{{ train.line }} {{ train.planned_dep.replace(':', '.') }}</h2>
    <dl class="stats">
      <div>
        <dt>Retard typique</dt>
        <dd>{{ s.median !== null ? `${s.median} min` : '—' }}</dd>
      </div>
      <div>
        <dt>9 fois sur 10</dt>
        <dd>{{ s.p90 !== null ? `≤ ${s.p90} min` : '—' }}</dd>
      </div>
      <div>
        <dt>Supprimé</dt>
        <dd>{{ s.cancelled }} jour{{ s.cancelled === 1 ? '' : 's' }}</dd>
      </div>
      <div>
        <dt>Pas de donnée</dt>
        <dd>{{ s.noData }} jour{{ s.noData === 1 ? '' : 's' }}</dd>
      </div>
    </dl>

    <div class="neighbours">
      <h3>Départs voisins</h3>
      <p class="verdict">{{ verdictText }}</p>
      <button
        v-for="n in nearby"
        :key="n.train.key"
        class="neighbour"
        type="button"
        @click="$emit('select', n.train)"
      >
        <span class="badge" :class="{ white: n.train.line.startsWith('S') }">{{
          n.train.line
        }}</span>
        <span class="time">{{ n.train.planned_dep.replace(':', '.') }}</span>
        <span class="rate" :class="{ warn: n.score.rate !== null && n.score.rate < 0.9 }">{{
          rateLabel(n.score.rate)
        }}</span>
      </button>
    </div>

    <ul v-if="lateDays.length" class="late">
      <li v-for="d in lateDays" :key="d.date">{{ formatDate(d.date) }} — retard {{ d.arr }} min</li>
    </ul>
    <p v-else class="late-empty">Aucun retard mesuré sur la fenêtre.</p>

  </section>
</template>

<style scoped>
.detail {
  border-top: 1px solid var(--hairline);
  padding-top: 1rem;
  margin-top: 1rem;
}

h2 {
  font-size: 1.1rem;
  margin: 0 0 0.75rem;
}

.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin: 0 0 1rem;
}

.stats dt {
  font-size: 0.75rem;
  opacity: 0.75;
}

.stats dd {
  margin: 0;
  font-weight: 700;
  font-size: 1.1rem;
}

.late {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.9rem;
}

.late li {
  padding: 0.25rem 0;
  border-top: 1px solid var(--hairline);
}

.late-empty {
  font-size: 0.9rem;
  opacity: 0.75;
}

.neighbours {
  border-top: 1px solid var(--hairline);
  padding-top: 1rem;
  margin-top: 1rem;
}

.neighbours h3 {
  font-size: 0.75rem;
  margin: 0 0 0.5rem;
  opacity: 0.75;
  font-weight: 400;
}

.verdict {
  margin: 0 0 0.5rem;
  font-weight: 700;
}

.neighbour {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.4rem 0.6rem;
  width: 100%;
  padding: 0.5rem 0;
  border: none;
  border-top: 1px solid var(--hairline);
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.neighbour:hover {
  background: rgba(255, 255, 255, 0.08);
}

.neighbour .badge {
  background: var(--red);
  color: var(--white);
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  line-height: 1;
}

.neighbour .badge.white {
  background: var(--white);
  color: var(--blue);
}

.neighbour .time {
  font-weight: 700;
  font-size: 1.1rem;
}

.neighbour .rate {
  margin-left: auto;
  font-weight: 700;
}

.neighbour .rate.warn {
  color: var(--yellow);
}
</style>
