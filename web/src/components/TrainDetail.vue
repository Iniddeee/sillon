<script setup lang="ts">
import { computed } from 'vue'
import type { Train } from '@/lib/data'
import { trainDays } from '@/lib/data'
import { score } from '@/lib/score'

const props = defineProps<{ train: Train }>()

const s = computed(() => score(props.train))
const lateDays = computed(() =>
  trainDays(props.train).filter((d) => d.status === 'real' && (d.arr ?? 0) >= 3),
)

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
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
</style>
