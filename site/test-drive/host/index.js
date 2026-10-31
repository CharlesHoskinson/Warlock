import {BRIDGE_VERSION, FRAME_IDS, FAULT_POLICIES, isEnvelope} from '../contracts.js';

const copy = value => structuredClone(value);
const freeze = value => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freeze); Object.freeze(value);
  }
  return value;
};
const initial = () => ({schema:1, epoch:0, binding:null, viewScope:{id:'1',generation:'1'}, output:{x:0,y:0,width:1280,height:720}, workArea:{x:0,y:56,width:1280,height:664}, activeWorkspace:'1', workspaces:[{id:'1',name:'1'},{id:'2',name:'2'},{id:'3',name:'3'}], windows:[{"id":"1","incarnation":"1","label":"Editor","title":"Editor","owner":null,"application":"warlock-editor","workspace":"1","minimized":false,"focused":true,"geometry":{"x":16,"y":72,"width":610,"height":620}},{"id":"2","incarnation":"2","label":"Browser","title":"Browser","owner":null,"application":"warlock-browser","workspace":"1","minimized":false,"focused":false,"geometry":{"x":642,"y":72,"width":622,"height":620}},{"id":"3","incarnation":"3","label":"Terminal","title":"Terminal","owner":null,"application":"warlock-terminal","workspace":"2","minimized":true,"focused":false,"geometry":{"x":16,"y":72,"width":610,"height":620}},{"id":"4","incarnation":"4","label":"Notes","title":"Notes","owner":null,"application":"warlock-editor","workspace":"2","minimized":false,"focused":false,"geometry":{"x":642,"y":72,"width":622,"height":620}}], activationHistory:['1','2','4','3'], appearance:{theme:'night',textScale:100,effectsOff:false,reducedTransparency:false}, motion:{applied:null}, popupPlacement:null});

/** Owns simulated external state; the Elm controller owns interaction policy. */
export function createHost({frames = {}, onSnapshot = () => {}, onDiagnostic = () => {}} = {}) {
  let state = initial(), epoch = 0, abort = new AbortController(), started = false, destroyed = false, fault = 'success', preview = null;
  const handlers = new Map(), listeners = new Set(), ready = new Set(), trace = [], batches = new Map();
  let presentation = null, applied = new Set(), highest = 0n, pointerSerial = 0, revision = 1, topologyRevision = 1, sequence = 0n;
  const issued = new Set();
  const timers = new Set();
  const cancelTimers = () => { for (const timer of timers) clearTimeout(timer); timers.clear(); };
  const schedule = fn => { const captured = epoch; const timer = setTimeout(() => { timers.delete(timer); if (captured === epoch && !abort.signal.aborted && !destroyed) fn(); }, fault === 'delayed' ? 750 : 0); timers.add(timer); };
  let observationBarrier = null;
  const observe = () => { observationBarrier={projection:false,geometry:false,after:null}; deliver('controller','receiveNative',{protocolVersion:3,kind:'host-refresh'}); };
  const viewport = (width,height) => { if (!Number.isFinite(width) || !Number.isFinite(height)) return; state.output = {x:0,y:0,width:Math.max(320,Math.round(width)),height:Math.max(240,Math.round(height))}; const scale = Number(state.appearance?.textScale || state.appearance?.values?.textScale || 100) / 100; const bar = Math.round(48 * scale + 8); state.workArea = {x:0,y:bar,width:state.output.width,height:Math.max(1,state.output.height-bar)}; };
  if (typeof innerWidth === 'number') viewport(innerWidth,innerHeight);
  const tile = workspace => {
    const rows=state.windows.filter(w=>w.workspace===workspace && !w.minimized && !w.owner && (!w.placementMode || w.placementMode==='tiled'));
    const area=state.workArea, gap=14, count=rows.length; if (!count) return;
    const width=Math.max(1,(area.width-gap*(count+1))/count);
    rows.forEach((w,i)=>{ const left=Math.round(area.x+gap+i*(width+gap)), right=Math.round(area.x+gap+i*(width+gap)+width); w.geometry={x:left,y:area.y+gap,width:Math.max(1,right-left),height:Math.max(1,area.height-2*gap)}; w.placementMode='tiled'; });
  };
  const tileAll = () => state.workspaces.forEach(w => tile(w.id));
  tileAll();
  const diag = (kind, detail) => { const item = {epoch,kind,detail}; trace.push(item); if (trace.length > 200) trace.shift(); onDiagnostic(item); };
  const snapshot = () => { const value=copy(state); const active=value.windows.find(w=>w.focused)?.application; value.windows.forEach(w=>{w.activeApplication=!!active && w.application===active; w.placementMode ||= 'tiled';}); return freeze(value); };
  const publish = () => { const value = snapshot(); onSnapshot(value); for (const listener of listeners) listener(value); };
  const frameWindow = id => frames[id]?.contentWindow || frames[id] || null;
  const send = (id, kind, payload) => frameWindow(id)?.postMessage({bridgeVersion:BRIDGE_VERSION,epoch,frameId:id,kind,payload}, location.origin);
  const deliver = (id, method, value) => send(id,'deliver',{method,value});
  // The Bar receives a typed observed focus fact, separate from application activity.
  const groupMatches = (row, application) => row.id === 'bar:pin:'+application || row.id === 'bar:group:application:'+application;
  const rendererFrame = (id, frame) => id !== 'bar' ? frame : {...frame, bar:(frame.bar || []).map(row => ({...row, activeApplication:state.windows.some(w => w.focused && !w.minimized && groupMatches(row,w.application)), windowFocused:state.windows.some(w => w.focused && !w.minimized && (w.workspace === state.activeWorkspace || w.pinned) && groupMatches(row,w.application))}))};
  const context = () => {
    const signal = abort.signal, captured = epoch;
    const live = () => !signal.aborted && captured === epoch && !destroyed;
    return Object.freeze({readWorld:snapshot, transact(operation) {
      if (!live() || typeof operation !== 'function') return false;
      const next = operation(copy(state));
      if (!next || typeof next !== 'object' || next.epoch !== epoch) return false;
      const previousScale = state.appearance?.textScale;
      state = copy(next);
      if (state.appearance?.textScale !== previousScale) {
        viewport(state.output.width,state.output.height); tileAll(); revision++; topologyRevision++;
        deliver('controller','receiveTopology',{viewProtocol:2,kind:'view-topology',revision:String(topologyRevision),views:[state.viewScope],locations:[{scope:state.viewScope,box:[0,0,state.output.width,state.output.height]}]});
        if (presentation?.lease) deliver('controller','receiveReflow',{scope:state.viewScope,lease:presentation.lease});
      }
      publish(); return true;
    }, reply(event) { if (live()) deliver('controller','receiveNative',event); }, publishObservation(event) { if (live()) deliver('controller','receiveNative',event); }, clock:Object.freeze({now:() => performance.now()}), signal});
  };
  let nextIncarnation = 5n, contextAnchor = null, currentQuery = '';
  let pendingFocus = null, issuedFocus = null, pendingOpener = null, leaseOpener = null, systemMotion = 'full', motionSerial = 0, switchChord = null;
  // This is the same eligibility reported in geometry-facts, not a shortcut
  // around the controller's capability checks.
  const geometryEligible = w => !!w && !w.minimized && !w.owner && (w.placementMode === 'floating' || w.placementMode === 'snapped' || (w.placementMode === 'maximized' && ['floating','snapped'].includes(w.restorePlacementMode)));
  let noticeTimer;
  const unavailable = message => {
    diag('entry-unavailable', message);
    const status = typeof document === 'undefined' ? null : document.getElementById('startup');
    if (!status || (!status.hidden && !status.dataset.hostNotice)) return;
    clearTimeout(noticeTimer); status.dataset.hostNotice = 'true'; status.textContent = message; status.hidden = false;
    noticeTimer = setTimeout(() => { status.hidden = true; delete status.dataset.hostNotice; }, 4000);
  };
  const routeRequest = request => {
    if (request.kind === 'host-reconnect') { reconnect(); return; }
    if (request.kind === 'projection-request') {
      if (observationBarrier) { observationBarrier.projection=true; if (observationBarrier.geometry) observationBarrier.after=highest; }
      context().reply({protocolVersion:3,kind:'action-projection',binding:request.binding,requestId:request.requestId,context:{lifetime:'1',epoch:'1',output:'1',revision:String(revision)},scene:{revision:String(revision),focused:state.windows.find(w=>w.focused)?.incarnation || null,windows:state.windows.map(w=>({incarnation:w.incarnation,label:w.label,owner:w.owner,application:w.application,minimized:w.minimized,available:true}))}}); return;
    }
    if (request.kind === 'geometry-attach') { context().reply({protocolVersion:3,kind:'geometry-attached',geometryProtocol:3,binding:request.binding,requestId:request.requestId,capabilities:{observe:true,effects:true,effectProtocol:2,operations:['maximize','restore-geometry','snap','transfer-workspace','pin','unpin'],placementCapacity:256,canonicalScene:false}}); return; }
    if (request.kind === 'geometry-facts-request') {
      if (observationBarrier) { observationBarrier.geometry=true; if (observationBarrier.projection) observationBarrier.after=highest; }
      const area = state.workArea, rect = [area.x,area.y,area.width,area.height];
      const windows = state.windows.map(w => { const g=w.geometry, box=[g.x,g.y,g.width,g.height]; const floating=w.placementMode==='floating' || w.placementMode==='snapped' || (w.placementMode==='maximized' && ['floating','snapped'].includes(w.restorePlacementMode)); const eligible=geometryEligible(w), mode=w.maximized?'maximized':'ordinary';
        const ordinary=w.restoreGeometry || g, restore=[ordinary.x,ordinary.y,ordinary.width,ordinary.height];
        const projection=(r,visual) => ({logical:r,visual:visual?r:null,real:r,configure:[r[2],r[3]]});
        return {incarnation:w.incarnation,owner:w.owner,workspace:w.workspace,workspaceGeneration:w.workspace,monitor:'0',outputOwnershipGeneration:'1',workAreaRevision:String(revision),workArea:rect,logicalGeometry:box,visualGeometry:box,nativeMode:mode,clientMode:mode,minimized:w.minimized,floating,grouped:false,fixedSize:false,constrainedSize:true,geometryEligible:eligible,ordinaryPlacementKnown:!!w.restoreGeometry,capabilities:{maximize:eligible&&!w.maximized,restoreGeometry:eligible&&!!w.maximized&&!!w.restoreGeometry},sizePolicy:{inputs:{profile:'wayland-zero-origin-v1',rawMinimum:[1,1],rawMaximum:[0,0],layoutMinimum:[1,1],layoutMaximum:[2147483647,2147483647],geometryOrigin:[0,0],reservedTopLeft:[0,0],reservedBottomRight:[0,0],monitorScale:1},maximize:projection(rect,false),restoreGeometry:projection(restore,true)},pin:{pinned:!!w.pinned,eligible:eligible && w.placementMode==='floating' && (w.workspace===state.activeWorkspace || !!w.pinned) && !w.maximized}}; });
      try { const minimum=BigInt(request.minimumWatermark || 0); if (minimum >= sequence) sequence=minimum; } catch { return; }
      context().reply({protocolVersion:3,kind:'geometry-facts',geometryProtocol:3,binding:request.binding,requestId:request.requestId,sequence:String(++sequence),revision:String(revision),outputGeneration:'1',facts:{focused:state.windows.find(w=>w.focused)?.incarnation || null,inputBlocked:false,windows,workspaces:state.workspaces.map(w=>({identity:w.id,generation:w.id,monitor:'0',outputOwnershipGeneration:'1'})),activeWorkspace:state.activeWorkspace}}); return;
    }
    if (request.kind === 'activation-history-request') { context().reply({protocolVersion:3,kind:'activation-history',binding:request.binding,requestId:request.requestId,context:{lifetime:'1',epoch:'1',output:'1',revision:String(revision)},roots:state.activationHistory.filter(id=>state.windows.some(w=>w.incarnation===id))}); return; }
    if (request.kind === 'workspace-navigation-recover') { context().reply({protocolVersion:3,kind:'workspace-navigation-recovery',workspaceProtocol:1,binding:request.binding,record:null}); return; }
    if (request.kind === 'window-effect' || request.kind === 'workspace-navigation') {
      const key=JSON.stringify([request.binding,request.kind,request.intent]); if (issued.has(key)) return; issued.add(key);
      const policy=fault;
      if (policy==='connection-loss') { deliver('controller','receiveNative',{protocolVersion:3,kind:'host-disconnected'}); return; }
      schedule(() => {
        let status=policy==='refusal'?'Refused':policy==='unknown'||policy==='stale'?'Unknown':'Committed';
        const intent=request.intent, win=state.windows.find(w=>w.incarnation===intent.incarnation);
        if (!intent?.context || intent.context.lifetime!=='1' || intent.context.epoch!=='1' || intent.context.output!=='1' || intent.context.revision!==String(revision) || JSON.stringify(request.binding)!==JSON.stringify(state.binding)) status='Refused';
        if (request.kind==='workspace-navigation' && (intent.source?.identity!==state.activeWorkspace || !state.workspaces.some(w=>w.id===intent.destination?.identity && w.id===intent.destination?.generation))) status='Refused';
        if (request.kind==='window-effect' && (!win || !['activate','restore','minimize','maximize','restore-geometry','snap','transfer-workspace','pin','unpin'].includes(intent.operation) || intent.context?.revision !== String(revision))) status='Refused';
        if ((intent.operation==='pin' || intent.operation==='unpin') && (!win || win.placementMode!=='floating' || win.minimized || win.owner || win.maximized || (win.workspace!==state.activeWorkspace && !win.pinned) || !!win.pinned !== (intent.operation==='unpin'))) status='Refused';
        if (intent.operation==='transfer-workspace' && win?.pinned) status='Refused';
        if (intent.operation==='snap' && (!Array.isArray(intent.placement?.geometry) || intent.placement.workAreaRevision!==String(revision))) status='Refused';
        if (intent.operation==='transfer-workspace' && (!win || intent.transfer?.source!==win.workspace || intent.transfer.sourceGeneration!==win.workspace || !state.workspaces.some(w=>w.id===intent.transfer.destination))) status='Refused';
        if (status==='Committed') {
          if (request.kind==='workspace-navigation') { state.activeWorkspace=intent.destination.identity; state.windows.forEach(w=>w.focused=false); }
          else if (intent.operation==='minimize') { win.minimized=true; win.focused=false; tile(win.workspace); }
          else if (intent.operation==='maximize') { if (!win.restoreGeometry) { win.restoreGeometry={...win.geometry}; win.restorePlacementMode=win.placementMode || 'tiled'; } win.geometry={...state.workArea}; win.placementMode='maximized'; win.maximized=true; }
          else if (intent.operation==='restore-geometry' && win.restoreGeometry) { win.geometry=win.restoreGeometry; delete win.restoreGeometry; win.placementMode=win.restorePlacementMode || 'floating'; delete win.restorePlacementMode; win.maximized=false; tile(win.workspace); }
          else if (intent.operation==='snap') { const [x,y,width,height]=intent.placement.geometry; if (!win.restoreGeometry) { win.restoreGeometry={...win.geometry}; win.restorePlacementMode=win.placementMode || 'tiled'; } win.geometry={x,y,width,height}; win.placementMode='snapped'; win.maximized=false; }
          else if (intent.operation==='transfer-workspace') { const source=win.workspace; win.workspace=intent.transfer.destination; win.focused=false; tile(source); tile(win.workspace); }
          else if (intent.operation==='pin' || intent.operation==='unpin') win.pinned=intent.operation==='pin';
          else { if (!win.pinned) state.activeWorkspace=win.workspace; state.windows.forEach(w=>w.focused=false); win.minimized=false; win.focused=true; tile(win.workspace); state.activationHistory=[win.incarnation,...state.activationHistory.filter(id=>id!==win.incarnation)]; }
          revision++; publish();
        }
        const reason=status==='Committed'?'committed':status==='Refused'?'refused':'delivery-unproven';
        if (request.kind==='window-effect') context().reply({protocolVersion:3,kind:'effect-outcome',effectProtocol:request.effectProtocol,binding:request.binding,intent,status,reason,revision:String(revision),outputGeneration:'1'});
        else context().reply({protocolVersion:3,kind:'workspace-navigation-outcome',workspaceProtocol:1,binding:request.binding,intent,status,reason});
        if (status==='Committed') observe();
      }); return;
    }
    if (request.kind === 'pointer-ownership-request') { context().reply({protocolVersion:3,kind:'pointer-ownership',ownershipProtocol:1,binding:request.binding,requestId:request.requestId,serial:String(++pointerSerial),state:'idle',owner:null}); return; }
    const handler = handlers.get(request.kind);
    if (handler) {
      const policy = fault, base = context();
      const mutation = /(?:-write|-effect|-launch|-open|-set)$/.test(request.kind);
      const key = JSON.stringify([request.binding, request.kind, request.requestId != null ? ['requestId', request.requestId] : ['intent', request.intent || request.proposal]]);
      if (mutation && issued.has(key)) return;
      if (mutation) issued.add(key);
      if (mutation && policy === 'connection-loss') { deliver('controller','receiveNative',{protocolVersion:3,kind:'host-disconnected'}); return; }
      schedule(() => {
        const blocked = mutation && ['refusal','unknown','stale'].includes(policy);
        const serviceContext = Object.freeze({...base, fault:policy,
          transact: blocked ? () => false : base.transact,
          reply(event) {
            if (blocked && event && typeof event === 'object') {
              event = copy(event);
              const outcome = event.outcome || event;
              if ('status' in outcome) outcome.status = policy === 'refusal' ? 'Refused' : 'Unknown';
              if ('reason' in outcome) outcome.reason = policy === 'refusal' ? 'refused' : 'delivery-unproven';
            }
            base.reply(event);
          }});
        try {
          // Launch dispatches an observation directly; do not run it for an unresolved submission.
          if (blocked && request.kind === 'application-launch') base.reply({protocolVersion:3,kind:'application-launch-outcome',binding:request.binding,outcome:{catalogProtocol:1,kind:'launch-outcome',intent:request.intent,status:policy === 'refusal' ? 'Refused' : 'Unknown',reason:policy === 'refusal' ? 'native-entry-unavailable' : 'submission-not-confirmed'}});
          else handler(copy(request),serviceContext);
        } catch (error) { diag('service-error',{kind:request.kind,message:String(error)}); }
      });
    }
    else diag('unhandled-request',request.kind);
  };
  const restart = seed => {
    abort.abort(); cancelTimers(); abort = new AbortController(); epoch++;
    ready.clear(); batches.clear(); issued.clear(); contextAnchor=null; currentQuery=''; highest=0n; presentation=null; pendingFocus=null; issuedFocus=null; pendingOpener=null; leaseOpener=null; observationBarrier=null; applied.clear(); pointerSerial=0; revision=1; topologyRevision=1; sequence=0n;
    const admittedOutput = {...state.output}; switchChord = null;
    state = {...initial(), ...(seed ? copy(seed) : {}), epoch, binding:null, presentation:null, popupPlacement:null};
    nextIncarnation = state.windows.reduce((n,w)=>{ try { const id=BigInt(w.incarnation); return id>=n?id+1n:n; } catch { return n; } }, nextIncarnation);
    viewport(admittedOutput.width,admittedOutput.height);
    state.windows.forEach(w => { if (w._drag) { Object.assign(w, w._drag.original); delete w._drag; } });
    tileAll();
    for (const id of FRAME_IDS) { const frame=frames[id]; if (frame?.addEventListener && frame?.src) { frame.addEventListener('load', () => send(id,'bind',null), {once:true}); frame.src=frame.src; } else send(id,'bind',null); }
    publish();
  };
  const reconnect = () => restart(state);

  const handleNative = (id, raw) => {
    if (typeof raw !== 'string' || raw.length > 131072) return;
    let packet; try { packet = JSON.parse(raw); } catch { diag('invalid-json',id); return; }
    if (!packet || typeof packet !== 'object' || Array.isArray(packet) || typeof packet.kind !== 'string') return;
    if (id === 'controller' && packet.kind === 'host-ready' && packet.protocolVersion === 3) {
      const scope = state.viewScope;
      deliver('controller','receiveTopology',{viewProtocol:2,kind:'view-topology',revision:String(topologyRevision),views:[scope],locations:[{scope,box:[state.output.x,state.output.y,state.output.width,state.output.height]}]});
      state.binding = {lifetime:'1', session:String(epoch + 1), frontend:'1'};
      deliver('controller','receiveNative',{protocolVersion:3,kind:'attached',binding:state.binding});
      deliver('controller','receiveNative',{protocolVersion:3,kind:'host-geometry-negotiate'});
      deliver('controller','receiveNative',{protocolVersion:3,kind:'pointer-ownership',ownershipProtocol:1,binding:state.binding,requestId:'1',serial:'1',state:'idle',owner:null}); publish();
      deliver('controller','receiveNative',{protocolVersion:3,kind:'host-motion-preference',serial:String(++motionSerial),profile:systemMotion,source:'portal'}); diag('controller-ready',null); return;
    }
    if ((id === 'bar' || id === 'popup') && packet.kind === 'presentation-ready' && packet.surfaceProtocol === 2) { ready.add(id); if (presentation) deliver(id,'receivePresentation',rendererFrame(id,presentation)); diag('renderer-ready',id); return; }
    if (id === 'controller' && packet.kind === 'view-commit' && packet.viewProtocol === 1) {
      const projection = packet.projection, frame = projection?.frame;
      if (!frame || !Array.isArray(packet.requests) || !Array.isArray(packet.focus) || projection.revision !== String(topologyRevision)) return;
      let number; try { number = BigInt(frame.publication); } catch { return; }
      const prior = batches.get(raw);
      if (prior) { deliver('controller','receiveBatchDisposition',prior); return; }
      if (number < highest) return;
      const scope = projection.popupOwner || projection.focusOwner || state.viewScope;
      if (scope.id !== state.viewScope.id || scope.generation !== state.viewScope.generation) return;
      if (packet.requests.length && packet.requests.some(request => JSON.stringify(request.binding) !== JSON.stringify(state.binding))) return;
      if (packet.requests.length && number <= highest) return;
      // Keep semantic identities, not generation-specific DOM IDs. A successor
      // publication can arrive before either presentation or focus is applied.
      // An explicit focus effect supersedes the previous intent.
      if (frame.mode !== 'closed' && pendingOpener) {
        leaseOpener = {lease:frame.lease, id:pendingOpener}; pendingOpener = null;
      }
      if (packet.focus.length) {
        const surface = frame.mode === 'closed' ? 'bar' : 'popup';
        let ids = packet.focus.map(target => (frame[surface] || []).find(row => row.domId === target)?.id).filter(Boolean);
        if (!ids.length && surface === 'bar' && leaseOpener?.lease === presentation?.lease) ids = [leaseOpener.id];
        pendingFocus = ids.length ? {surface, ids} : null;
      } else if (pendingFocus && (frame.mode === 'closed' ? 'bar' : 'popup') !== pendingFocus.surface) {
        pendingFocus = null;
      }
      issuedFocus = null;
      if (presentation?.mode === 'switcher' && frame.mode !== 'switcher' && switchChord) {
        switchChord.queue.length = 0; switchChord = null;
      }
      highest = number; presentation = frame; applied.clear();
      if (observationBarrier?.after != null && number > observationBarrier.after) observationBarrier=null;
      if (frame.appearance && [100,125,150,200].includes(frame.appearance.textScale)) {
        const oldScale=state.appearance?.textScale; state.appearance=copy(frame.appearance);
        if (oldScale !== state.appearance.textScale) { viewport(state.output.width,state.output.height); tileAll(); }
      }
      if (state.motion?.profile && frame.motion === state.motion.profile) state.motion={...state.motion,applied:frame.motion};
      state.presentation = {actionable:true, publication:frame.publication, lease:frame.lease, mode:frame.mode, applied:{}, controls:{bar:(frame.bar || []).map(r=>r.id),popup:(frame.popup || []).map(r=>r.id)}, selectedControls:[...(frame.bar || []),...(frame.popup || [])].filter(r=>r.checked === true).map(r=>r.id), query:currentQuery, operationStatus:(frame.status || '').match(/\b(Pending|Submitted|Refused|Unknown)\b/i)?.[0] || null};
      const width=Math.min(700,state.output.width-8), height=Math.min(420,state.output.height-state.workArea.y-4), anchor=contextAnchor || {x:50,y:state.workArea.y};
      const x=Math.max(4,Math.min(anchor.x,state.output.width-width-4)); let y=anchor.y; if (y+height>state.output.height-4 && y-height>=4) y-=height; y=Math.max(4,Math.min(y,state.output.height-height-4));
      state.popupPlacement = frame.mode === 'closed' ? null : {open:true,x,y,width,height};
      if (frame.mode==='closed') contextAnchor=null;
      publish(); diag('presentation-admitted',{actionable:true,publication:frame.publication});
      for (const renderer of ['bar','popup']) if (ready.has(renderer)) deliver(renderer,'receivePresentation',rendererFrame(renderer,frame));
      if (packet.requests.length) {
        const certificate = {viewProtocol:1,kind:'batch-disposition',disposition:'admitted',scope,revision:projection.revision,publication:frame.publication,lease:frame.lease,binding:state.binding,batch:raw};
        batches.set(raw,certificate); if (batches.size > 64) batches.delete(batches.keys().next().value);
        deliver('controller','receiveBatchDisposition',certificate);
      }
      for (const request of packet.requests) routeRequest(request);
      for (const surface of ['bar','popup']) { const recipient={scope:state.viewScope,surface}; deliver(surface,'receiveAnnouncement',{announcementProtocol:1,kind:'announcement-projection',recipient,announcer:projection.announcer,publication:frame.publication,lease:frame.lease,message:projection.announcement,deliver:!!projection.announcement && JSON.stringify(projection.announcer)===JSON.stringify(recipient)}); }
      diag('view-commit',{publication:frame.publication,requests:packet.requests.map(r=>r.kind)}); return;
    }
    if ((id === 'bar' || id === 'popup') && packet.surfaceProtocol === 2) {
      if (!presentation || packet.publication !== presentation.publication || packet.lease !== presentation.lease) return;
      if (packet.kind === 'presentation-applied') { applied.add(id); state.presentation.applied[id]=presentation.publication; publish(); if (pendingFocus?.surface === id) { const targets=pendingFocus.ids.map(controlId => presentation[id]?.find(row => row.id === controlId && row.enabled)?.domId).filter(Boolean); if (targets.length === pendingFocus.ids.length) { issuedFocus = {surfaceProtocol:2,kind:'surface-focus',publication:presentation.publication,lease:presentation.lease,targets}; deliver(id,'receiveFocus',issuedFocus); } } return; }
      if (packet.kind === 'focus-applied') { if (id !== pendingFocus?.surface || !issuedFocus || !Array.isArray(packet.targets) || !packet.targets.length || !packet.targets.every(target => issuedFocus.targets.includes(target))) return; pendingFocus = null; issuedFocus = null; diag('focus-applied',packet); return; }
      if (!applied.has(id)) return;
      if (['surface-action','surface-query','surface-context','surface-notification-focus','surface-menu-navigation'].includes(packet.kind)) {
        if (id === 'bar' && packet.kind === 'surface-action') pendingOpener = packet.id;
        if (packet.kind==='surface-query') { currentQuery=packet.query; state.presentation.query=currentQuery; }
        if (packet.kind==='surface-context') { const rect=frames[id]?.getBoundingClientRect?.() || {left:0,top:0}; contextAnchor={x:Math.round(rect.left+packet.x),y:Math.round(rect.top+packet.y)}; }
        deliver('controller','receiveAction',{viewProtocol:1,kind:'view-action',scope:state.viewScope,action:packet}); return;
      }
    }
    if (id === 'popup' && packet.kind === 'preview-commands' && preview) { preview(packet,context()); return; }
    diag('unrouted-native-message',{frame:id,packet});
  };
  const receive = event => {
    const packet = event.data;
    if (event.origin !== location.origin || !isEnvelope(packet) || packet.epoch !== epoch || event.source !== frameWindow(packet.frameId)) return;
    if (packet.kind === 'bound') { ready.add(packet.frameId); return; }
    if (packet.kind === 'native') handleNative(packet.frameId,packet.payload);
  };
  const activateControl = (surface,id,contextMenu=false,invocation=null) => {
    const rows = presentation?.[surface], control = rows?.find(row=>row.id===id);
    if (!control?.enabled || !applied.has(surface)) return false;
    if (surface === 'bar' && !contextMenu) pendingOpener = id;
    const action={surfaceProtocol:2,kind:contextMenu?'surface-context':'surface-action',surface,publication:presentation.publication,lease:presentation.lease,id,trigger:invocation?.trigger || 'keyboard'};
    if (contextMenu) {
      const anchor=invocation?.anchor || {x:50,y:state.workArea.y};
      contextAnchor={x:Math.round(anchor.x),y:Math.round(anchor.y)};
      Object.assign(action,contextAnchor);
    }
    deliver('controller','receiveAction',{viewProtocol:1,kind:'view-action',scope:state.viewScope,action}); return true;
  };
  const bind = () => { for (const id of FRAME_IDS) if (frameWindow(id)) send(id,'bind',null); };
  return {
    registerService(kind,handler) { if (typeof kind !== 'string' || typeof handler !== 'function' || handlers.has(kind)) throw new TypeError('A unique service kind and handler are required'); handlers.set(kind,handler); return () => handlers.delete(kind); },
    registerPreview(provider) { if (typeof provider !== 'function') throw new TypeError('A preview handler is required'); preview = provider; return () => { if (preview === provider) preview = null; }; },
    start() { if (destroyed || started) return; started = true; addEventListener('message',receive); bind(); publish(); },
    reset(seed) { if (!destroyed) restart(seed); },
    getSnapshot:snapshot,
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
    async invoke(intent, invocation) {
      if (invocation !== undefined && (intent !== 'window-menu' || !invocation || !['pointer','keyboard'].includes(invocation.trigger) || typeof invocation.windowId !== 'string' || typeof invocation.incarnation !== 'string' || !invocation.anchor || !Number.isFinite(invocation.anchor.x) || !Number.isFinite(invocation.anchor.y))) return false;
      const invocationEpoch=epoch;
      const capturedWindow = () => invocation && epoch===invocationEpoch && state.windows.find(w=>w.id===invocation.windowId && w.incarnation===invocation.incarnation && w.focused && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned));
      if (invocation && !capturedWindow()) return false;
      const ids = {launcher:'bar:applications', 'task-view':'bar:overview', switcher:'bar:switcher', notifications:'bar:notifications', settings:'bar:settings', files:'bar:files', system:'bar:system'};
      // Admission and submission are synchronous: no successor publication can
      // invalidate the acknowledged row between the check and its stamped action.
      const click = (surface,predicate,menu=false,context=null,valid=()=>true) => new Promise(resolve => {
        let stop=()=>{};
        const finish=value=>{clearTimeout(timer);stop();resolve(value);};
        const timer=setTimeout(()=>finish(false),5000);
        const check=()=>{
          if (epoch!==invocationEpoch || (invocation && !capturedWindow()) || !valid()) { finish(false); return; }
          const row=presentation?.[surface]?.find(r=>r.enabled && predicate(r));
          if (row && applied.has(surface) && !observationBarrier) { stop(); clearTimeout(timer); resolve(activateControl(surface,row.id,menu,context)); }
        };
        stop=this.subscribe(check); check();
      });
      const exact=id=>row=>row.id===id;
      if (intent==='taskbar') return !!presentation && applied.has('bar');
      if (ids[intent]) return click('bar',exact(ids[intent]));
      if (intent==='picker' || intent==='preview-states') { const focused=state.windows.find(w=>w.focused && !w.minimized); return !!focused && click('bar',r=>groupMatches(r,focused.application)); }
      if (intent==='transfer') return await this.invoke('task-view') && await click('popup',r=>r.id.startsWith('overview:transfer:'));
      if (intent==='confirmation') return await this.invoke('system') && await click('popup',r=>r.id==='system:reboot:0' || r.id==='system:poweroff:0');
      if (intent==='status-recovery') return this.invoke('files');
      if (intent==='window-menu' || intent==='snap') {
        const focused=invocation ? capturedWindow() : state.windows.find(w=>w.focused && !w.minimized);
        if (intent === 'snap' && !geometryEligible(focused)) { unavailable('Snap layouts are unavailable for this window.'); return false; }
        if (!focused) return false;
        const group=presentation?.bar?.find(r=>groupMatches(r,focused.application));
        const targetValid=()=>!!state.windows.find(w=>w.id===focused.id && w.incarnation===focused.incarnation && w.focused && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned));
        if (!group || !await click('bar',exact(group.id),true,invocation,targetValid)) return false;
        const expected=epoch;
        for (let i=0;i<250 && epoch===expected;i++) {
          if (invocation && !capturedWindow()) return false;
          if (presentation?.mode==='picker' && applied.has('popup')) {
            if (!await click('popup',exact('family:'+focused.incarnation),true,invocation,targetValid)) return false;
          }
          if (presentation?.mode==='menu' && applied.has('popup')) {
            if (invocation && !capturedWindow()) return false;
            if (intent==='window-menu') return true;
            if (!geometryEligible(state.windows.find(w=>w.incarnation===focused.incarnation && w.focused)) || !await click('popup',r=>r.id.startsWith('control:snap-open'),false,null,()=>targetValid() && geometryEligible(state.windows.find(w=>w.incarnation===focused.incarnation)))) return false;
            for (let j=0;j<250 && epoch===expected;j++) {
              if (presentation?.mode==='snap' && applied.has('popup')) return true;
              await new Promise(resolve=>setTimeout(resolve,20));
            }
            return false;
          }
          await new Promise(resolve=>setTimeout(resolve,20));
        }
        return false;
      }
      if (intent.startsWith('application-actions:') || intent.startsWith('new-instance:') || intent==='application-actions') {
        const app=intent==='application-actions' ? (state.windows.find(w=>w.focused)?.application || 'warlock-editor') : intent.slice(intent.indexOf(':')+1).replace(/^bar:(?:pin:|group:application:)/,'');
        if (!await this.invoke('launcher') || !await click('popup',exact('entry:'+app),true)) return false;
        return !intent.startsWith('new-instance:') || click('popup',r=>r.id.startsWith('control:new-instance:'));
      }
      return false;
    },
    dispatchInput(input) {
      if (input?.kind === 'popup-dismiss' || input?.kind === 'outside-press') {
        if (input.epoch !== epoch || presentation?.mode === 'closed' || !presentation || input.lease !== presentation.lease || (input.kind === 'outside-press' && input.publication !== presentation.publication) || (input.kind === 'popup-dismiss' && (input.scope?.id !== state.viewScope.id || input.scope?.generation !== state.viewScope.generation))) return false;
        deliver('controller','receiveDismiss',{scope:state.viewScope,lease:presentation.lease}); return true;
      }
      if (input?.kind === 'placement') {
        const win=state.windows.find(w=>w.id===input.windowId && w.incarnation===input.incarnation);
        const g=input.geometry, area=state.workArea, placementMode=input.placementMode || (input.zone === 'maximize' ? 'maximized' : ['left','right','top-left','top-right','bottom-left','bottom-right'].includes(input.zone) ? 'snapped' : null);
        if (input.epoch!==epoch || !win || win.minimized || !['snapped','maximized'].includes(placementMode) || !g || !['x','y','width','height'].every(k=>Number.isFinite(g[k])) || g.width<=0 || g.height<=0 || g.x<area.x || g.y<area.y || g.x+g.width>area.x+area.width || g.y+g.height>area.y+area.height) return false;
        if (!win.restoreGeometry) { win.restoreGeometry={...(win._drag?.original.restoreGeometry || win._drag?.original.geometry || win.geometry)}; win.restorePlacementMode=win._drag?.original.restorePlacementMode || win._drag?.original.placementMode || win.placementMode || 'tiled'; }
        win.geometry={x:Math.round(g.x),y:Math.round(g.y),width:Math.round(g.width),height:Math.round(g.height)}; win.placementMode=placementMode; win.maximized=placementMode==='maximized'; delete win._drag;
        tile(win.workspace); revision++; publish(); observe(); return true;
      }
      if (input?.kind === 'viewport') { viewport(input.width,input.height); tileAll(); revision++; topologyRevision++; deliver('controller','receiveTopology',{viewProtocol:2,kind:'view-topology',revision:String(topologyRevision),views:[state.viewScope],locations:[{scope:state.viewScope,box:[0,0,state.output.width,state.output.height]}]}); if (presentation?.lease) deliver('controller','receiveReflow',{scope:state.viewScope,lease:presentation.lease}); publish(); observe(); return true; }
      if (input?.kind === 'window' && input.action === 'restore-geometry') {
        const win=state.windows.find(w=>w.id===input.windowId && w.incarnation===input.incarnation && w.focused && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned));
        if (input.epoch!==epoch || !win || !win.restoreGeometry || !['snapped','maximized'].includes(win.placementMode)) return false;
        win.geometry=win.restoreGeometry; delete win.restoreGeometry;
        win.placementMode=win.restorePlacementMode || 'floating'; delete win.restorePlacementMode; win.maximized=false;
        tile(win.workspace); revision++; publish(); observe(); return true;
      }
      if (input?.kind === 'window' && input.action === 'minimize' && !state.windows.some(w=>input.epoch===epoch && w.id===input.windowId && w.incarnation===input.incarnation && w.focused && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned))) return false;
      if (input?.kind === 'window' && ['close','minimize'].includes(input.action)) {
        const win=state.windows.find(w=>input.epoch===epoch && w.id===input.windowId && w.incarnation===input.incarnation && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned)); if (!win) return false;
        if (input.action==='close') { const workspace=win.workspace; state.windows=state.windows.filter(w=>w.id!==win.id); state.activationHistory=state.activationHistory.filter(id=>id!==win.incarnation); tile(workspace); }
        else { win.minimized=true; win.focused=false; tile(win.workspace); }
        if (!state.windows.some(w=>w.focused)) { const next=state.windows.find(w=>!w.minimized && (w.workspace===state.activeWorkspace || w.pinned)); if (next) next.focused=true; }
        revision++; publish(); observe(); return true;
      }
      if (input?.kind === 'pointer') {
        const win=state.windows.find(w=>input.epoch===epoch && w.id===input.windowId && w.incarnation===input.incarnation && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned));
        if (!win) return false;
        if (input.action==='start') {
          if (win._drag || !['move','resize'].includes(input.mode) || !Number.isFinite(input.x) || !Number.isFinite(input.y)) return false;
          const original={geometry:copy(win.geometry),placementMode:win.placementMode,maximized:win.maximized,restoreGeometry:copy(win.restoreGeometry),restorePlacementMode:win.restorePlacementMode};
          const restored=['maximized','snapped'].includes(win.placementMode) && win.restoreGeometry ? copy(win.restoreGeometry) : copy(win.geometry);
          win._drag={epoch,incarnation:win.incarnation,pointerId:input.pointerId,mode:input.mode,x:input.x,y:input.y,original,geometry:restored};
          win.geometry=copy(restored); win.placementMode='floating'; win.maximized=false; delete win.restoreGeometry; delete win.restorePlacementMode;
          publish(); return true;
        }
        const drag=win._drag;
        if (!drag || drag.epoch!==epoch || drag.incarnation!==input.incarnation || drag.pointerId!==input.pointerId || drag.mode!==input.mode || drag.x!==input.x || drag.y!==input.y) return false;
        if (input.action==='cancel') { Object.assign(win,drag.original); delete win._drag; revision++; publish(); observe(); return true; }
        if (!['move','end'].includes(input.action) || !Number.isFinite(input.currentX) || !Number.isFinite(input.currentY)) return false;
        const dx=Math.round(input.currentX-drag.x), dy=Math.round(input.currentY-drag.y), g=drag.geometry;
        if (drag.mode==='move') win.geometry={...g,x:g.x+dx,y:g.y+dy};
        else win.geometry={...g,width:Math.max(160,g.width+dx),height:Math.max(100,g.height+dy)};
        if (input.action==='end') { delete win._drag; tile(win.workspace); revision++; observe(); } publish(); return true;
      }
      if (input?.kind === 'window' && input.action === 'focus') {
        const selected = state.windows.find(w=>input.epoch===epoch && w.id===input.windowId && w.incarnation===input.incarnation && !w.minimized && (w.workspace===state.activeWorkspace || w.pinned));
        if (!selected) return false;
        state.windows.forEach(w=>{w.focused=w===selected;}); state.activationHistory=[selected.incarnation,...state.activationHistory.filter(id=>id!==selected.incarnation)]; revision++; publish(); observe(); return true;
      }
      if (input?.kind === 'system-motion-preference') {
        systemMotion = input.reduced || input.matches || input.profile === 'reduced' ? 'reduced' : 'full';
        if (state.binding) deliver('controller','receiveNative',{protocolVersion:3,kind:'host-motion-preference',serial:String(++motionSerial),profile:systemMotion,source:'portal'}); return true;
      }
      if ((input?.kind === 'application' && input.action === 'launch') || (input?.kind === 'files' && input.action === 'open')) {
        const app = input.kind === 'files' ? 'warlock-files' : input.intent?.entry;
        if (!app) return false;
        if (input.kind==='files') { const key=JSON.stringify([input.peer?.pid,input.peer?.start,input.peer?.instance]); const existing=state.windows.find(w=>w.filesPeer===key); if (existing) { state.windows.forEach(w=>w.focused=false); existing.focused=true; existing.minimized=false; existing.workspace=state.activeWorkspace; existing.location=input.target; tile(existing.workspace); state.activationHistory=[existing.incarnation,...state.activationHistory.filter(id=>id!==existing.incarnation)]; revision++; publish(); observe(); return true; } }
        const next = String(nextIncarnation++);
        const labels = {'warlock-editor':'Editor','warlock-browser':'Browser','warlock-terminal':'Terminal','warlock-files':'Files'};
        state.windows.forEach(w=>w.focused=false);
        const area=state.workArea, count=state.windows.filter(w=>w.workspace===state.activeWorkspace && !w.minimized).length;
        const win={id:next,incarnation:next,label:labels[app] || app,title:labels[app] || app,owner:null,application:app,workspace:state.activeWorkspace,minimized:false,focused:true,geometry:{x:16+24*(count%5),y:area.y+16+24*(count%5),width:Math.max(160,Math.floor(area.width*.65)-32),height:Math.max(100,Math.floor(area.height*.75)-32)}};
        win.placementMode='tiled'; if (input.kind==='files') { win.filesPeer=JSON.stringify([input.peer?.pid,input.peer?.start,input.peer?.instance]); win.location=input.target; }
        state.windows.push(win); tile(win.workspace); state.activationHistory=[next,...state.activationHistory]; revision++; publish(); observe(); return true;
      }
      if (input?.kind === 'switcher') {
        const action=input.action;
        if (!['next','previous','activate','cancel'].includes(action)) return false;
        if (!switchChord) {
          if (!['next','previous'].includes(action)) return false;
          const alreadyOpen=presentation?.mode==='switcher';
          const chord={epoch, queue:alreadyOpen ? [action] : action==='previous'?['previous']:[], terminal:false};
          switchChord=chord;
          (async () => {
            const opened=presentation?.mode==='switcher' || await this.invoke('switcher');
            if (!opened || switchChord!==chord || epoch!==chord.epoch) { if (switchChord===chord) switchChord=null; return; }
            let lastPublication=null;
            const deadline=Date.now()+5000;
            while (switchChord===chord && epoch===chord.epoch && Date.now()<deadline) {
              if (chord.queue.length && presentation?.mode==='switcher' && applied.has('popup') && presentation.publication!==lastPublication) {
                const next=chord.queue.shift();
                lastPublication=presentation.publication;
                const sent=activateControl('popup',({next:'control:forward',previous:'control:reverse',activate:'control:commit',cancel:'control:close'})[next]);
                if (!sent || next==='activate' || next==='cancel') { if (switchChord===chord) switchChord=null; return; }
              }
              await new Promise(resolve=>setTimeout(resolve,10));
            }
            if (switchChord===chord) switchChord=null;
          })();
          return true;
        }
        if (switchChord.terminal) return false;
        switchChord.queue.push(action);
        if (action==='activate' || action==='cancel') switchChord.terminal=true;
        return true;
      }
      if (input?.kind === 'taskbar-number') {
        const groups=presentation?.bar?.filter(row=>row.id.startsWith('bar:pin:') || row.id.startsWith('bar:group:')) || [];
        const group=groups[input.index-1]; if (!group) return false;
        if (input.action==='launch') return this.invoke('new-instance:' + group.id);
        if (input.action==='menu') return this.invoke('application-actions:' + group.id);
        return activateControl('bar',group.id);
      }
      const route = input?.kind === 'shortcut' ? {applications:'launcher',system:'system',notifications:'notifications'}[input.route] : input?.kind === 'utility' ? input.action : input?.kind === 'switcher' && input.action === 'next' ? 'switcher' : null;
      return route ? this.invoke(route) : false;
    },
    setFault(policy) { if (!FAULT_POLICIES.includes(policy)) throw new RangeError('Unknown fault policy'); fault = policy; diag('fault-policy',fault); },
    destroy() { if (destroyed) return; destroyed = true; abort.abort(); cancelTimers(); clearTimeout(noticeTimer); removeEventListener('message',receive); listeners.clear(); handlers.clear(); preview = null; },
    getTrace() { return freeze(copy(trace)); }
  };
}
