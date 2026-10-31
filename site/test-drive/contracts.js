/** Bridge and host API version. UInt64 identifiers cross this boundary as strings. */
export const BRIDGE_VERSION = 1;
export const FRAME_IDS = Object.freeze(['controller', 'bar', 'popup']);
export const FAULT_POLICIES = Object.freeze(['success', 'delayed', 'refusal', 'unknown', 'connection-loss', 'stale']);
export function isEnvelope(value) {
  return !!value && typeof value === 'object' && value.bridgeVersion === BRIDGE_VERSION && Number.isSafeInteger(value.epoch) && FRAME_IDS.includes(value.frameId) && typeof value.kind === 'string' && Object.hasOwn(value, 'payload');
}

/** Snapshot appearance is committed Settings values; motion.applied is the acknowledged profile ('full' or 'reduced'), or null while unacknowledged. */
export const SNAPSHOT_VERSION = 1;
