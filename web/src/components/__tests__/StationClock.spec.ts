import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StationClock from '../StationClock.vue'

describe('StationClock', () => {
  it('rotates the hands to match 06:51', () => {
    const wrapper = mount(StationClock, { props: { hh: 6, mm: 51, size: 380 } })
    const hands = wrapper.findAll('line.hand')

    expect(hands).toHaveLength(2)
    expect(hands[0]!.attributes('style')).toContain('rotate(205.5deg)')
    expect(hands[1]!.attributes('style')).toContain('rotate(306deg)')
  })

  it('draws 60 ticks and a fixed red mark', () => {
    const wrapper = mount(StationClock, { props: { hh: 0, mm: 0, size: 380 } })

    expect(wrapper.findAll('line').length).toBe(60 + 2 + 1)
    expect(wrapper.find('line[stroke="#eb0000"]').exists()).toBe(true)
  })
})
