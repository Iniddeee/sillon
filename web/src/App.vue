<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { DataIndex, PairData, Train } from '@/lib/data'
import { loadIndex, loadPair, trainDays } from '@/lib/data'
import { score, toMinutes } from '@/lib/score'
import { neighbours, verdict } from '@/lib/neighbours'
import { timetableUrl } from '@/lib/sbb'
import PairPicker from '@/components/PairPicker.vue'
import StationClock from '@/components/StationClock.vue'
import DayStrip from '@/components/DayStrip.vue'
import DepartureBoard from '@/components/DepartureBoard.vue'

const index = ref<DataIndex | null>(null)
const loaded = ref(false)
const selectedPairId = ref('')
const pairData = ref<PairData | null>(null)
const heroTrain = ref<Train | null>(null)

onMounted(async () => {
  index.value = await loadIndex()
  loaded.value = true
  if (index.value && index.value.pairs.length > 0) {
    selectedPairId.value = index.value.pairs[0]!.id
  }
})

watch(selectedPairId, async (id) => {
  pairData.value = id ? await loadPair(id) : null
  heroTrain.value = pairData.value ? defaultTrain(pairData.value.trains) : null
})

// first departure at or after 6h, so a commuter opening the page sees their morning train
function defaultTrain(trains: Train[]): Train | null {
  if (trains.length === 0) return null
  const sorted = [...trains].sort((a, b) => a.planned_dep.localeCompare(b.planned_dep))
  return sorted.find((t) => toMinutes(t.planned_dep) >= 360) ?? sorted[0]!
}

function selectTrain(train: Train) {
  heroTrain.value = train
}

function time(hhmm: string): string {
  return hhmm.replace(':', '.')
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function rateLabel(rate: number | null): string {
  return rate === null ? '—' : `${Math.round(rate * 100)} %`
}

const heroHh = computed(() => {
  const dep = heroTrain.value?.planned_dep
  return dep ? Number(dep.split(':')[0]) : 0
})
const heroMm = computed(() => {
  const dep = heroTrain.value?.planned_dep
  return dep ? Number(dep.split(':')[1]) : 0
})

const heroScore = computed(() =>
  heroTrain.value ? score(heroTrain.value, pairData.value?.transfer_min ?? 2) : null,
)
const heroDenom = computed(() =>
  heroScore.value ? heroScore.value.measured + heroScore.value.cancelled : 0,
)
const heroRateDisplay = computed(() => {
  const s = heroScore.value
  return s === null || s.rate === null ? '—' : String(Math.round(s.rate * 100))
})

const dateRangeLabel = computed(() => {
  const days = index.value?.days ?? []
  if (days.length === 0) return ''
  const fmt = new Intl.DateTimeFormat('fr-CH', { day: 'numeric', month: 'long' })
  const first = fmt.format(new Date(`${days[0]!}T00:00:00`))
  const last = fmt.format(new Date(`${days[days.length - 1]!}T00:00:00`))
  return `${first} → ${last}`
})

const lateDays = computed(() =>
  heroTrain.value
    ? trainDays(heroTrain.value).filter((d) => d.status === 'real' && (d.arr ?? 0) >= 3)
    : [],
)

const ranked = computed(() =>
  heroTrain.value && pairData.value
    ? neighbours(pairData.value.trains, heroTrain.value, pairData.value.transfer_min)
    : [],
)
const nearby = computed(() => ranked.value.slice(0, 2))
const verdictText = computed(() =>
  heroTrain.value ? verdict(heroTrain.value, ranked.value, pairData.value?.transfer_min ?? 2) : '',
)

const sbbUrl = computed(() =>
  heroTrain.value && pairData.value ? timetableUrl(pairData.value, heroTrain.value) : '#',
)
</script>

<template>
  <div class="page">
    <svg class="grain" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>

    <p v-if="loaded && (!index || index.pairs.length === 0)" class="empty">
      Les données arrivent avec le premier passage nocturne.
    </p>

    <template v-else-if="index">
      <header class="top">
        <div class="brand">
          <span class="dot" />
          <span class="name">Sillon</span>
        </div>
        <PairPicker v-model="selectedPairId" :pairs="index.pairs" />
      </header>

      <div v-if="pairData && heroTrain && heroScore" class="board">
        <div class="col-left">
          <StationClock class="a-clock" :hh="heroHh" :mm="heroMm" :size="380" />

          <div class="a-calendar">
            <div class="calendar-title">
              <span class="name full-only">
                Les {{ index.days.length }} derniers jours du {{ time(heroTrain.planned_dep) }}
              </span>
              <span class="name mobile-only">Les {{ index.days.length }} derniers jours</span>
              <span class="range full-only">{{ dateRangeLabel }}</span>
            </div>
            <DayStrip
              :days="index.days"
              :train="heroTrain"
              :transfer-min="pairData.transfer_min"
              :via="pairData.via"
            />
            <div class="legend">
              <span><i class="sw ink" />à l'heure</span>
              <span><i class="sw yellow" />3 min et plus</span>
              <span><i class="sw red" />supprimé</span>
              <span><i class="sw hollow" />pas de donnée</span>
              <span v-if="pairData.via"><i class="sw missed" />correspondance ratée</span>
            </div>
          </div>
        </div>

        <div class="col-right">
          <div class="a-hero">
            <div class="hero-head">
              <span class="badge">{{ heroTrain.line }}</span>
              <span class="hero-time">{{ time(heroTrain.planned_dep) }}</span>
              <span class="hero-dest full-only">→ {{ pairData.to.name }} {{ time(heroTrain.planned_arr) }}</span>
              <span class="hero-dest mobile-only">→ {{ time(heroTrain.planned_arr) }}</span>
            </div>
            <div class="hero-num">
              <span class="pct">{{ heroRateDisplay }}</span>
              <span class="pct-sign">%</span>
              <span class="phrase full-only">
                à l'heure sur les {{ index.days.length }} derniers jours, {{ heroScore.onTime }} jours sur
                {{ heroDenom }}.
              </span>
            </div>
            <span class="phrase mobile-only">à l'heure, {{ heroScore.onTime }} jours sur {{ heroDenom }}</span>
          </div>

          <div class="a-stats">
            <div>
              <span class="label">Retard typique</span>
              <span class="value">{{ heroScore.median !== null ? `${heroScore.median} min` : '—' }}</span>
            </div>
            <div>
              <span class="label">9 fois sur 10</span>
              <span class="value">{{ heroScore.p90 !== null ? `≤ ${heroScore.p90} min` : '—' }}</span>
            </div>
            <div>
              <span class="label">Supprimé</span>
              <span class="value red">{{ heroScore.cancelled }} jour{{ heroScore.cancelled === 1 ? '' : 's' }}</span>
            </div>
            <div>
              <span class="label">Pas de donnée</span>
              <span class="value">{{ heroScore.noData }} jour{{ heroScore.noData === 1 ? '' : 's' }}</span>
            </div>
          </div>

          <div class="a-button">
            <a class="sbb" :href="sbbUrl" target="_blank" rel="noopener">
              Horaire et billet sur sbb.ch
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 8h10M9 4l4 4-4 4" />
              </svg>
            </a>
            <span class="hint full-only">ouvre l'horaire CFF avec ce trajet et cette heure</span>
          </div>

          <div class="a-extra">
            <div class="late">
              <span class="label">Les jours en retard</span>
              <div v-for="d in lateDays" :key="d.date" class="late-row">
                <span>{{ formatDate(d.date) }}</span>
                <span :class="(d.arr ?? 0) < 6 ? 'yellow' : 'red'">+{{ d.arr }} min</span>
              </div>
              <p v-if="!lateDays.length" class="none">Aucun retard mesuré sur la fenêtre.</p>
            </div>
            <div class="neigh">
              <span class="label">Départs voisins</span>
              <p class="verdict">{{ verdictText }}</p>
              <button
                v-for="n in nearby"
                :key="n.train.key"
                class="neigh-row"
                type="button"
                @click="selectTrain(n.train)"
              >
                <span
                  ><b>{{ n.train.line }} {{ time(n.train.planned_dep) }}</b>
                  <span class="muted">arrivée {{ time(n.train.planned_arr) }}</span></span
                >
                <span>{{ rateLabel(n.score.rate) }}</span>
              </button>
            </div>
          </div>

          <div class="a-list">
            <DepartureBoard :pair="pairData" :selected-key="heroTrain.key" :days="index.days" @select="selectTrain" />
          </div>
        </div>
      </div>

      <span class="footer">
        Données : opentransportdata.swiss, fichiers Ist-Daten, agrégés chaque nuit. Un train est ponctuel s'il
        arrive avec moins de 3 minutes de retard.
      </span>
    </template>
  </div>
</template>

<style scoped>
.page {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 56px 48px;
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.grain {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.06;
  pointer-events: none;
  mix-blend-mode: multiply;
}

.empty {
  opacity: 0.85;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand .dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--red);
}

.brand .name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.board {
  display: grid;
  grid-template-columns: 446px minmax(0, 1fr);
  align-items: start;
  gap: 56px;
}

.col-left {
  display: flex;
  flex-direction: column;
  gap: 22px;
  align-items: flex-start;
}

.col-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.a-clock {
  align-self: center;
  width: 100%;
  max-width: 380px;
}

.a-calendar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.calendar-title {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-top: 2px solid var(--ink);
  padding-top: 8px;
}

.calendar-title .name {
  font-size: 13px;
  font-weight: 700;
}

.calendar-title .range {
  font-size: 12px;
  color: var(--muted);
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 12px;
  color: var(--muted);
}

.legend span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sw {
  display: block;
  width: 10px;
  height: 10px;
  box-sizing: border-box;
}

.sw.ink {
  background: var(--ink);
}

.sw.yellow {
  background: var(--yellow);
}

.sw.red {
  background: var(--red);
}

.sw.hollow {
  border: 2px solid var(--ink);
}

.sw.missed {
  background: var(--yellow);
  border: 2px solid var(--red);
}

.a-hero {
  grid-area: hero;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hero-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.badge {
  font-size: 12px;
  font-weight: 700;
  color: #ffffff;
  background: var(--red);
  padding: 3px 8px;
}

.hero-time {
  font-size: 30px;
  font-weight: 700;
}

.hero-dest {
  font-size: 16px;
  color: var(--muted);
}

.hero-num {
  display: flex;
  align-items: baseline;
  gap: 12px;
  line-height: 0.9;
}

.pct {
  font-size: 150px;
  font-weight: 700;
  letter-spacing: -0.04em;
}

.pct-sign {
  font-size: 54px;
  font-weight: 700;
  color: var(--red);
}

.phrase {
  font-size: 19px;
  color: var(--muted);
  max-width: 230px;
  line-height: 1.25;
}

.phrase.mobile-only {
  max-width: none;
}

.mobile-only {
  display: none;
}

.a-stats {
  grid-area: stats;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  border-top: 2px solid var(--ink);
  padding-top: 10px;
}

.a-stats > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.a-stats .label {
  font-size: 12px;
  color: var(--muted);
}

.a-stats .value {
  font-size: 22px;
  font-weight: 700;
}

.a-stats .value.red {
  color: var(--red);
}

.a-button {
  grid-area: button;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sbb {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 16px;
  background: var(--ink);
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.hint {
  font-size: 12px;
  color: var(--muted);
}

.a-extra {
  grid-area: extra;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 32px;
}

.a-extra .label {
  display: block;
  font-size: 12px;
  color: var(--muted);
  padding-bottom: 6px;
}

.late-row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  border-top: 1px solid var(--rule);
  font-size: 14px;
}

.late-row .yellow {
  color: var(--yellow);
  font-weight: 700;
}

.late-row .red {
  color: var(--red);
  font-weight: 700;
}

.late .none {
  margin: 0;
  font-size: 14px;
  color: var(--muted);
}

.neigh {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.verdict {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.3;
}

.neigh-row {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 7px 0;
  border: none;
  border-top: 1px solid var(--rule);
  font: inherit;
  font-size: 14px;
  color: inherit;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.neigh-row .muted {
  color: var(--muted);
}

.a-list {
  grid-area: list;
}

.footer {
  font-size: 12px;
  color: var(--muted);
}

@media (max-width: 899px) {
  .page {
    padding: 20px 16px 28px;
    gap: 18px;
  }

  .brand .dot {
    width: 12px;
    height: 12px;
  }

  .brand .name {
    font-size: 18px;
  }

  .board {
    grid-template-columns: 132px minmax(0, 1fr);
    grid-template-areas:
      'clock hero'
      'stats stats'
      'calendar calendar'
      'button button'
      'extra extra'
      'list list';
    gap: 18px;
    align-items: center;
  }

  .col-left,
  .col-right {
    display: contents;
  }

  .a-clock {
    grid-area: clock;
    max-width: 132px;
  }

  .a-calendar {
    grid-area: calendar;
  }

  .hero-time {
    font-size: 24px;
  }

  .hero-dest {
    font-size: 13px;
  }

  .pct {
    font-size: 76px;
  }

  .pct-sign {
    font-size: 28px;
  }

  .phrase {
    font-size: 13px;
  }

  .a-stats .label {
    font-size: 11px;
  }

  .a-stats .value {
    font-size: 18px;
  }

  .legend {
    font-size: 11px;
  }

  .sw {
    width: 9px;
    height: 9px;
  }

  .sbb {
    width: 100%;
    justify-content: center;
    padding: 13px 16px;
  }

  .a-extra {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .footer {
    font-size: 11px;
  }

  .full-only {
    display: none;
  }

  .mobile-only {
    display: inline;
  }
}
</style>
