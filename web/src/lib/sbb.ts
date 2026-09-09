import type { Pair, Train } from './data'
import { toMinutes } from './score'

interface ZurichNow {
  year: number
  month: number
  day: number
  minutes: number
}

function zurichNow(now: Date): ZurichNow {
  const fmt = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Zurich',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  })
  const parts = Object.fromEntries(fmt.formatToParts(now).map((p) => [p.type, p.value]))
  return {
    year: Number(parts.year),
    month: Number(parts.month),
    day: Number(parts.day),
    minutes: Number(parts.hour) * 60 + Number(parts.minute),
  }
}

function tomorrow(zurich: ZurichNow): { year: number; month: number; day: number } {
  const utc = new Date(Date.UTC(zurich.year, zurich.month - 1, zurich.day + 1))
  return { year: utc.getUTCFullYear(), month: utc.getUTCMonth() + 1, day: utc.getUTCDate() }
}

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

// pre-fills sbb.ch's timetable search with this train's route and departure time
export function timetableUrl(pair: Pair, train: Train, now = new Date()): string {
  const zurich = zurichNow(now)
  const isPast = toMinutes(train.planned_dep) < zurich.minutes
  const { year, month, day } = isPast ? tomorrow(zurich) : zurich
  const datum = `${pad(day)}.${pad(month)}.${year}`
  const von = encodeURIComponent(pair.from.name)
  const nach = encodeURIComponent(pair.to.name)
  return `https://www.sbb.ch/fr/acheter/pages/fahrplan/fahrplan.xhtml?von=${von}&nach=${nach}&datum=${datum}&zeit=${train.planned_dep}&suche=true`
}
