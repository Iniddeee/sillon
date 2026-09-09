import type { Train } from './data'

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

export function score(train: Train): Score {
  const days = Object.values(train.days)
  const real = days.filter((d) => d.status === 'real')
  const cancelled = days.filter((d) => d.status === 'cancelled').length
  const noData = days.filter((d) => d.status === 'nodata').length

  const arrivals = real.map((d) => d.arr ?? 0).sort((a, b) => a - b)
  const onTime = arrivals.filter((arr) => arr < 3).length
  const late = arrivals.length - onTime
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
