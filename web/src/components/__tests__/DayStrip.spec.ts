import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DayStrip from '../DayStrip.vue'
import type { Day, Train } from '@/lib/data'

function train(days: Record<string, Day>): Train {
  return { key: 'S3|07:04', line: 'S3', planned_dep: '07:04', planned_arr: '07:31', days }
}

describe('DayStrip', () => {
  it('one cell per day of the window, index preserved for a day the train never ran', () => {
    const days = ['2026-09-01', '2026-09-02', '2026-09-03']
    const t = train({
      '2026-09-01': { status: 'real', dep: 0, arr: 0 },
      '2026-09-03': { status: 'real', dep: 0, arr: 0 },
    })
    const wrapper = mount(DayStrip, { props: { days, train: t } })
    const cells = wrapper.findAll('.cell')

    expect(cells).toHaveLength(3)
    expect(cells[1]!.find('.dot').exists()).toBe(true)
    expect(cells[1]!.attributes('title')).toBe('pas de train ce jour')
    expect(cells[0]!.find('.dot').exists()).toBe(false)
  })

  it('one color per status', () => {
    const days = ['2026-09-01', '2026-09-02', '2026-09-03', '2026-09-04']
    const t = train({
      '2026-09-01': { status: 'real', dep: 0, arr: 0 },
      '2026-09-02': { status: 'real', dep: 3, arr: 4 },
      '2026-09-03': { status: 'cancelled' },
      '2026-09-04': { status: 'nodata' },
    })
    const wrapper = mount(DayStrip, { props: { days, train: t } })
    const cells = wrapper.findAll('.cell')

    expect(cells[0]!.attributes('style')).toContain('background: rgb(17, 17, 17)')
    expect(cells[1]!.attributes('style')).toContain('background: rgb(240, 180, 0)')
    expect(cells[2]!.attributes('style')).toContain('background: rgb(235, 0, 0)')
    expect(cells[3]!.attributes('style')).toContain('background: transparent')
    expect(cells[3]!.classes()).toContain('outlined')
  })

  it('a missed connection is drawn yellow with a red outline', () => {
    const t: Train = {
      key: 'S3|07:04',
      line: 'S3',
      planned_dep: '07:04',
      planned_arr: '09:12',
      line2: 'IC5',
      via_arr: '07:51',
      via_dep: '08:02',
      days: {
        '2026-09-01': { status: 'real', arr: 5, dep: 0, legs: [{ arr: 11 }, { dep: 0 }] },
      },
    }
    const wrapper = mount(DayStrip, {
      props: {
        days: ['2026-09-01'],
        train: t,
        transferMin: 2,
        via: { bpuic: 8504300, name: 'Bienne' },
      },
    })
    const cell = wrapper.find('.cell')

    expect(cell.attributes('style')).toContain('background: rgb(240, 180, 0)')
    expect(cell.classes()).toContain('outlined')
    expect(cell.attributes('data-missed')).toBe('true')
    expect(cell.attributes('title')).toContain('correspondance ratée')
  })

  it('a held connection on the same itinerary is not flagged', () => {
    const t: Train = {
      key: 'S3|07:04',
      line: 'S3',
      planned_dep: '07:04',
      planned_arr: '09:12',
      line2: 'IC5',
      via_arr: '07:51',
      via_dep: '08:02',
      days: {
        '2026-09-01': { status: 'real', arr: 0, dep: 0, legs: [{ arr: 1 }, { dep: 0 }] },
      },
    }
    const wrapper = mount(DayStrip, {
      props: {
        days: ['2026-09-01'],
        train: t,
        transferMin: 2,
        via: { bpuic: 8504300, name: 'Bienne' },
      },
    })
    const cell = wrapper.find('.cell')

    expect(cell.attributes('style')).toContain('background: rgb(17, 17, 17)')
    expect(cell.attributes('data-missed')).toBe('false')
  })
})
