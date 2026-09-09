import { describe, it, expect } from 'vitest'
import { neighbours, verdict } from '../neighbours'
import type { Day, Train } from '../data'

function train(key: string, dep: string, days: Record<string, Day>): Train {
  return { key, line: 'S3', planned_dep: dep, planned_arr: dep, days }
}

const reliable: Record<string, Day> = {
  '2026-09-01': { status: 'real', dep: 0, arr: 0 },
  '2026-09-02': { status: 'real', dep: 0, arr: 0 },
  '2026-09-03': { status: 'real', dep: 0, arr: 0 },
  '2026-09-04': { status: 'real', dep: 0, arr: 0 },
  '2026-09-05': { status: 'real', dep: 0, arr: 0 },
}

const unreliable: Record<string, Day> = {
  '2026-09-01': { status: 'real', dep: 5, arr: 5 },
  '2026-09-02': { status: 'real', dep: 5, arr: 5 },
  '2026-09-03': { status: 'real', dep: 0, arr: 0 },
  '2026-09-04': { status: 'real', dep: 5, arr: 5 },
  '2026-09-05': { status: 'real', dep: 0, arr: 0 },
}

const noData: Record<string, Day> = {
  '2026-09-01': { status: 'nodata' },
  '2026-09-02': { status: 'nodata' },
}

describe('neighbours', () => {
  it('keeps trains strictly inside the window and drops the boundary', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const within = train('S3|07:01', '07:01', reliable)
    const onBoundary = train('S3|07:00', '07:00', reliable)
    const outside = train('S3|06:59', '06:59', reliable)

    const result = neighbours([selected, within, onBoundary, outside], selected)

    expect(result.map((r) => r.train.key)).toEqual(['S3|07:01'])
  })

  it('excludes the selected train even if it would match the window', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const result = neighbours([selected], selected)
    expect(result).toEqual([])
  })

  it('ranks by rate desc, then median delay asc, then departure time', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const worse = train('S3|08:10', '08:10', unreliable)
    const better = train('S3|07:50', '07:50', reliable)

    const result = neighbours([selected, worse, better], selected)

    expect(result.map((r) => r.train.key)).toEqual(['S3|07:50', 'S3|08:10'])
  })

  it('sorts trains with a null rate after every ranked train', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const withData = train('S3|07:50', '07:50', unreliable)
    const withoutData = train('S3|08:05', '08:05', noData)

    const result = neighbours([selected, withData, withoutData], selected)

    expect(result.map((r) => r.train.key)).toEqual(['S3|07:50', 'S3|08:05'])
    expect(result[1]!.score.rate).toBeNull()
  })

  it('accepts a custom window', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const near = train('S3|08:20', '08:20', reliable)
    const result = neighbours([selected, near], selected, 2, 15)
    expect(result).toEqual([])
  })
})

describe('verdict', () => {
  it('names a neighbour that is at least 5 points more reliable', () => {
    const selected = train('S3|07:04', '07:04', unreliable)
    const better = train('S3|07:34', '07:34', reliable)
    const ranked = neighbours([selected, better], selected)

    expect(verdict(selected, ranked)).toBe('Le 07.34 est plus fiable : 100 % contre 40 %.')
  })

  it('says it is already the most reliable when no neighbour beats it by 5 points', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    const similar = train('S3|08:10', '08:10', reliable)
    const ranked = neighbours([selected, similar], selected)

    expect(verdict(selected, ranked)).toBe("C'est le plus fiable de sa tranche horaire.")
  })

  it('says there is no neighbour when the window is empty', () => {
    const selected = train('S3|08:00', '08:00', reliable)
    expect(verdict(selected, [])).toBe("Aucun autre départ à moins d'une heure.")
  })
})
