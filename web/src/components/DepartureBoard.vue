<script setup lang="ts">
import { computed } from 'vue'
import type { PairData, Train } from '@/lib/data'
import DepartureRow from './DepartureRow.vue'

const props = defineProps<{ pair: PairData; selectedKey: string | null }>()
defineEmits<{ select: [train: Train] }>()

const trains = computed(() =>
  [...props.pair.trains].sort((a, b) => a.planned_dep.localeCompare(b.planned_dep)),
)
</script>

<template>
  <div class="board">
    <DepartureRow
      v-for="train in trains"
      :key="train.key"
      :train="train"
      :selected="train.key === selectedKey"
      @click="$emit('select', train)"
    />
  </div>
</template>

<style scoped>
.board {
  display: flex;
  flex-direction: column;
}
</style>
