import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../App.vue'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('shows the empty state when index.json is missing', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 404 }),
    )

    const wrapper = mount(App)
    await flushPromises()

    expect(wrapper.text()).toContain('Les données arrivent avec le premier passage nocturne.')
  })

  it('lists the tracked pairs from index.json', async () => {
    const index = {
      generated: '2026-09-08',
      days: ['2026-09-08'],
      pairs: [
        {
          id: 'delemont-porrentruy',
          from: { bpuic: 8504221, name: 'Delémont' },
          to: { bpuic: 8504225, name: 'Porrentruy' },
          via: null,
        },
        {
          id: 'bienne-lausanne',
          from: { bpuic: 8504200, name: 'Bienne/Biel' },
          to: { bpuic: 8501120, name: 'Lausanne' },
          via: null,
        },
      ],
    }
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true, json: async () => index }),
    )

    const wrapper = mount(App)
    await flushPromises()

    expect(wrapper.text()).toContain('Delémont → Porrentruy')
    expect(wrapper.text()).toContain('Bienne/Biel → Lausanne')
  })
})
