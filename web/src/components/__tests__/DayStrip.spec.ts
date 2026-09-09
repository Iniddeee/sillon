import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DayStrip from '../DayStrip.vue'
import type { DayEntry } from '@/lib/data'

const days: DayEntry[] = [
  { date: '2026-09-01', status: 'real', dep: 0, arr: 0 },
  { date: '2026-09-02', status: 'real', dep: 3, arr: 4 },
  { date: '2026-09-03', status: 'cancelled' },
  { date: '2026-09-04', status: 'nodata' },
]

describe('DayStrip', () => {
  it('one square per day', () => {
    const wrapper = mount(DayStrip, { props: { days } })
    expect(wrapper.findAll('rect')).toHaveLength(days.length)
  })

  it('one color per status', () => {
    const wrapper = mount(DayStrip, { props: { days } })
    const rects = wrapper.findAll('rect')

    expect(rects[0]!.attributes('fill')).toBe('#ffffff')
    expect(rects[1]!.attributes('fill')).toBe('#ffcc00')
    expect(rects[2]!.attributes('fill')).toBe('#e2231a')
    expect(rects[3]!.attributes('fill')).toBe('transparent')
  })

  it('wraps to a new row every 30 days, oldest at the top-left', () => {
    const month: DayEntry[] = Array.from({ length: 31 }, (_, i) => ({
      date: `2026-01-${String(i + 1).padStart(2, '0')}`,
      status: 'real',
      dep: 0,
      arr: 0,
    }))
    const wrapper = mount(DayStrip, { props: { days: month } })
    const rects = wrapper.findAll('rect')

    expect(rects[0]!.attributes('x')).toBe('0')
    expect(rects[0]!.attributes('y')).toBe('0')
    expect(rects[29]!.attributes('y')).toBe('0')
    expect(rects[30]!.attributes('x')).toBe('0')
    expect(rects[30]!.attributes('y')).toBe('12')
  })
})
