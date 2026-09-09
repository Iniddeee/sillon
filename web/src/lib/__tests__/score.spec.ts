import { describe, it, expect } from 'vitest'
import { missed, score } from '../score'
import type { Day, Train } from '../data'

function train(days: Record<string, Day>): Train {
  return { key: 'S3|07:04', line: 'S3', planned_dep: '07:04', planned_arr: '07:31', days }
}

function itineraryTrain(days: Record<string, Day>): Train {
  return {
    key: 'S3|07:04',
    line: 'S3',
    planned_dep: '07:04',
    planned_arr: '09:12',
    line2: 'IC5',
    via_arr: '07:51',
    via_dep: '08:02',
    days,
  }
}

describe('score', () => {
  it('all on time gives a 100% rate', () => {
    const s = score(
      train({
        '2026-09-01': { status: 'real', dep: 0, arr: 0 },
        '2026-09-02': { status: 'real', dep: 0, arr: 1 },
        '2026-09-03': { status: 'real', dep: 1, arr: 2 },
      }),
    )
    expect(s.measured).toBe(3)
    expect(s.onTime).toBe(3)
    expect(s.late).toBe(0)
    expect(s.cancelled).toBe(0)
    expect(s.rate).toBe(1)
  })

  it('a cancelled day counts against the rate', () => {
    const s = score(
      train({
        '2026-09-01': { status: 'real', dep: 0, arr: 0 },
        '2026-09-02': { status: 'real', dep: 0, arr: 1 },
        '2026-09-03': { status: 'real', dep: 0, arr: 0 },
        '2026-09-04': { status: 'real', dep: 0, arr: 0 },
        '2026-09-05': { status: 'cancelled' },
      }),
    )
    expect(s.cancelled).toBe(1)
    expect(s.rate).toBeCloseTo(4 / 5)
  })

  it('nodata only gives a null rate and null quantiles', () => {
    const s = score(
      train({
        '2026-09-01': { status: 'nodata' },
        '2026-09-02': { status: 'nodata' },
      }),
    )
    expect(s.measured).toBe(0)
    expect(s.noData).toBe(2)
    expect(s.rate).toBeNull()
    expect(s.median).toBeNull()
    expect(s.p90).toBeNull()
  })

  it('2 min vs 3 min delay boundary', () => {
    const s = score(
      train({
        '2026-09-01': { status: 'real', dep: 2, arr: 2 },
        '2026-09-02': { status: 'real', dep: 3, arr: 3 },
      }),
    )
    expect(s.onTime).toBe(1)
    expect(s.late).toBe(1)
  })

  it('p90 over 10 values is the 9th value', () => {
    const days: Record<string, Day> = {}
    for (let i = 1; i <= 10; i++) {
      days[`2026-09-${String(i).padStart(2, '0')}`] = { status: 'real', dep: i, arr: i }
    }
    const s = score(train(days))
    expect(s.median).toBe(5)
    expect(s.p90).toBe(9)
  })
})

describe('missed', () => {
  const t = itineraryTrain({})

  it('missed when the actual arrival plus transfer lands after the actual departure', () => {
    const day: Day = { status: 'real', arr: 5, dep: 0, legs: [{ arr: 11 }, { dep: 0 }] }
    expect(missed(t, day, 2)).toBe(true)
  })

  it('held when there is enough buffer at the transfer', () => {
    const day: Day = { status: 'real', arr: 0, dep: 0, legs: [{ arr: 2 }, { dep: 0 }] }
    expect(missed(t, day, 2)).toBe(false)
  })

  it('exact equality counts as held', () => {
    // via_arr 07:51 + 9min + 2min transfer lands exactly on via_dep 08:02
    const day: Day = { status: 'real', arr: 0, dep: 0, legs: [{ arr: 9 }, { dep: 0 }] }
    expect(missed(t, day, 2)).toBe(false)
  })

  it('false without legs', () => {
    const day: Day = { status: 'real', arr: 0, dep: 0 }
    expect(missed(t, day, 2)).toBe(false)
  })
})

describe('score with a missed connection', () => {
  it('counts a missed real day as late and excludes its arrival from the quantiles', () => {
    const t = itineraryTrain({
      '2026-09-01': { status: 'real', arr: 0, dep: 0, legs: [{ arr: 0 }, { dep: 0 }] },
      '2026-09-02': { status: 'real', arr: 0, dep: 0, legs: [{ arr: 11 }, { dep: 0 }] },
    })
    const s = score(t, 2)
    expect(s.measured).toBe(2)
    expect(s.onTime).toBe(1)
    expect(s.late).toBe(1)
    expect(s.median).toBe(0)
  })
})
