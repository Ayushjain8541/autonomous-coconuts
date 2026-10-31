export type Severity = 'Critical' | 'Elevated' | 'Safe';
export interface Encounter { id: string; object: string; day: number; time: string; distance: string; severity: Severity }
// Fixed illustrative encounters. No input file contents are read or interpreted.
export const encounters: Encounter[] = Array.from({ length: 35 }, (_, index) => {
  const day = Math.floor(index / 5);
  const severity: Severity = index % 5 === 0 ? 'Critical' : index % 3 === 0 ? 'Elevated' : 'Safe';
  return { id: `demo-${index}`, object: `SAT-${String(1042 + index * 17)}`, day, time: `2030-01-${String(1 + day).padStart(2, '0')} ${String(2 + (index * 3) % 21).padStart(2, '0')}:${String((index * 13) % 60).padStart(2, '0')}`, distance: (0.18 + ((index * 137) % 4400) / 1000).toFixed(2), severity };
});
export function encountersForDays(days: number): Encounter[] {
  if (!Number.isInteger(days) || days < 1 || days > 7) return [];
  return encounters.filter(row => row.day < days);
}
