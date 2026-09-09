import { describe, it, expect } from 'vitest'
import { handAngles } from '../clock'

describe('handAngles', () => {
  it('06:51', () => {
    expect(handAngles(6, 51)).toEqual({ hour: 205.5, minute: 306 })
  })

  it('00:00 points both hands at 12', () => {
    expect(handAngles(0, 0)).toEqual({ hour: 0, minute: 0 })
  })

  it('12:30 wraps the hour to 0', () => {
    expect(handAngles(12, 30)).toEqual({ hour: 15, minute: 180 })
  })
})
