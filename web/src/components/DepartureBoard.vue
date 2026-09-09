<script setup lang="ts">
import { computed } from 'vue'
import type { PairData, Train } from '@/lib/data'
import { isOccasional } from '@/lib/occasional'
import DepartureRow from './DepartureRow.vue'

const props = defineProps<{ pair: PairData; selectedKey: string | null; days: string[] }>()
defineEmits<{ select: [train: Train] }>()

const sorted = computed(() =>
  [...props.pair.trains].sort((a, b) => a.planned_dep.localeCompare(b.planned_dep)),
)

const regular = computed(() => sorted.value.filter((t) => !isOccasional(t, props.days.length)))
const occasional = computed(() => sorted.value.filter((t) => isOccasional(t, props.days.length)))
</script>

<template>
  <div class="departures">
    <span class="header">Tous les départs, cliquer pour changer</span>
    <DepartureRow
      v-for="train in regular"
      :key="train.key"
      :train="train"
      :selected="train.key === selectedKey"
      :transfer-min="pair.transfer_min"
      @click="$emit('select', train)"
    />
    <details v-if="occasional.length" class="occasional">
      <summary>Départs occasionnels ({{ occasional.length }})</summary>
      <DepartureRow
        v-for="train in occasional"
        :key="train.key"
        :train="train"
        :selected="train.key === selectedKey"
        :transfer-min="pair.transfer_min"
        @click="$emit('select', train)"
      />
    </details>
  </div>
</template>

<style scoped>
.departures {
  display: flex;
  flex-direction: column;
}

.header {
  font-size: 12px;
  color: var(--muted);
  padding-bottom: 6px;
}

.occasional {
  border-top: 1px solid var(--rule);
}

.occasional summary {
  padding: 9px 0;
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
}
</style>
