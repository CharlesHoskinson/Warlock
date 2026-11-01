// Prepared ELM-UI-007 component harness. Execute only under root's reviewed runner.
// node feedback-context-browser.mjs BASE_URL OUTPUT_DIR CHROME ROWS_PATH
// BASE_URL serves /qa/feedback-context-bar.html and -popup.html, each loading the
// actual compiled Elm root, shell.css, and exposing testApp and actions[].
// ROWS_PATH is the elm-tests JSON report containing source-derived rows.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const [base, out, binary, rowsPath] = process.argv.slice(2);
const report = { schema: 1, scope: 'compiled Elm Bar/Popup browser component only', nativeAcceptance: false, fullReleaseAccepted: false, passed: false, checks: [], errors: [], externalRequests: [] };
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
let browser, ws, session, seq = 0, stderr = '', stdout = '', profile;
const pending = new Map();
function check(name, condition, detail) {
  report.checks.push({ name, detail });
  if (!condition) throw Error(`${name}: ${JSON.stringify(detail)}`);
}
function call(method, params = {}, sessionId = session) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => { pending.delete(id); reject(Error(`CDP timeout: ${method}`)); }, 15000);
    pending.set(id, { resolve, reject, timer });
    ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
}
async function evaluate(expression) {
  const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function until(expression) {
  for (let i = 0; i < 100; i++) { if (await evaluate(expression)) return; await sleep(30); }
  throw Error(`Timed out waiting for ${expression}`);
}
try {
  if (process.argv.length !== 6 || !base || !out || !binary || !rowsPath) throw Error('Expected BASE_URL OUTPUT_DIR CHROME ROWS_PATH');
  const origin = new URL(base);
  if (origin.protocol !== 'http:' || origin.hostname !== '127.0.0.1' || origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) throw Error('BASE_URL must be a bare http://127.0.0.1:PORT origin');
  const fixture = JSON.parse(fs.readFileSync(rowsPath, 'utf8'));
  const rows = fixture.rows;
  const states = ['Pending', 'Unknown', 'Refused', 'None', 'Committed'];
  check('fixture report passed and contains rows', fixture.passed === true && Array.isArray(rows), { passed: fixture.passed, rows: typeof rows });
  const selected = rows.filter(r => r.open === true && r.context === 'matching' && !r.older && !r.detached);
  const ordered = states.map(state => selected.find(r => r.status === state));
  check('fixture has matching Applications rows for all states', ordered.every(Boolean), selected.map(r => ({ name: r.name, status: r.status })));
  for (const row of ordered) {
    check(`fixture contract ${row.status}`, row.frame?.mode === 'applications' && row.repeatFrame?.mode === 'applications' && typeof row.expectedQuery === 'string' && typeof row.expectedGuidance === 'string' && row.expectedGuidance.length > 0 && typeof row.frame.status === 'string' && (row.feedback === null || typeof row.feedback === 'string') && Array.isArray(row.forbidden), row.name);
  }
  check('query and lease stable across rows', ordered.every(r => r.expectedQuery === ordered[0].expectedQuery && r.frame.lease === ordered[0].frame.lease && r.repeatFrame.lease === r.frame.lease), { query: ordered[0].expectedQuery, lease: ordered[0].frame.lease });
  profile = fs.mkdtempSync(path.join(os.tmpdir(), 'warlock-feedback-context-'));
  const env = { ...process.env };
  for (const key of ['DISPLAY', 'WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'DBUS_SESSION_BUS_ADDRESS', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']) delete env[key];
  browser = spawn(binary, ['--headless=new', '--disable-gpu', '--disable-software-rasterizer', '--disable-breakpad', '--disable-crash-reporter', '--disable-background-networking', '--no-first-run', '--no-default-browser-check', '--no-proxy-server', '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'], { env, stdio: ['ignore', 'pipe', 'pipe'] });
  browser.stderr.on('data', b => { stderr += b; }); browser.stdout.on('data', b => { stdout += b; });
  let endpoint;
  for (let i = 0; i < 150; i++) { endpoint = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/)?.[1]; if (endpoint) break; if (browser.exitCode !== null) throw Error(`Chrome exited ${browser.exitCode}: ${stderr}`); await sleep(30); }
  if (!endpoint) throw Error('No DevTools endpoint');
  ws = new WebSocket(endpoint);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  ws.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id) { const p = pending.get(message.id); if (p) { pending.delete(message.id); clearTimeout(p.timer); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); } }
    else if (message.method === 'Runtime.exceptionThrown') report.errors.push(message.params.exceptionDetails);
    else if (message.method === 'Fetch.requestPaused') {
      const url = message.params.request.url;
      let allowed = false;
      try { allowed = new URL(url).origin === origin.origin; } catch (_) {}
      if (!allowed) report.externalRequests.push(url);
      call(allowed ? 'Fetch.continueRequest' : 'Fetch.failRequest', { requestId: message.params.requestId, ...(allowed ? {} : { errorReason: 'BlockedByClient' }) }, message.sessionId).catch(e => report.errors.push(String(e)));
    }
  };
  const target = await call('Target.createTarget', { url: 'about:blank' }, null);
  session = (await call('Target.attachToTarget', { targetId: target.targetId, flatten: true }, null)).sessionId;
  await call('Page.enable'); await call('Runtime.enable'); await call('Fetch.enable', { patterns: [{ urlPattern: '*' }] });
  let publication = 0;
  let baselineError = null;
  try {
  for (const width of [320, 1440]) {
    await call('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
    for (const surface of ['bar', 'popup']) {
      await call('Page.navigate', { url: `${origin.origin}/qa/feedback-context-${surface}.html` });
      await until('!!window.testApp && Array.isArray(window.actions)');
      for (const [index, row] of ordered.entries()) {
        for (const [repetition, sourceFrame] of [row.frame, row.repeatFrame].entries()) {
          const frame = structuredClone(sourceFrame); frame.publication = String(++publication);
          await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(frame)})`);
          await until(`document.querySelector('.surface-${surface}')?.dataset.publication === ${JSON.stringify(frame.publication)}`);
          if (index === 0 && repetition === 0 && surface === 'popup') {
            await evaluate(`window.heldField=document.querySelector('[data-surface-field="control:search"]'); if(window.heldField) window.heldField.focus()`);
            check(`${width} popup query focus established`, await evaluate('!!heldField && document.activeElement === heldField'));
          }
          if (index === 0 && repetition === 0 && surface === 'bar') {
            await evaluate(`window.heldControl=document.querySelector('.surface-bar [data-surface-control="bar:applications"]:not([disabled])'); if(window.heldControl) window.heldControl.focus()`);
            check(`${width} bar control focus established`, await evaluate('!!heldControl && document.activeElement === heldControl'));
          }
          const seen = await evaluate(`(()=>{const root=document.querySelector('.surface-${surface}'), n=root.querySelector('[role="status"]'), r=n.getBoundingClientRect(), style=getComputedStyle(n), field=document.querySelector('[data-surface-field="control:search"]'), toolbar=root.querySelector('.surface-actions[role="toolbar"]'), t=toolbar?.getBoundingClientRect(); return {text:n.textContent,ariaLabel:n.getAttribute('aria-label'),live:n.getAttribute('aria-live'),display:style.display,visibility:style.visibility,clipPath:style.clipPath,x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,viewportWidth:window.innerWidth,viewportHeight:window.innerHeight,toolbar:t?{x:t.x,y:t.y,right:t.right,bottom:t.bottom,width:t.width,height:t.height}:null,query:field?.value,queryName:field?.getAttribute('aria-label'),fieldHeld:!!window.heldField && document.activeElement===heldField && heldField.isConnected,controlHeld:!!window.heldControl && document.activeElement===heldControl && heldControl.isConnected,actions:window.actions.length};})()`);
          const positive = ['Pending', 'Unknown', 'Refused'].includes(row.status);
          const feedback = positive ? typeof row.feedback === 'string' && seen.text.includes(row.feedback) : row.feedback === null && row.forbidden.every(text => !seen.text.includes(text)) && seen.text === row.expectedGuidance;
          check(`${width} ${surface} ${row.status} ${repetition} status and guidance`, seen.text === frame.status && seen.text.includes(row.expectedGuidance) && feedback, seen);
          const inViewport = seen.x >= 0 && seen.y >= 0 && seen.right <= seen.viewportWidth && seen.bottom <= seen.viewportHeight;
          const toolbar = seen.toolbar;
          const noToolbarOverlap = toolbar && (seen.right <= toolbar.x || seen.x >= toolbar.right || seen.bottom <= toolbar.y || seen.y >= toolbar.bottom);
          check(`${width} ${surface} ${row.status} ${repetition} visible semantic status`, seen.display !== 'none' && seen.visibility === 'visible' && seen.clipPath === 'none' && seen.width > 0 && seen.height > 0 && inViewport && seen.live === 'off' && (surface !== 'bar' || (seen.ariaLabel === seen.text && noToolbarOverlap)), seen);
          if (positive) {
            const expectedPrefix = { Pending: 'Restore: applying', Unknown: 'Restore: not confirmed', Refused: 'Restore: refused' }[row.status];
            const prefix = await evaluate(`(()=>{const n=document.querySelector('.surface-${surface} [role="status"]'), expected=${JSON.stringify(expectedPrefix)}, walker=document.createTreeWalker(n,NodeFilter.SHOW_TEXT), nodes=[]; let node; while((node=walker.nextNode())) nodes.push(node); const text=nodes.map(part=>part.data).join(''), rects=[]; if(text.startsWith(expected) && nodes.length){let remaining=expected.length, end=null; for(const part of nodes){if(remaining<=part.length){end={part,offset:remaining}; break;} remaining-=part.length;} if(end){const range=document.createRange(); range.setStart(nodes[0],0); range.setEnd(end.part,end.offset); for(const r of range.getClientRects()) rects.push({x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height});}} const box=n.getBoundingClientRect(); return {expectedPrefix:expected,startsWith:text.startsWith(expected),rects,box:{x:box.x,y:box.y,right:box.right,bottom:box.bottom},viewport:{width:innerWidth,height:innerHeight}};})()`);
            const contained = prefix.rects.length > 0 && prefix.rects.every(r => r.width > 0 && r.height > 0 && r.x >= prefix.box.x && r.y >= prefix.box.y && r.right <= prefix.box.right && r.bottom <= prefix.box.bottom && r.x >= 0 && r.y >= 0 && r.right <= prefix.viewport.width && r.bottom <= prefix.viewport.height);
            check(`${width} ${surface} ${row.status} ${repetition} leading prefix visible`, prefix.startsWith && contained, prefix);
          }
          check(`${width} ${surface} ${row.status} ${repetition} no actions and retained focus`, seen.actions === 0 && (surface === 'popup' ? seen.query === row.expectedQuery && seen.queryName === 'Search applications' && seen.fieldHeld : seen.controlHeld), seen);
          const ax = (await call('Accessibility.getFullAXTree')).nodes.filter(n => !n.ignored).map(n => ({ role: n.role?.value, name: n.name?.value }));
          check(`${width} ${surface} ${row.status} ${repetition} accessibility names`, surface === 'bar' ? ax.some(n => n.role === 'status' && n.name === seen.text) : ax.some(n => n.role === 'searchbox' && n.name === 'Search applications') && ax.some(n => n.role === 'StaticText' && n.name === seen.text), ax.filter(n => ['status', 'searchbox', 'StaticText'].includes(n.role)));
          if (row.status === 'Unknown' && repetition === 0) {
            const screenshot = await call('Page.captureScreenshot', { format: 'png' });
            const filename = `feedback-context-${surface}-unknown-${width}.png`;
            fs.writeFileSync(path.join(out, filename), Buffer.from(screenshot.data, 'base64'));
            report.checks.push({ name: `${width} ${surface} Unknown screenshot captured`, detail: filename });
          }
        }
      }
    }
  }
  } catch (err) {
    baselineError = err;
    report.baselineError = String(err.stack || err);
  }
  // Controlled renderer precondition checks at 621px width across 100% and 200%
  // textScale. Projecting frame.appearance here verifies SurfaceRenderer/SurfaceTheme
  // scaling, status scrollport reachability, and control hit geometry only; it is
  // neither Settings persistence nor native/release acceptance.
  report.controlledRenderer621 = {
    preconditionOnly: true,
    settingsPersistenceAccepted: false,
    nativeAcceptance: false,
    fullReleaseAccepted: false,
    barScales: {},
    popupScales: {},
    statusChangeScrollReset: null,
    counterexampleError: null,
    observations: []
  };
  let controlledError = null;
  try {
    await call('Emulation.setFocusEmulationEnabled', { enabled: true });
    const pressKey = async (key, code, vk) => {
      await call('Input.dispatchKeyEvent', { type: 'keyDown', key, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk });
      await call('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk });
      await sleep(45);
    };
    const clickPoint = async (x, y) => {
      await call('Input.dispatchMouseEvent', { type: 'mousePressed', button: 'left', clickCount: 1, x, y });
      await call('Input.dispatchMouseEvent', { type: 'mouseReleased', button: 'left', clickCount: 1, x, y });
      await sleep(45);
    };
    const measureRangeInStatus = (surfaceName, expectedSubstring) => evaluate(`(()=>{const n=document.querySelector('.surface-${surfaceName} [role="status"]'), expected=${JSON.stringify(expectedSubstring)}, walker=document.createTreeWalker(n,NodeFilter.SHOW_TEXT), nodes=[]; let node; while((node=walker.nextNode())) nodes.push(node); const text=nodes.map(part=>part.data).join(''), startIndex=text.indexOf(expected), rects=[]; if(startIndex>=0 && nodes.length){let startOffset=startIndex, endOffset=startIndex+expected.length, pos=0, startRef=null, endRef=null; for(const part of nodes){const nextPos=pos+part.length; if(!startRef && startOffset<=nextPos) startRef={part,offset:startOffset-pos}; if(!endRef && endOffset<=nextPos){endRef={part,offset:endOffset-pos}; break;} pos=nextPos;} if(startRef && endRef){const range=document.createRange(); range.setStart(startRef.part,startRef.offset); range.setEnd(endRef.part,endRef.offset); for(const r of range.getClientRects()) rects.push({x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height});}} const outer=n.getBoundingClientRect(), inner=n.closest(".surface-bar")?n.querySelector(':scope > span[tabindex="0"]'):null, scroll=inner?.getBoundingClientRect(); const box=scroll?{x:Math.max(0,outer.left,scroll.left+inner.clientLeft),y:Math.max(0,outer.top,scroll.top+inner.clientTop),right:Math.min(innerWidth,outer.right,scroll.left+inner.clientLeft+inner.clientWidth),bottom:Math.min(innerHeight,outer.bottom,scroll.top+inner.clientTop+inner.clientHeight)}:outer; const contained=rects.length>0 && rects.every(r=>r.width>0 && r.height>0 && r.x>=box.x-0.75 && r.y>=box.y-0.75 && r.right<=box.right+0.75 && r.bottom<=box.bottom+0.75 && r.x>=-0.75 && r.y>=-0.75 && r.right<=innerWidth+0.75 && r.bottom<=innerHeight+0.75); return {expected,found:startIndex>=0,contained,rects,outerBox:{x:outer.x,y:outer.y,right:outer.right,bottom:outer.bottom},box:{x:box.x,y:box.y,right:box.right,bottom:box.bottom},viewport:{width:innerWidth,height:innerHeight}};})()`);
    const positiveRows = ['Pending', 'Unknown', 'Refused'].map(status => ordered.find(r => r.status === status));
    const pendingRow = ordered.find(r => r.status === 'Pending');
    const unknownRow = ordered.find(r => r.status === 'Unknown');
    const refusedRow = ordered.find(r => r.status === 'Refused');

    await call('Emulation.setDeviceMetricsOverride', { width: 621, height: 240, deviceScaleFactor: 1, mobile: false });
    await call('Page.navigate', { url: `${origin.origin}/qa/feedback-context-bar.html` });
    await until('!!window.testApp && Array.isArray(window.actions)');
    for (const scale of [100, 200]) {
      for (const row of positiveRows) {
        const frame = structuredClone(row.frame);
        frame.publication = String(++publication);
        frame.appearance = { ...(frame.appearance || {}), textScale: scale };
        let activePublication = frame.publication;
        await evaluate(`window.actions.length = 0; window.testApp.ports.presentation.send(${JSON.stringify(frame)})`);
        await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(frame.publication)} && document.querySelector('.surface-bar')?.dataset.textScale === ${JSON.stringify(String(scale))}`);
        const metrics = await evaluate(`(()=>{const bar=document.querySelector('.surface-bar'), status=bar.querySelector('[role="status"]'), inner=status?.firstElementChild, toolbar=bar.querySelector('.surface-actions[role="toolbar"]'), br=bar.getBoundingClientRect(), sr=status.getBoundingClientRect(), tr=toolbar.getBoundingClientRect(), bs=getComputedStyle(bar), ss=getComputedStyle(status), is=inner?getComputedStyle(inner):null; return {scale:${scale},statusState:${JSON.stringify(row.status)},barFont:parseFloat(bs.fontSize),statusFont:parseFloat(ss.fontSize),innerFont:is?parseFloat(is.fontSize):null,barHeight:br.height,statusBox:{x:sr.x,y:sr.y,right:sr.right,bottom:sr.bottom,width:sr.width,height:sr.height},toolbarBox:{x:tr.x,y:tr.y,right:tr.right,bottom:tr.bottom,width:tr.width,height:tr.height},tabIndex:inner?.getAttribute('tabindex')??null,overflowY:is?.overflowY??null,clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,scrollTop:inner?.scrollTop??-1,actions:window.actions.length};})()`);
        report.controlledRenderer621.observations.push(metrics);
        if (row.status === 'Unknown') report.controlledRenderer621.barScales[scale] = metrics;
        const expectedBarFont = (16 * scale) / 100;
        const expectedStatusFont = (12 * scale) / 100;
        const expectedBarHeight = 3 * expectedBarFont + 8;
        check(`621 bar ${scale}% ${row.status} controlled precondition scale and scrollport`, metrics.barFont === expectedBarFont && metrics.statusFont === expectedStatusFont && metrics.innerFont === expectedStatusFont && Math.abs(metrics.barHeight - expectedBarHeight) <= 1 && metrics.tabIndex === '0' && metrics.overflowY === 'auto' && metrics.clientHeight > 0 && metrics.scrollHeight >= metrics.clientHeight && metrics.scrollTop === 0 && metrics.statusBox.x >= metrics.toolbarBox.right - 0.5 && metrics.statusBox.right <= 621.5 && metrics.actions === 0, metrics);

        const expectedPrefix = { Pending: 'Restore: applying', Unknown: 'Restore: not confirmed', Refused: 'Restore: refused' }[row.status];
        const initialPrefix = await measureRangeInStatus('bar', expectedPrefix);
        check(`621 bar ${scale}% ${row.status} initial leading prefix visible`, initialPrefix.found && initialPrefix.contained, initialPrefix);

        await pressKey('Tab', 'Tab', 9);
        await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); if(inner) inner.focus();})()`);
        const focusState = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'), s=inner?getComputedStyle(inner):null; return {focused:!!inner && document.activeElement===inner,focusVisible:!!inner && inner.matches(':focus-visible'),outlineStyle:s?.outlineStyle??'none',outlineWidth:s?parseFloat(s.outlineWidth):0,inlineOutlineWidth:inner?.style?.outlineWidth??'',clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,scrollTop:inner?.scrollTop??0,actions:window.actions.length};})()`);
        check(`621 bar ${scale}% ${row.status} status scrollport keyboard focusable`, focusState.focused && focusState.focusVisible && focusState.outlineStyle !== 'none' && focusState.inlineOutlineWidth === '2px' && focusState.actions === 0, focusState);

        if (scale === 200 && (row.status === 'Unknown' || row.status === 'Refused')) {
          check(`621 bar 200% ${row.status} overflows vertically without font shrinking`, focusState.scrollHeight > focusState.clientHeight + 4, focusState);
        }
        if (focusState.scrollHeight > focusState.clientHeight + 1) {
          for (let step = 0; step < 12; step++) {
            const done = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return !!inner && inner.scrollTop >= inner.scrollHeight - inner.clientHeight - 2;})()`);
            if (done) break;
            await pressKey('PageDown', 'PageDown', 34);
            await pressKey('ArrowDown', 'ArrowDown', 40);
          }
        }
        const afterScroll = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return {clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,scrollTop:inner?.scrollTop??0,actions:window.actions.length};})()`);
        const recoverySnippet = { Pending: row.expectedGuidance, Unknown: 'Refresh only reads status.', Refused: 'Refresh window status, then choose again.' }[row.status];
        // Recovery and guidance may occupy more than one scrollport together.
        // Prove each complete phrase is reachable by real keyboard scrolling,
        // rather than requiring both at the same final bottom offset.
        const revealPhrase = async phrase => {
          let measured = await measureRangeInStatus('bar', phrase);
          const reached = measured.rects.map(() => false);
          const observations = [];
          for (let step = 0; measured.found && step <= 24; step++) {
            measured.rects.forEach((r, index) => {
              if (r.width > 0 && r.height > 0 && r.x >= measured.box.x - 0.75 && r.y >= measured.box.y - 0.75 && r.right <= measured.box.right + 0.75 && r.bottom <= measured.box.bottom + 0.75 && r.x >= -0.75 && r.y >= -0.75 && r.right <= measured.viewport.width + 0.75 && r.bottom <= measured.viewport.height + 0.75) reached[index] = true;
            });
            observations.push(measured);
            if (reached.length > 0 && reached.every(Boolean)) break;
            const above = measured.rects.some((r, index) => !reached[index] && r.y < measured.box.y - 0.75);
            await pressKey(above ? 'ArrowUp' : 'ArrowDown', above ? 'ArrowUp' : 'ArrowDown', above ? 38 : 40);
            measured = await measureRangeInStatus('bar', phrase);
          }
          return { found: measured.found, fullyReachable: reached.length > 0 && reached.every(Boolean), reached, observations };
        };
        const recoveryVisible = await revealPhrase(recoverySnippet);
        const guidanceVisible = await revealPhrase(row.expectedGuidance);
        check(`621 bar ${scale}% ${row.status} full recovery and guidance reachable via keyboard scroll`, (afterScroll.scrollHeight <= afterScroll.clientHeight + 1 || (afterScroll.scrollTop > 0 && afterScroll.scrollTop >= afterScroll.scrollHeight - afterScroll.clientHeight - 2)) && recoveryVisible.found && recoveryVisible.fullyReachable && guidanceVisible.found && guidanceVisible.fullyReachable && afterScroll.actions === 0, { afterScroll, recoveryVisible, guidanceVisible });
        // Retention below compares a user-chosen bottom offset across repeats.
        await pressKey('End', 'End', 35);

        if (scale === 200 && row.status === 'Unknown') {
          const screenshot = await call('Page.captureScreenshot', { format: 'png' });
          const filename = 'feedback-context-bar-unknown-621-200.png';
          fs.writeFileSync(path.join(out, filename), Buffer.from(screenshot.data, 'base64'));
          report.checks.push({ name: '621 bar 200% Unknown scrolled precondition screenshot captured', detail: filename });

          await until(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return inner && Math.abs(inner.scrollTop-(inner.scrollHeight-inner.clientHeight))<=1;})()`);
          const beforeRepeat = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); window.beforeRepeatStatusInner=inner; return {focused:document.activeElement===inner,scrollTop:inner.scrollTop,clientHeight:inner.clientHeight,scrollHeight:inner.scrollHeight};})()`);
          const repeat = structuredClone(row.repeatFrame);
          repeat.publication = String(++publication);
          repeat.appearance = { ...(repeat.appearance || {}), textScale: 200 };
          activePublication = repeat.publication;
          await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(repeat)})`);
          await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(repeat.publication)}`);
          const retained = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return {sameNode:inner===window.beforeRepeatStatusInner,focused:document.activeElement===inner,scrollTop:inner?.scrollTop??-1};})()`);
          check('621 bar 200% identical repeat status retains user scrollport offset', beforeRepeat.focused && retained.sameNode && retained.focused && Math.abs(retained.scrollTop - beforeRepeat.scrollTop) <= 1, { beforeRepeat, retained });
        }

        if (row.status === 'Unknown') {
          for (const controlId of ['bar:recovery-refresh', 'bar:applications', 'bar:settings']) {
            await pressKey('Tab', 'Tab', 9);
            const target = await evaluate(`(()=>{const toolbar=document.querySelector('.surface-bar .surface-actions[role="toolbar"]'), el=toolbar?.querySelector('[data-surface-control=${JSON.stringify(controlId)}]:not([disabled])'); if(!el) return null; el.scrollIntoView({block:'nearest',inline:'nearest'}); el.focus(); const r=el.getBoundingClientRect(), tr=toolbar.getBoundingClientRect(), s=getComputedStyle(el), cx=r.left+r.width/2, cy=r.top+r.height/2, hit=document.elementFromPoint(cx,cy), labels=[...el.querySelectorAll('.control-label,.control-detail')].filter(n=>n.textContent.length>0).map(n=>{const lr=n.getBoundingClientRect(); return {text:n.textContent,top:lr.top,bottom:lr.bottom,left:lr.left,right:lr.right};}); return {controlId:${JSON.stringify(controlId)},focused:document.activeElement===el,cx,cy,pointerUnobscured:!!hit && el.contains(hit),inlineOutlineWidth:el.style.outlineWidth,outlineColor:s.outlineColor,rect:{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height},toolbar:{left:tr.left,top:tr.top,right:tr.right,bottom:tr.bottom},labelsInside:labels.every(l=>l.top>=r.top-0.75 && l.bottom<=r.bottom+0.75 && l.left>=r.left-0.75 && l.right<=r.right+0.75),labels};})()`);
            check(`621 bar ${scale}% ${controlId} keyboard and pointer reachable without clipping`, !!target && target.focused && target.pointerUnobscured && target.inlineOutlineWidth === '3px' && target.outlineColor === 'rgb(142, 200, 255)' && target.rect.width >= 24 && target.rect.height >= 24 && target.rect.left >= target.toolbar.left - 0.75 && target.rect.right <= target.toolbar.right + 0.75 && target.rect.top >= -0.75 && target.rect.bottom <= target.toolbar.bottom + 0.75 && target.labelsInside, target);
            if (controlId === 'bar:recovery-refresh') {
              await clickPoint(target.cx, target.cy);
              const dispatched = await evaluate(`(()=>{const copy=[...window.actions]; window.actions.length=0; return copy;})()`);
              check(`621 bar ${scale}% bar:recovery-refresh pointer click dispatches scoped action`, dispatched.length === 1 && dispatched[0]?.kind === 'surface-action' && dispatched[0]?.id === 'bar:recovery-refresh' && dispatched[0]?.publication === activePublication, dispatched);
            }
          }
        }
      }
    }
    check('621 bar controlled precondition exact 2x font scaling (100% -> 200%)', report.controlledRenderer621.barScales[100]?.barFont === 16 && report.controlledRenderer621.barScales[200]?.barFont === 32 && report.controlledRenderer621.barScales[200]?.statusFont === report.controlledRenderer621.barScales[100]?.statusFont * 2 && report.controlledRenderer621.barScales[200]?.innerFont === report.controlledRenderer621.barScales[100]?.innerFont * 2, report.controlledRenderer621.barScales);

    await call('Emulation.setDeviceMetricsOverride', { width: 621, height: 620, deviceScaleFactor: 1, mobile: false });
    await call('Page.navigate', { url: `${origin.origin}/qa/feedback-context-popup.html` });
    await until('!!window.testApp && Array.isArray(window.actions)');
    for (const scale of [100, 200]) {
      const frame = structuredClone(unknownRow.frame);
      frame.publication = String(++publication);
      frame.appearance = { ...(frame.appearance || {}), textScale: scale };
      await evaluate(`window.actions.length = 0; window.testApp.ports.presentation.send(${JSON.stringify(frame)})`);
      await until(`document.querySelector('.surface-popup')?.dataset.publication === ${JSON.stringify(frame.publication)} && document.querySelector('.surface-popup')?.dataset.textScale === ${JSON.stringify(String(scale))}`);
      if (scale === 100) {
        await evaluate(`window.heldField621=document.querySelector('[data-surface-field="control:search"]'); if(window.heldField621) window.heldField621.focus()`);
      }
      const popupMetrics = await evaluate(`(()=>{const popup=document.querySelector('.surface-popup'), field=popup.querySelector('[data-surface-field="control:search"]'), ps=getComputedStyle(popup), fs=getComputedStyle(field), fr=field.getBoundingClientRect(); return {scale:${scale},popupFont:parseFloat(ps.fontSize),fieldFont:parseFloat(fs.fontSize),fieldHeight:fr.height,fieldLeft:fr.left,fieldRight:fr.right,query:field.value,fieldHeld:!!window.heldField621 && document.activeElement===window.heldField621 && window.heldField621.isConnected,scrollWidth:popup.scrollWidth,clientWidth:popup.clientWidth,actions:window.actions.length};})()`);
      report.controlledRenderer621.popupScales[scale] = popupMetrics;
      const expectedFont = (16 * scale) / 100;
      const popupPrefix = await measureRangeInStatus('popup', 'Restore: not confirmed');
      const popupGuidance = await measureRangeInStatus('popup', unknownRow.expectedGuidance);
      check(`621 popup ${scale}% Unknown controlled scale, query retention, and unclipped status`, popupMetrics.popupFont === expectedFont && popupMetrics.fieldFont === expectedFont && popupMetrics.fieldHeight >= 2.5 * expectedFont && popupMetrics.fieldLeft >= 0 && popupMetrics.fieldRight <= 621.5 && popupMetrics.scrollWidth <= popupMetrics.clientWidth + 1 && popupMetrics.query === unknownRow.expectedQuery && popupMetrics.fieldHeld && popupPrefix.contained && popupGuidance.contained && popupMetrics.actions === 0, { popupMetrics, popupPrefix, popupGuidance });

      // This fixture has no qualified native launch capability. Inspect its
      // reachable read-only application-actions control; launch stays disabled.
      const launchState = await evaluate(`(()=>{const entries=[...document.querySelectorAll('[data-surface-control^="entry:"]')]; return {count:entries.length,allDisabled:entries.every(el=>el.disabled)};})()`);
      check(`621 popup ${scale}% unqualified launch remains disabled`, launchState.count > 0 && launchState.allDisabled, launchState);
      for (const selector of ['[data-surface-control="control:close"]', '[data-surface-control="control:refresh"]', '[data-surface-control^="jump:open:"]:not([disabled])']) {
        await pressKey('Tab', 'Tab', 9);
        const item = await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)}); if(!el) return null; el.scrollIntoView({block:'nearest',inline:'nearest'}); el.focus(); const r=el.getBoundingClientRect(), s=getComputedStyle(el), cx=r.left+r.width/2, cy=r.top+r.height/2, hit=document.elementFromPoint(cx,cy); return {id:el.dataset.surfaceControl,focused:document.activeElement===el,focusVisible:el.matches(':focus-visible'),pointerUnobscured:!!hit && el.contains(hit),outlineStyle:s.outlineStyle,outlineWidth:parseFloat(s.outlineWidth),rect:{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};})()`);
        check(`621 popup ${scale}% ${selector} keyboard and pointer reachable without clipping`, !!item && item.focused && item.focusVisible && item.pointerUnobscured && item.outlineStyle !== 'none' && item.outlineWidth >= 2 && item.rect.width >= 44 && item.rect.height >= 40 && item.rect.left >= 0 && item.rect.right <= 621.5 && item.rect.top >= -0.75 && item.rect.bottom <= 620.75, item);
      }
      await evaluate(`if (window.heldField621) { window.heldField621.scrollIntoView({ block: 'nearest' }); window.heldField621.focus(); }`);
      if (scale === 200) {
        const screenshot = await call('Page.captureScreenshot', { format: 'png' });
        const filename = 'feedback-context-popup-unknown-621-200.png';
        fs.writeFileSync(path.join(out, filename), Buffer.from(screenshot.data, 'base64'));
        report.checks.push({ name: '621 popup 200% Unknown precondition screenshot captured', detail: filename });

        for (const nextRow of [refusedRow, pendingRow]) {
          const nextPopupFrame = structuredClone(nextRow.frame);
          nextPopupFrame.publication = String(++publication);
          nextPopupFrame.appearance = { ...(nextPopupFrame.appearance || {}), textScale: 200 };
          await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(nextPopupFrame)})`);
          await until(`document.querySelector('.surface-popup')?.dataset.publication === ${JSON.stringify(nextPopupFrame.publication)}`);
          const kept = await evaluate(`(()=>{const field=document.querySelector('[data-surface-field="control:search"]'); return {sameNode:field===window.heldField621,focused:document.activeElement===window.heldField621 && window.heldField621.isConnected,query:field?.value,actions:window.actions.length};})()`);
          check(`621 popup 200% status change to ${nextRow.status} preserves keyed search input focus and draft`, kept.sameNode && kept.focused && kept.query === unknownRow.expectedQuery && kept.actions === 0, kept);
        }
      }
    }
    check('621 popup controlled precondition exact 2x font scaling (100% -> 200%)', report.controlledRenderer621.popupScales[100]?.popupFont === 16 && report.controlledRenderer621.popupScales[200]?.popupFont === 32 && report.controlledRenderer621.popupScales[200]?.fieldFont === report.controlledRenderer621.popupScales[100]?.fieldFont * 2, report.controlledRenderer621.popupScales);

    // Status-change scroll-reset and focus reproducer at 621px width, 200% textScale.
    // Tests both (A) existing taskbar control focused and (B) status scrollport itself
    // focused when status text transitions across overflowing messages (Unknown -> Refused -> Pending).
    await call('Emulation.setDeviceMetricsOverride', { width: 621, height: 240, deviceScaleFactor: 1, mobile: false });
    await call('Page.navigate', { url: `${origin.origin}/qa/feedback-context-bar.html` });
    await until('!!window.testApp && Array.isArray(window.actions)');
    const scrollBarStatusToBottom = async sourceRow => {
      const f = structuredClone(sourceRow.frame);
      f.publication = String(++publication);
      f.appearance = { ...(f.appearance || {}), textScale: 200 };
      await evaluate(`window.actions.length = 0; window.testApp.ports.presentation.send(${JSON.stringify(f)})`);
      await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(f.publication)}`);
      await pressKey('Tab', 'Tab', 9);
      await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); if(inner) inner.focus();})()`);
      for (let step = 0; step < 12; step++) {
        const done = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return !!inner && inner.scrollTop >= inner.scrollHeight - inner.clientHeight - 2;})()`);
        if (done) break;
        await pressKey('PageDown', 'PageDown', 34);
        await pressKey('ArrowDown', 'ArrowDown', 40);
      }
      return evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return {scrollTop:inner?.scrollTop??0,clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0};})()`);
    };

    const scrolledA = await scrollBarStatusToBottom(unknownRow);
    await evaluate(`window.heldBarControl621=document.querySelector('.surface-bar [data-surface-control="bar:applications"]:not([disabled])'); if(window.heldBarControl621) window.heldBarControl621.focus()`);
    const nextRefusedA = structuredClone(refusedRow.frame);
    nextRefusedA.publication = String(++publication);
    nextRefusedA.appearance = { ...(nextRefusedA.appearance || {}), textScale: 200 };
    await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(nextRefusedA)})`);
    await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(nextRefusedA.publication)}`);
    const controlCase = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return {controlFocusPreserved:!!window.heldBarControl621 && document.activeElement===window.heldBarControl621 && window.heldBarControl621.isConnected,scrollTop:inner?.scrollTop??-1,clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,actions:window.actions.length};})()`);
    controlCase.refusedPrefix = await measureRangeInStatus('bar', 'Restore: refused');
    check('621 bar 200% status change preserves focused taskbar control', scrolledA.scrollTop > 0 && controlCase.controlFocusPreserved && controlCase.actions === 0, { scrolledA, controlCase });

    const scrolledB = await scrollBarStatusToBottom(unknownRow);
    await evaluate(`window.prevStatusInner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]')`);
    const nextRefusedB = structuredClone(refusedRow.frame);
    nextRefusedB.publication = String(++publication);
    nextRefusedB.appearance = { ...(nextRefusedB.appearance || {}), textScale: 200 };
    await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(nextRefusedB)})`);
    await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(nextRefusedB.publication)}`);
    const statusFocusedCase = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'), active=document.activeElement; return {sameInnerNode:!!inner && inner===window.prevStatusInner,prevInnerConnected:!!window.prevStatusInner?.isConnected,activeTag:active?.tagName??null,statusStillFocused:!!inner && active===inner,focusDroppedToBodyOnKeyedReplace:!window.prevStatusInner?.isConnected && (active===document.body || active===document.documentElement),newInnerTabIndex:inner?.getAttribute('tabindex')??null,scrollTop:inner?.scrollTop??-1,clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,actions:window.actions.length};})()`);
    statusFocusedCase.refusedPrefix = await measureRangeInStatus('bar', 'Restore: refused');
    await pressKey('Tab', 'Tab', 9);
    statusFocusedCase.reFocusable = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); if(inner) inner.focus(); return !!inner && document.activeElement===inner && inner.matches(':focus-visible');})()`);
    check('621 bar 200% status update retains focused scrollport DOM node', scrolledB.scrollTop > 0 && statusFocusedCase.actions === 0 && statusFocusedCase.newInnerTabIndex === '0' && statusFocusedCase.reFocusable && statusFocusedCase.sameInnerNode && statusFocusedCase.statusStillFocused, { scrolledB, statusFocusedCase });

    for (let step = 0; step < 12; step++) {
      const done = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return !!inner && inner.scrollTop >= inner.scrollHeight - inner.clientHeight - 2;})()`);
      if (done) break;
      await pressKey('PageDown', 'PageDown', 34);
      await pressKey('ArrowDown', 'ArrowDown', 40);
    }
    const nextPending = structuredClone(pendingRow.frame);
    nextPending.publication = String(++publication);
    nextPending.appearance = { ...(nextPending.appearance || {}), textScale: 200 };
    await evaluate(`window.testApp.ports.presentation.send(${JSON.stringify(nextPending)})`);
    await until(`document.querySelector('.surface-bar')?.dataset.publication === ${JSON.stringify(nextPending.publication)}`);
    const pendingCase = await evaluate(`(()=>{const inner=document.querySelector('.surface-bar [role="status"] > span[tabindex="0"]'); return {scrollTop:inner?.scrollTop??-1,clientHeight:inner?.clientHeight??0,scrollHeight:inner?.scrollHeight??0,actions:window.actions.length};})()`);
    pendingCase.pendingPrefix = await measureRangeInStatus('bar', 'Restore: applying');

    report.controlledRenderer621.statusChangeScrollReset = { scrolledA, controlCase, scrolledB, statusFocusedCase, pendingCase };
    check('621 bar 200% status change resets scrollport and reveals new leading prefix', controlCase.scrollTop === 0 && controlCase.refusedPrefix.found && controlCase.refusedPrefix.contained && statusFocusedCase.scrollTop === 0 && statusFocusedCase.refusedPrefix.found && statusFocusedCase.refusedPrefix.contained && pendingCase.scrollTop === 0 && pendingCase.pendingPrefix.found && pendingCase.pendingPrefix.contained && pendingCase.actions === 0, report.controlledRenderer621.statusChangeScrollReset);
  } catch (err) {
    controlledError = err;
    report.controlledRenderer621.counterexampleError = String(err.stack || err);
  } finally {
    try { await call('Emulation.setFocusEmulationEnabled', { enabled: false }); } catch (_) {}
  }
  check('no browser exceptions or external requests', report.errors.length === 0 && report.externalRequests.length === 0, { errors: report.errors, externalRequests: report.externalRequests });
  if (baselineError) throw baselineError;
  if (controlledError) throw controlledError;
  report.passed = true;
} catch (error) { report.error = String(error.stack || error); }
finally {
  if (ws?.readyState === 1) { try { await call('Browser.close', {}, null); } catch (_) {} ws.close(); }
  if (browser) {
    for (let i = 0; i < 100 && browser.exitCode === null && browser.signalCode === null; i++) await sleep(20);
    if (browser.exitCode === null && browser.signalCode === null) browser.kill('SIGTERM');
    await Promise.race([new Promise(resolve => { if (browser.exitCode !== null || browser.signalCode !== null) resolve(); else browser.once('exit', resolve); }), sleep(3000)]);
    report.browserExitCode = browser.exitCode; report.browserSignal = browser.signalCode;
    if (browser.exitCode !== 0) report.passed = false;
  }
  if (profile && (!browser || browser.exitCode !== null || browser.signalCode !== null)) fs.rmSync(profile, { recursive: true, force: true });
  else if (profile) { report.passed = false; report.cleanupError = `Browser still alive; profile retained at ${profile}`; }
  if (out) { fs.writeFileSync(path.join(out, 'feedback-context-browser.stderr'), stderr); fs.writeFileSync(path.join(out, 'feedback-context-browser.stdout'), stdout); fs.writeFileSync(path.join(out, 'feedback-context-browser-report.json'), JSON.stringify(report, null, 2) + '\n'); }
  console.log(JSON.stringify({ passed: report.passed, checks: report.checks.length, error: report.error }));
  process.exitCode = report.passed ? 0 : 1;
}
