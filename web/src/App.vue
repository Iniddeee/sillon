<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Station {
  bpuic: number
  name: string
}

interface Pair {
  id: string
  from: Station
  to: Station
  via: Station | null
}

interface DataIndex {
  generated: string
  days: string[]
  pairs: Pair[]
}

const pairs = ref<Pair[]>([])
const loaded = ref(false)

onMounted(async () => {
  const res = await fetch(`${import.meta.env.BASE_URL}data/index.json`)
  if (res.ok) {
    const data: DataIndex = await res.json()
    pairs.value = data.pairs
  }
  loaded.value = true
})
</script>

<template>
  <main>
    <h1>Sillon</h1>
    <p class="tagline">Fiabilité réelle des trains suisses, mesurée nuit après nuit.</p>

    <p v-if="loaded && pairs.length === 0" class="empty">
      Les données arrivent avec le premier passage nocturne.
    </p>

    <ul v-else-if="pairs.length > 0">
      <li v-for="pair in pairs" :key="pair.id">{{ pair.from.name }} → {{ pair.to.name }}</li>
    </ul>
  </main>
</template>

<style scoped>
main {
  max-width: 40rem;
  margin: 2rem auto;
  padding: 0 1rem;
  font-family: sans-serif;
}
</style>
