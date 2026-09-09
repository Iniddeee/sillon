<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import type { DataIndex, PairData, Train } from '@/lib/data'
import { loadIndex, loadPair } from '@/lib/data'
import PairPicker from '@/components/PairPicker.vue'
import DepartureBoard from '@/components/DepartureBoard.vue'
import TrainDetail from '@/components/TrainDetail.vue'

const index = ref<DataIndex | null>(null)
const loaded = ref(false)
const selectedPairId = ref('')
const pairData = ref<PairData | null>(null)
const selectedTrain = ref<Train | null>(null)

onMounted(async () => {
  index.value = await loadIndex()
  loaded.value = true
  if (index.value && index.value.pairs.length > 0) {
    selectedPairId.value = index.value.pairs[0]!.id
  }
})

watch(selectedPairId, async (id) => {
  selectedTrain.value = null
  pairData.value = id ? await loadPair(id) : null
})

function selectTrain(train: Train) {
  selectedTrain.value = selectedTrain.value?.key === train.key ? null : train
}
</script>

<template>
  <main>
    <h1>Sillon</h1>
    <p class="tagline">
      Ce train précis, sur les 90 derniers jours : à l'heure, en retard, ou pas venu du tout.
    </p>

    <p v-if="loaded && (!index || index.pairs.length === 0)" class="empty">
      Les données arrivent avec le premier passage nocturne.
    </p>

    <template v-else-if="index">
      <PairPicker v-model="selectedPairId" :pairs="index.pairs" />

      <p class="legend">
        <span class="legend-item">
          <svg width="10" height="10" aria-hidden="true"><rect width="10" height="10" fill="#ffffff" /></svg>
          à l'heure
        </span>
        <span class="legend-item">
          <svg width="10" height="10" aria-hidden="true"><rect width="10" height="10" fill="#ffcc00" /></svg>
          retard de 3 min et plus
        </span>
        <span class="legend-item">
          <svg width="10" height="10" aria-hidden="true"><rect width="10" height="10" fill="#e2231a" /></svg>
          supprimé
        </span>
        <span class="legend-item">
          <svg width="10" height="10" aria-hidden="true">
            <rect width="10" height="10" fill="none" stroke="rgba(255,255,255,.5)" />
          </svg>
          pas de donnée
        </span>
        <span v-if="pairData?.via" class="legend-item">
          <svg width="10" height="10" aria-hidden="true">
            <rect width="10" height="10" fill="#ffcc00" stroke="#e2231a" stroke-width="2" />
          </svg>
          correspondance ratée
        </span>
      </p>

      <DepartureBoard
        v-if="pairData"
        :pair="pairData"
        :selected-key="selectedTrain?.key ?? null"
        @select="selectTrain"
      />
      <TrainDetail
        v-if="selectedTrain"
        :train="selectedTrain"
        :trains="pairData?.trains ?? []"
        @select="selectTrain"
      />
    </template>
  </main>
</template>

<style scoped>
main {
  max-width: 48rem;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
}

h1 {
  font-size: 1.75rem;
  margin: 0 0 0.4rem;
  letter-spacing: 0.02em;
}

.tagline {
  max-width: 34rem;
  margin: 0 0 1.25rem;
  font-size: 0.95rem;
  opacity: 0.75;
}

.empty {
  opacity: 0.85;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.9rem;
  margin: 0.75rem 0 1rem;
  font-size: 0.75rem;
  opacity: 0.85;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.legend-item svg {
  display: block;
  flex: none;
}

.legend-item:not(:last-child)::after {
  content: '·';
  margin-left: 0.9rem;
  opacity: 0.6;
}
</style>
