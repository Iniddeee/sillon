import type { Day, Train } from './data'

export interface Score {
  measured: number
  onTime: number
  late: number
  cancelled: number
  noData: number
  rate: number | null
  median: number | null
  p90: number | null
}

// Nearest-rank: median/p90 stay whole minutes that actually occurred, easy to explain.
function percentile(sorted: number[], p: number): number {
  return sorted[Math.ceil(p * sorted.length) - 1]!
}

export function toMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(':').map(Number)
  return h! * 60 + m!
}

// positive once the actual arrival at the transfer point, plus the transfer
// time, lands after the actual departure of the connecting train
export function missedBy(train: Train, day: Day): number | null {
  if (!day.legs || train.via_arr === undefined || train.via_dep === undefined) return null
  const arrival = toMinutes(train.via_arr) + day.legs[0].arr
  const departure = toMinutes(train.via_dep) + day.legs[1].dep
  return arrival - departure
}

export function missed(train: Train, day: Day, transferMin: number): boolean {
  const by = missedBy(train, day)
  return by !== null && by + transferMin > 0
}

// default 2 matches the pipeline's default (config/pairs.json min_transfer_min)
export function score(train: Train, transferMin = 2): Score {
  const days = Object.values(train.days)
  const real = days.filter((d) => d.status === 'real')
  const cancelled = days.filter((d) => d.status === 'cancelled').length
  const noData = days.filter((d) => d.status === 'nodata').length

  let onTime = 0
  let late = 0
  const arrivals: number[] = []

  for (const day of real) {
    if (missed(train, day, transferMin)) {
      late++
      continue
    }
    const arr = day.arr ?? 0
    arrivals.push(arr)
    if (arr < 3) onTime++
    else late++
  }
  arrivals.sort((a, b) => a - b)

  const denom = real.length + cancelled

  return {
    measured: real.length,
    onTime,
    late,
    cancelled,
    noData,
    rate: denom === 0 ? null : onTime / denom,
    median: arrivals.length ? percentile(arrivals, 0.5) : null,
    p90: arrivals.length ? percentile(arrivals, 0.9) : null,
  }
}
