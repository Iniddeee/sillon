import type { Train } from './data'
import type { Score } from './score'
import { score } from './score'

export interface Ranked {
  train: Train
  score: Score
}

function minutesOf(hhmm: string): number {
  const [h, m] = hhmm.split(':')
  return Number(h) * 60 + Number(m)
}

export function neighbours(
  trains: Train[],
  selected: Train,
  transferMin = 2,
  windowMin = 60,
): Ranked[] {
  const selectedMin = minutesOf(selected.planned_dep)

  return trains
    .filter((t) => t.key !== selected.key)
    .filter((t) => Math.abs(minutesOf(t.planned_dep) - selectedMin) < windowMin)
    .map((train) => ({ train, score: score(train, transferMin) }))
    .sort(compareRanked)
}

function compareRanked(a: Ranked, b: Ranked): number {
  const rate = compareDesc(a.score.rate, b.score.rate)
  if (rate !== 0) return rate

  const median = compareAsc(a.score.median, b.score.median)
  if (median !== 0) return median

  return minutesOf(a.train.planned_dep) - minutesOf(b.train.planned_dep)
}

function compareAsc(a: number | null, b: number | null): number {
  if (a === null) return b === null ? 0 : 1
  if (b === null) return -1
  return a - b
}

function compareDesc(a: number | null, b: number | null): number {
  if (a === null) return b === null ? 0 : 1
  if (b === null) return -1
  return b - a
}

export function verdict(selected: Train, ranked: Ranked[], transferMin = 2): string {
  if (ranked.length === 0) return "Aucun autre départ à moins d'une heure."

  const best = ranked[0]!
  const ownRate = score(selected, transferMin).rate

  if (best.score.rate !== null && ownRate !== null) {
    // compare the percentages people see, so the wording never contradicts the numbers
    const bestPct = Math.round(best.score.rate * 100)
    const ownPct = Math.round(ownRate * 100)
    if (bestPct - ownPct >= 5) {
      const time = best.train.planned_dep.replace(':', '.')
      return `Le ${time} est plus fiable : ${bestPct} % contre ${ownPct} %.`
    }
    if (bestPct > ownPct) return 'Ses voisins font à peu près pareil.'
  }

  return "C'est le plus fiable de sa tranche horaire."
}
