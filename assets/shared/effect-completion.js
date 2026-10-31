/** Watch one decorative animation. Completion never implies an operation result. */
export function watchEffectCompletion({target, animationName, cycle, duration, onComplete, signal}) {
 let done = false;
 let timer;
 const finish = (reason) => {
  if (done) return;
  done = true;
  clearTimeout(timer);
  target.removeEventListener('animationend', ended);
  target.removeEventListener('animationcancel', cancelled);
  signal?.removeEventListener('abort', aborted);
  document.removeEventListener('visibilitychange', visibility);
  onComplete({cycle, reason});
 };
 const valid = (event) => event.target === target && event.animationName === animationName && target.dataset.effectCycle === String(cycle);
 const ended = (event) => { if (valid(event)) finish('end'); };
 const cancelled = (event) => { if (valid(event)) finish('cancel'); };
 const aborted = () => finish('cancel');
 const visibility = () => { if (document.hidden) finish('cancel'); };
 document.addEventListener('visibilitychange', visibility);
 target.addEventListener('animationend', ended);
 target.addEventListener('animationcancel', cancelled);
 signal?.addEventListener('abort', aborted, {once:true});
 if (signal?.aborted || duration <= 0 || document.hidden) finish('cancel');
 else timer = setTimeout(() => { if (target.dataset.effectCycle === String(cycle)) finish('watchdog'); else finish('cancel'); }, Math.max(0, duration) + 100);
 return () => finish('cancel');
}
