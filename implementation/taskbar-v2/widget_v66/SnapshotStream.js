.pragma library

function initial() { return {epoch: "", sequence: 0} }
function empty() { return {groups: [], snapGroups: [], monitors: [], settings: {}, focusedAddress: "", reducedMotion: false} }
function object(value) { return value !== null && typeof value === "object" && !Array.isArray(value) }
function decode(line, state) {
  if (typeof line !== "string" || line.length > 4 * 1024 * 1024) return null
  var value
  try { value = JSON.parse(line) } catch (error) { return null }
  if (!object(value) || value.protocolVersion !== 1 || typeof value.epoch !== "string"
      || !/^[a-zA-Z0-9_-]{1,128}$/.test(value.epoch) || !Number.isSafeInteger(value.sequence)
      || value.sequence <= state.sequence || state.epoch && value.epoch !== state.epoch) return null
  if (!Array.isArray(value.groups) || !Array.isArray(value.snapGroups) || !Array.isArray(value.monitors)
      || !object(value.settings) || typeof value.focusedAddress !== "string" || typeof value.reducedMotion !== "boolean") return null
  for (var i = 0; i < value.groups.length; i++) {
    var group = value.groups[i]
    if (!object(group) || typeof group.key !== "string" || typeof group.desktopId !== "string"
        || typeof group.name !== "string" || typeof group.icon !== "string" || typeof group.pinned !== "boolean"
        || !Array.isArray(group.windows) || !Array.isArray(group.actions) || !Array.isArray(group.recent)) return null
    for (var j = 0; j < group.windows.length; j++) {
      var window = group.windows[j]
      if (!object(window) || typeof window.address !== "string" || !/^0x[0-9a-fA-F]+$/.test(window.address)
          || !object(window.workspace) || typeof window.workspace.name !== "string") return null
    }
  }
  return {state: {epoch: value.epoch, sequence: value.sequence}, snapshot: value}
}
