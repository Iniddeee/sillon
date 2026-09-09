export interface Station {
  bpuic: number
  name: string
}

export interface Pair {
  id: string
  from: Station
  to: Station
  via: Station | null
}

export interface DataIndex {
  generated: string
  days: string[]
  pairs: Pair[]
}

export type DayStatus = 'real' | 'cancelled' | 'nodata'

export interface Day {
  status: DayStatus
  dep?: number
  arr?: number
  legs?: [{ arr: number }, { dep: number }]
}

export interface Train {
  key: string
  line: string
  planned_dep: string
  planned_arr: string
  line2?: string
  via_arr?: string
  via_dep?: string
  days: Record<string, Day>
}

export interface PairData extends Pair {
  transfer_min: number
  trains: Train[]
}

export interface DayEntry extends Day {
  date: string
}

const base = import.meta.env.BASE_URL

export async function loadIndex(): Promise<DataIndex | null> {
  const res = await fetch(`${base}data/index.json`)
  if (!res.ok) return null
  return res.json()
}

export async function loadPair(id: string): Promise<PairData | null> {
  const res = await fetch(`${base}data/pairs/${id}.json`)
  if (!res.ok) return null
  return res.json()
}

export function trainDays(train: Train): DayEntry[] {
  return Object.entries(train.days)
    .map(([date, day]) => ({ date, ...day }))
    .sort((a, b) => a.date.localeCompare(b.date))
}
