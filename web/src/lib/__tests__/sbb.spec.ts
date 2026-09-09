import { describe, it, expect } from 'vitest'
import { timetableUrl } from '../sbb'
import type { Pair, Train } from '../data'

const pair: Pair = {
  id: 'delemont-porrentruy',
  from: { bpuic: 8500109, name: 'Delémont' },
  to: { bpuic: 8500126, name: 'Porrentruy' },
  via: null,
}

function train(dep: string): Train {
  return { key: `S3|${dep}`, line: 'S3', planned_dep: dep, planned_arr: dep, days: {} }
}

describe('timetableUrl', () => {
  it('encodes accented station names', () => {
    const url = timetableUrl(pair, train('06:51'), new Date('2026-09-09T10:00:00Z'))
    expect(url).toContain('von=Del%C3%A9mont')
    expect(url).toContain('nach=Porrentruy')
  })

  it('keeps the departure time uncoded and appends suche=true', () => {
    const url = timetableUrl(pair, train('06:51'), new Date('2026-09-09T10:00:00Z'))
    expect(url).toContain('zeit=06:51')
    expect(url).toContain('suche=true')
  })

  it('moves to tomorrow once the planned departure has passed in Zurich', () => {
    // 10:00 UTC = 12:00 in Zurich (CEST) on 2026-09-09
    const url = timetableUrl(pair, train('06:51'), new Date('2026-09-09T10:00:00Z'))
    expect(url).toContain('datum=10.09.2026')
  })

  it('keeps today when the planned departure is still ahead', () => {
    const url = timetableUrl(pair, train('18:00'), new Date('2026-09-09T10:00:00Z'))
    expect(url).toContain('datum=09.09.2026')
  })
})
