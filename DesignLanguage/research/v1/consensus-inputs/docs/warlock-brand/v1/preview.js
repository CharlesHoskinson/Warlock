"use strict";
// A bounded immutable illustration model. It performs no window-system effects.
const root = document.documentElement;
const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
const controls = Object.fromEntries(["theme", "motion", "event", "reset"].map(id => [id, document.getElementById(id)]));
let model = Object.freeze({ revision: 0, events: Object.freeze([]) });
let animationRequested = false;
function update(message, previous) {
  switch (message.kind) {
    case "Event": {
      const next = previous.revision + 1;
      return Object.freeze({ revision: next, events: Object.freeze([...previous.events, next].slice(-6)) });
    }
    case "Reset": return Object.freeze({ revision: 0, events: Object.freeze([]) });
    default: return previous;
  }
}
function render() {
  document.getElementById("flow-status").textContent = model.revision ? `Event ${model.revision} → state ${model.revision} → updated view.` : "Ready for an event.";
  const history = document.getElementById("event-history");
  history.replaceChildren(...model.events.map(revision => { const node = document.createElement("li"); node.textContent = `Event ${revision}`; return node; }));
}
function syncMotion() {
  const reduced = motionPreference.matches;
  if (reduced) animationRequested = false;
  const running = animationRequested && !document.hidden && !reduced;
  root.dataset.motion = running ? "on" : "off";
  controls.motion.disabled = reduced;
  controls.motion.setAttribute("aria-pressed", String(animationRequested));
  document.getElementById("motion-note").textContent = reduced ? "Reduced motion is enabled. The illustration stays still." : document.hidden && animationRequested ? "Animation pauses while this page is hidden." : "Animation starts only when you choose it.";
}
controls.theme.addEventListener("click", () => { const light = root.dataset.theme !== "light"; root.dataset.theme = light ? "light" : "dark"; controls.theme.setAttribute("aria-pressed", String(light)); });
controls.motion.addEventListener("click", () => { animationRequested = !animationRequested; syncMotion(); });
controls.event.addEventListener("click", () => { model = update({ kind: "Event" }, model); render(); });
controls.reset.addEventListener("click", () => { model = update({ kind: "Reset" }, model); render(); });
document.addEventListener("visibilitychange", syncMotion);
motionPreference.addEventListener("change", syncMotion);
syncMotion();
