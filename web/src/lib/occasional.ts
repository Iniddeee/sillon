import type { Train } from './data'

// runs on fewer than 40% of the window's days: not part of the regular pattern
export function isOccasional(train: Train, totalDays: number): boolean {
  if (totalDays === 0) return false
  return Object.keys(train.days).length / totalDays < 0.4
}
