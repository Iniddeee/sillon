import { describe, it, expect } from 'vitest'
import { isOccasional } from '../occasional'
import type { Day, Train } from '../data'

function train(dayCount: number): Train {
  const days: Record<string, Day> = {}
  for (let i = 0; i < dayCount; i++) {
    days[`2026-09-${String(i + 1).padStart(2, '0')}`] = { status: 'real', dep: 0, arr: 0 }
  }
  return { key: 'S3|07:04', line: 'S3', planned_dep: '07:04', planned_arr: '07:31', days }
}

describe('isOccasional', () => {
  it('below 40% of the window is occasional', () => {
    expect(isOccasional(train(3), 10)).toBe(true)
  })

  it('at 40% is not occasional', () => {
    expect(isOccasional(train(4), 10)).toBe(false)
  })

  it('above 40% is not occasional', () => {
    expect(isOccasional(train(9), 10)).toBe(false)
  })

  it('an empty window is never occasional', () => {
    expect(isOccasional(train(0), 0)).toBe(false)
  })
})
