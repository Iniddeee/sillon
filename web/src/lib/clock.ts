export interface HandAngles {
  hour: number
  minute: number
}

// station clock hands are drawn pointing at 12 in the SVG, rotated with CSS from there
export function handAngles(hh: number, mm: number): HandAngles {
  return {
    hour: ((hh % 12) + mm / 60) * 30,
    minute: mm * 6,
  }
}
