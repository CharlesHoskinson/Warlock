/** Match only the renderer's acknowledged presentation in this epoch.
 * A host that does not expose mode, controls and applied publication cannot
 * establish admission. It must not substitute popup placement for admission. */
export function matchesObservation(snapshot, expected, epoch) {
  const p = snapshot?.presentation;
  if (!p || snapshot.epoch !== epoch || !p.actionable || p.mode !== expected.mode) return false;
  const surface = expected.surface;
  if (p.applied?.[surface] !== p.publication) return false;
  const controls = p.controls?.[surface];
  return Array.isArray(controls) && expected.controls.every(id => controls.includes(id)) && (!expected.status || expected.status.some(status => status.toLowerCase() === p.operationStatus?.toLowerCase()));
}
