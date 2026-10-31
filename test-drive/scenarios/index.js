import {matchesObservation} from './observation.js';
const ids = new Set(['taskbar','launcher','switcher','task-view','transfer','picker','preview-states','snap','notifications','settings','files','system','window-menu','confirmation','application-actions','status-recovery']);
const waitFor = (host, predicate, epoch) => new Promise(resolve => {
  let done=false, unsubscribe=()=>{};
  const finish=value=>{if(done)return;done=true;clearTimeout(timer);unsubscribe();resolve(value);};
  const check=s=>{if(s.epoch!==epoch) finish(false); else if(predicate(s)) finish(true);};
  const timer=setTimeout(()=>finish(false),10000);
  unsubscribe=host.subscribe(check); check(host.getSnapshot());
});
export async function loadScenario(id, host) {
  if (!ids.has(id)) return {ok:false,reason:`Unknown scenario “${String(id)}”. The default desktop is available.`};
  const response=await fetch(new URL(`./${id}.json`,import.meta.url));
  if(!response.ok) throw new Error(`Could not load scenario ${id}`);
  const scenario=await response.json();
  if(scenario.id!==id) throw new Error('Scenario identity mismatch');
  let snapshot=host.getSnapshot();
  const seed=scenario.initialExternalFacts;
  const matchesSeed=s=>s.activeWorkspace===seed.activeWorkspace && JSON.stringify(s.windows)===JSON.stringify(seed.windows) && JSON.stringify(s.workspaces)===JSON.stringify(seed.workspaces);
  if(!matchesSeed(snapshot)) {
    host.reset(seed); snapshot=host.getSnapshot();
    if(!await waitFor(host,s=>s.binding && s.presentation?.actionable && s.presentation.applied?.bar===s.presentation.publication && s.presentation.controls?.bar?.includes('bar:pin:warlock-editor'), snapshot.epoch)) return {ok:false,scenario,reason:'The seeded desktop did not become ready. Reset the desktop and try again.'};
  }
  snapshot=host.getSnapshot();
  if(id==='taskbar') { const ok=await waitFor(host,s=>matchesObservation(s, scenario.expectedObservations, snapshot.epoch),snapshot.epoch); return ok ? {ok:true,scenario} : {ok:false,scenario,reason:'The taskbar renderer has not acknowledged its presentation.'}; }
  if (scenario.faultPolicy) host.setFault(scenario.faultPolicy);
  const admitted=await host.invoke(scenario.entryIntent);
  if(!admitted) { if (scenario.faultPolicy) host.setFault('success'); return {ok:false,scenario,reason:`The ${scenario.title} entry is unavailable in this desktop. The default desktop remains available.`}; }
  const observed=await waitFor(host,s=>s.presentation?.publication!==snapshot.presentation?.publication && matchesObservation(s,scenario.expectedObservations,snapshot.epoch),snapshot.epoch);
  if (scenario.faultPolicy) host.setFault('success');
  return observed ? {ok:true,scenario} : {ok:false,scenario,reason:`The ${scenario.title} surface did not open. Reset the desktop and try again.`};
}
