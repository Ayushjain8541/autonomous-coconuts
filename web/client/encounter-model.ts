import type { Encounter, Severity } from './contract.ts';

export const clampTime = (value: number) => Math.min(1, Math.max(0, Number.isFinite(value) ? value : 0));
export function phaseLabel(time: number) {
  const t = clampTime(time);
  return Math.abs(t - .5) < .015 ? 'Closest approach' : t < .5 ? 'Approach' : 'Departure';
}
export function maneuverReview(severity: Severity): string {
  return ({critical:'Maneuver planning required · operator review',elevated:'Monitor / further assessment',safe:'No immediate maneuver planning indicated',unknown:'Undetermined'})[severity];
}
export function remainingTime(hours: number): string {
  const minutes = Math.round(hours * 60), h = Math.floor(minutes / 60), m = minutes % 60;
  return `${h}h${m ? ` ${m}m` : ''} remaining`;
}
/** Mode B only. Normalized conceptual paths, NOT propagation of supplied RTN states. */
export function schematicSample(missDistanceM: number | null, time: number) {
  if (missDistanceM === null || !Number.isFinite(missDistanceM) || missDistanceM < 0) return null;
  const t = clampTime(time), metresPerUnit = Math.max(missDistanceM / 4, 1);
  const relativeX = (t - .5) * 24, gap = missDistanceM / metresPerUnit;
  const primary: [number, number, number] = [-relativeX * .2, 0, 0];
  const debris: [number, number, number] = [relativeX * .8, gap, 0];
  return {time:t,primary,debris,metresPerUnit,separationM:Math.hypot(relativeX, gap) * metresPerUnit};
}
export type SortOrder = 'priority' | 'horizon' | 'pc' | 'distance' | 'event';
export function dashboardRows(rows: Encounter[], search: string, risk: string, sort: SortOrder) {
  const priority = {critical:0,elevated:1,unknown:2,safe:3};
  const result = rows.filter(row => row.event_id.toLowerCase().includes(search.trim().toLowerCase()) && (risk === 'all' || row.severity === risk));
  return result.sort((a,b) => {
    const comparison = sort === 'priority' ? priority[a.severity] - priority[b.severity] : sort === 'horizon' ? a.time_to_tca_hours - b.time_to_tca_hours : sort === 'pc' ? (b.predicted_pc ?? -1) - (a.predicted_pc ?? -1) : sort === 'distance' ? (a.miss_distance_m ?? Infinity) - (b.miss_distance_m ?? Infinity) : 0;
    return comparison || a.event_id.localeCompare(b.event_id);
  });
}
export function eventRoute(path: string): string | null {
  const match = /^\/encounters\/([^/]+)\/?$/.exec(path);
  if (!match) return null;
  try { return decodeURIComponent(match[1]); } catch { return null; }
}

/** Requires two explicit clocks; lead time is never report age. */
export function reportAgeHours(reportTimestamp: string | null, referenceClock: string | null): number | null {
  if (!reportTimestamp || !referenceClock) return null;
  const zonedIso = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
  if (!zonedIso.test(reportTimestamp) || !zonedIso.test(referenceClock)) return null;
  const report = Date.parse(reportTimestamp), reference = Date.parse(referenceClock);
  if (!Number.isFinite(report) || !Number.isFinite(reference) || report > reference) return null;
  return (reference - report) / 3_600_000;
}
export function sliderSample(raw: number, reducedMotion = false) {
  const time = clampTime(raw), overshoot = Number.isFinite(raw) ? raw - time : 0;
  return {time,visualOffset:reducedMotion ? 0 : Math.tanh(overshoot * 3) * 22};
}
export function advancePlayback(time: number, elapsedMs: number, speed: number) {
  const next = clampTime(time + Math.max(0, Math.min(100, elapsedMs)) / 10000 * Math.max(0, speed));
  return time < .5 && next >= .5 ? .5 : next;
}
