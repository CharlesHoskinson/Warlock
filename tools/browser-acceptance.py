#!/usr/bin/env python3
"""Executable browser gate. Requires Playwright; static checks remain stdlib-only."""
import argparse, asyncio, json, sys, threading, tempfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.async_api import async_playwright

SCENARIOS='taskbar launcher switcher task-view transfer picker preview-states snap notifications settings files system window-menu confirmation application-actions status-recovery'.split()
# Each probe drives the relevant Elm control, then demands an admitted change.
# A missing, disabled, or unresponsive control is a failure, never a partial pass.
ACTIONS={
 'taskbar':('bar','bar:system'), 'launcher':('field','control:search'),
 'switcher':('popup','control:forward'), 'task-view':('popup','overview:workspace:2'),
 'transfer':('popup','overview:destination:2'), 'picker':('popup','family:4'),
 'preview-states':('popup','family:4'), 'snap':('popup','snap:region:left-half'),
 'notifications':('prefix','notification:'), 'settings':('popup','settings:theme:dawn'),
 'files':('popup','files:home'), 'system':('popup','system:volume-set:25'),
 'window-menu':('popup','menu:1:1'), 'confirmation':('popup','system:cancel'),
 'application-actions':('popup','control:new-instance:warlock-editor'), 'status-recovery':('popup','control:refresh')}
# These are renderer identities, not visible labels or button positions.
MODES={'launcher':'applications','switcher':'switcher','task-view':'overview','picker':'picker','preview-states':'picker','snap':'snap','notifications':'notifications','settings':'settings','files':'files','system':'system','window-menu':'menu','confirmation':'system','application-actions':'jump'}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass

def evaluate_result(scenario, status, mode, world_changed, announcements_ok=True):
 if status: return 'scenario failed or timed out: '+status
 if scenario in MODES and mode != MODES[scenario]: return f'wrong popup mode: expected {MODES[scenario]}, got {mode}'
 if not world_changed: return 'expected behavioral state change was not observed'
 if not announcements_ok:return 'wrong announcement ownership'
 return None

def browser_failed(results):
 return any(r['result'] != 'PASS' for r in results)

async def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--browser',choices=['chromium','firefox','webkit','all'],default='all');ap.add_argument('--cdp',default='');ap.add_argument('--output');a=ap.parse_args()
 root=Path(a.root).resolve(); tmp=tempfile.TemporaryDirectory();(Path(tmp.name)/'Warlock').symlink_to(root)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=tmp.name));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/Warlock/'
 results=[]
 async with async_playwright() as pw:
  for name in (['chromium','firefox','webkit'] if a.browser=='all' else [a.browser]):
   browser=None
   try:
    browser=await (pw.chromium.connect_over_cdp(a.cdp) if name=='chromium' and a.cdp else getattr(pw,name).launch())
    ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce'); errors=[]
    async def route(r):
     if not r.request.url.startswith(base): errors.append('external request '+r.request.url);await r.abort()
     elif r.request.url.split('?')[0] == base+'test-drive/host/index.js':
      source=(root/'test-drive/host/index.js').read_text()
      marker="const deliver = (id, method, value) => send(id,'deliver',{method,value});"
      if marker not in source: raise RuntimeError('host instrumentation marker changed')
      source=source.replace("trace.push(item);", "trace.push(item); (window.__acceptanceDiagnostics ||= []).push(structuredClone(item));")
      source=source.replace(marker, "const deliver = (id, method, value) => { (window.__acceptancePackets ||= []).push({id,method,value:structuredClone(value)}); send(id,'deliver',{method,value}); };")
      await r.fulfill(status=200,content_type='text/javascript',body=source)
     elif r.request.url.split('?')[0] == base+'test-drive/bootstrap.js':
      # Instrument only the test response, never the published implementation.
      source=(root/'test-drive/bootstrap.js').read_text()
      marker="stage = stageModule.mountStage({root:document.getElementById('stage'), host});"
      if marker not in source: raise RuntimeError('bootstrap instrumentation marker changed')
      source=source.replace(marker, marker+'\n    window.__acceptanceHost = host;')
      await r.fulfill(status=200,content_type='text/javascript',body=source)
     else:await r.continue_()
    await ctx.route('**/*',route)
    async def scenario_case(scenario):
     page=await ctx.new_page(); local=[]
     page.on('pageerror',lambda e:local.append('page error '+str(e)))
     page.on('console',lambda m:local.append('console '+m.text) if m.type=='error' else None)
     page.on('response',lambda r:local.append(f'HTTP {r.status} {r.url}') if r.status>=400 else None)
     try:
      await page.goto(base+'test-drive/index.html?scenario='+scenario,wait_until='load',timeout=30000)
      await page.locator('#startup').wait_for(state='hidden',timeout=15000)
      await page.wait_for_function("() => window.__acceptanceHost?.getSnapshot()?.presentation?.actionable",timeout=15000)
      fixture=json.loads((root/'test-drive/scenarios'/f'{scenario}.json').read_text())
      expected=fixture['expectedObservations']
      await page.wait_for_function("""e => {const p=window.__acceptanceHost.getSnapshot().presentation; return p?.mode===e.mode && p.applied?.[e.surface]===p.publication && e.controls.every(id=>p.controls?.[e.surface]?.includes(id)) && (!e.status || e.status.some(x=>x.toLowerCase()===p.operationStatus?.toLowerCase()));}""",arg=expected,timeout=12000)
      if scenario=='preview-states':
       assert await page.frame_locator('#popup').locator('.window-preview').count()>0, 'preview content is missing'
      before=await page.evaluate('window.__acceptanceHost.getSnapshot()')
      packet_start=await page.evaluate('(window.__acceptancePackets || []).length')
      kind,identity=ACTIONS[scenario]
      frame=page.frame_locator('#bar' if kind=='bar' else '#popup')
      if kind=='field':
       control=frame.locator('[data-surface-field="'+identity+'"]')
       await control.fill('terminal',timeout=5000)
       await page.wait_for_timeout(300)
       assert await control.input_value()=='terminal', 'search query did not persist'
       # The renderer must publish query results, not merely accept text.
       await page.wait_for_function("n => window.__acceptanceHost.getSnapshot().presentation?.publication !== n",arg=before['presentation']['publication'],timeout=5000)
      else:
       selector=('[data-surface-control^="'+identity+'"]') if kind=='prefix' else ('[data-surface-control="'+identity+'"]')
       control=frame.locator(selector).first
       await control.click(timeout=5000)
       if scenario != 'snap':
        await page.wait_for_function("n => {let s=window.__acceptanceHost.getSnapshot(); return s.presentation?.publication !== n || !s.popupPlacement?.open}",arg=before['presentation']['publication'],timeout=5000)
      after=await page.evaluate('window.__acceptanceHost.getSnapshot()')
      if scenario=='taskbar':
       await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().presentation?.mode === 'system'",timeout=5000)
       after=await page.evaluate('window.__acceptanceHost.getSnapshot()')
       assert after['presentation']['mode']=='system', 'taskbar did not open System'
      elif scenario=='launcher':
       assert await frame.locator('[data-surface-control^="entry:"]').count()>0, 'search returned no application entries'
      elif scenario=='snap':
       assert await control.get_attribute('aria-current')=='true', 'snap region is not selected'
       await frame.locator('[data-surface-control="snap:apply"]').click(timeout=5000)
       await page.wait_for_function("n => window.__acceptancePackets.slice(n).some(p => p.value?.kind === 'effect-outcome' && p.value.intent?.operation === 'snap' && p.value.status === 'Committed')",arg=packet_start,timeout=5000)
       outcome=await page.evaluate("n => window.__acceptancePackets.slice(n).find(p => p.value?.kind === 'effect-outcome' && p.value.intent?.operation === 'snap').value",packet_start)
       geometry=outcome['intent']['placement']['geometry']
       await page.wait_for_function("({id,g}) => {const w=window.__acceptanceHost.getSnapshot().windows.find(w=>w.incarnation===id); return w && [w.geometry.x,w.geometry.y,w.geometry.width,w.geometry.height].every((v,i)=>v===g[i])}",arg={'id':outcome['intent']['incarnation'],'g':geometry},timeout=5000)
      elif scenario=='confirmation': await frame.locator('[data-surface-control="system:confirm"]').wait_for(state='detached',timeout=5000)
      elif scenario=='settings': await frame.locator('[data-surface-control="settings:theme:dawn"][aria-current="true"]').wait_for(timeout=5000)
      elif scenario=='switcher':
       selected=frame.locator('[data-surface-control^="switcher:family:"][aria-label*="selected"]')
       assert await selected.count()==1, 'candidate selection is not exposed'
       identity=await selected.get_attribute('data-surface-control')
       await frame.locator('[data-surface-control="control:commit"]').click(timeout=5000)
       await page.wait_for_function("id => window.__acceptanceHost.getSnapshot().windows.some(w=>w.incarnation===id && w.focused)",arg=identity.split(':')[-1],timeout=5000)
      elif scenario=='task-view':
       await frame.locator('[data-surface-control="overview:workspace:2"][aria-pressed="true"]').wait_for(timeout=5000)
      elif scenario=='transfer':
       await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().windows.some(w => w.id==='1' && w.workspace==='2')",timeout=5000)
      elif scenario in ('picker','preview-states'):
       await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().windows.some(w => w.id==='4' && w.focused)",timeout=5000)
      elif scenario=='notifications': await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().services?.notifications?.entries?.some(e => ['invoked','dismissed'].includes(e.state))",timeout=5000)
      elif scenario=='files': await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().services?.files?.peer?.target === 'home'",timeout=5000)
      elif scenario=='system': await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().services?.system?.volume?.percent === 25",timeout=5000)
      elif scenario=='window-menu': assert next(w for w in after['windows'] if w['id']=='1')['minimized'], 'window did not minimize'
      elif scenario=='application-actions': await page.wait_for_function('n => window.__acceptanceHost.getSnapshot().windows.length > n',arg=len(before['windows']),timeout=5000)
      elif scenario=='status-recovery':
       await page.wait_for_function("n => window.__acceptancePackets.slice(n).some(p => p.value?.kind === 'application-catalog')",arg=packet_start,timeout=5000)
      else: raise AssertionError('missing scenario assertion')
      if local: raise AssertionError('; '.join(local))
      results.append({'browser':name,'case':'scenario/'+scenario,'result':'PASS','detail':'scenario-specific behavior and admitted presentation asserted'})
     except Exception as e:results.append({'browser':name,'case':'scenario/'+scenario,'result':'FAIL','detail':str(e)})
     finally:await page.close()
    for scenario in SCENARIOS:
     await scenario_case(scenario)
    page=await ctx.new_page()
    for identity,expected in [('bar:system','system'),('bar:settings','settings')]:
     try:
      await page.goto(base+'test-drive/index.html',wait_until='load');await page.locator('#startup').wait_for(state='hidden',timeout=15000)
      await page.wait_for_function("() => {const p=window.__acceptanceHost?.getSnapshot()?.presentation;return p?.actionable && p.applied?.bar===p.publication}",timeout=15000)
      await page.frame_locator('#bar').locator('[data-surface-control="'+identity+'"]').click(timeout=5000)
      await page.frame_locator('#popup').locator('[data-mode="'+expected+'"]').wait_for(state='visible',timeout=5000)
      await page.frame_locator('#popup').locator('[data-mode="'+expected+'"] button:enabled').first.focus()
      diagnostic_start=await page.evaluate('(window.__acceptanceDiagnostics || []).length')
      await page.keyboard.press('Escape')
      await page.wait_for_function("n => (window.__acceptanceDiagnostics || []).slice(n).some(d => d.kind === 'focus-applied')",arg=diagnostic_start,timeout=5000)
      await page.frame_locator('#popup').locator('[data-mode="'+expected+'"]').wait_for(state='hidden',timeout=5000)
      assert await page.frame_locator('#bar').locator('[data-surface-control="'+identity+'"]').evaluate('e => e.ownerDocument.activeElement===e'), 'focus did not return to opener'
      results.append({'browser':name,'case':'control/'+identity,'result':'PASS','detail':'opened, dismissed and returned focus'})
     except Exception as e:results.append({'browser':name,'case':'control/'+identity,'result':'FAIL','detail':str(e)})
    try:
     await page.goto(base+'test-drive/index.html',wait_until='load');await page.locator('#bar').wait_for();await page.locator('#reset-button').click(timeout=5000)
     await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     results.append({'browser':name,'case':'reset','result':'PASS','detail':'desktop became ready after reset'})
    except Exception as e:results.append({'browser':name,'case':'reset','result':'FAIL','detail':str(e)})
    if errors:results.append({'browser':name,'case':'offline','result':'FAIL','detail':'; '.join(errors)})
    else:results.append({'browser':name,'case':'offline','result':'PASS','detail':'no external requests during executed cases'})
    async def check(case, action):
     try:
      await action()
      results.append({'browser':name,'case':case,'result':'PASS','detail':'assertions passed'})
     except Exception as e: results.append({'browser':name,'case':case,'result':'FAIL','detail':str(e)})
    async def ready():
     await page.goto(base+'test-drive/index.html',wait_until='load')
     await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     await page.wait_for_function("() => {const p=window.__acceptanceHost?.getSnapshot()?.presentation; return p?.actionable && p.applied?.bar===p.publication}",timeout=15000)
    async def keyboard():
     await ready(); await page.locator('#shortcuts-button').focus(); await page.keyboard.press('Enter')
     assert await page.locator('#shortcuts').is_visible(), 'keyboard did not open shortcuts'
     await page.locator('#help-button').focus(); await page.keyboard.press('Enter')
     assert await page.locator('#help').is_visible(), 'keyboard did not open help'
    async def narrow():
     await page.set_viewport_size({'width':320,'height':640}); await ready()
     await page.add_style_tag(content='* { letter-spacing: .12em !important; word-spacing: .16em !important; }')
     assert await page.locator('#stage').count() and await page.locator('#reset-button').is_visible(), 'desktop controls unavailable at 320px'
     await page.set_viewport_size({'width':1440,'height':900})
    async def forced():
     await page.emulate_media(forced_colors='active',reduced_motion='reduce'); await ready()
     assert await page.evaluate('matchMedia("(forced-colors: active)").matches && matchMedia("(prefers-reduced-motion: reduce)").matches'), 'media preferences not active'
     assert await page.locator('#reset-button').is_visible(), 'reset unavailable'
     await page.emulate_media(forced_colors='none',reduced_motion='reduce')
    async def epoch():
     await ready(); before=await page.evaluate('window.__acceptanceHost.getSnapshot().epoch')
     await page.locator('#reset-button').click(); await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     after=await page.evaluate('window.__acceptanceHost.getSnapshot().epoch')
     assert after>before, 'reset did not advance epoch'
    async def sustained():
     await ready()
     result=await page.evaluate('''() => { const h=window.__acceptanceHost; for(let i=0;i<100;i++) h.dispatchInput({kind:'viewport',width:1440,height:900}); return h.getSnapshot().output.width }''')
     assert result==1440 and await page.locator('#reset-button').is_visible(), 'batch left desktop unresponsive'
    await check('keyboard controls',keyboard)
    await check('320px and text spacing',narrow)
    await check('forced colors and reduced motion',forced)
    await check('reset epoch',epoch)
    await check('sustained viewport observations',sustained)
    async def ime():
     await ready(); await page.frame_locator('#bar').locator('[data-surface-control="bar:applications"]').click()
     field=page.frame_locator('#popup').locator('[data-surface-field="control:search"]')
     await field.wait_for(state='visible',timeout=5000); await field.focus()
     await field.evaluate("e => {e.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true,data:''})); e.value='漢'; e.dispatchEvent(new InputEvent('input',{bubbles:true,data:'漢',isComposing:true})); e.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'漢'})); e.dispatchEvent(new InputEvent('input',{bubbles:true,data:'漢'}));}")
     assert await field.input_value()=='漢', 'composed query was not retained'
    async def scaling():
     await page.set_viewport_size({'width':720,'height':450}); await ready()
     await page.evaluate("document.body.style.zoom='200%'")
     assert await page.locator('#reset-button').is_visible(), 'reset unavailable at 200% zoom'
     await page.evaluate("document.body.style.zoom=''"); await page.set_viewport_size({'width':1440,'height':900})
     await page.frame_locator('#bar').locator('[data-surface-control="bar:settings"]').click()
     for scale in (100,125,150,200):
      popup=page.frame_locator('#popup')
      choice=popup.locator(f'[data-surface-control="settings:scale:{scale}"]')
      if await choice.get_attribute('aria-current') != 'true':
       await choice.click(timeout=5000)
       await popup.locator('[data-surface-control="settings:save"]').click(timeout=5000)
      await page.wait_for_function('scale => Number(window.__acceptanceHost.getSnapshot().appearance.textScale) === scale',arg=scale,timeout=5000)
    async def focus_return():
     await ready(); opener=page.frame_locator('#bar').locator('[data-surface-control="bar:applications"]')
     await opener.focus(); await page.keyboard.press('Enter'); await page.frame_locator('#popup').locator('[data-mode="applications"]').wait_for(timeout=5000)
     await page.frame_locator('#popup').locator('[data-mode="applications"] [data-surface-field="control:search"]').focus()
     diagnostic_start=await page.evaluate('(window.__acceptanceDiagnostics || []).length')
     await page.keyboard.press('Escape'); await page.wait_for_function("n => (window.__acceptanceDiagnostics || []).slice(n).some(d => d.kind === 'focus-applied')",arg=diagnostic_start,timeout=5000)
     assert await opener.evaluate('e => e.ownerDocument.activeElement === e'), 'focus did not return to opener'
    async def announcement():
     await page.goto(base+'test-drive/index.html?scenario=status-recovery',wait_until='load')
     await page.wait_for_function("() => (window.__acceptancePackets || []).some(p => p.method === 'receiveAnnouncement' && p.value?.message)",timeout=15000)
     projections=await page.evaluate("(window.__acceptancePackets || []).filter(p => p.method === 'receiveAnnouncement' && p.value?.message)")
     assert projections, 'no nonempty announcement projection observed'
     for p in projections:
      v=p['value']
      assert bool(v['deliver']) == (v['recipient']==v['announcer']), 'announcement delivered to wrong surface'
    async def effects():
     await page.emulate_media(reduced_motion='no-preference'); await ready()
     await page.evaluate("window.__acceptanceHost.dispatchInput({kind:'system-motion-preference',profile:'full'})")
     await page.wait_for_function("() => document.querySelector('#stage').dataset.effectsTier==='full'",timeout=8000)
     before=await page.evaluate('window.__acceptanceHost.getSnapshot().windows.length')
     await page.evaluate("window.__acceptanceHost.dispatchInput({kind:'application',action:'launch',intent:{entry:'warlock-editor'}})")
     await page.locator('[data-portal-phase="open"][data-effects-tier="full"]').wait_for(state='attached',timeout=2000)
     assert await page.locator('[data-portal-phase="open"]').evaluate("e => { const s=getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && e.getBoundingClientRect().width > 0 && e.getAnimations().length > 0 && getComputedStyle(e,'::before').backgroundImage.includes('gradient') && getComputedStyle(e,'::before').content !== 'none' }"), 'opening portal is not painted and animated'
     await page.wait_for_timeout(150)
     portal=page.locator('[data-portal-phase="open"]')
     await portal.evaluate("e => e.getAnimations({subtree:true}).forEach(a => a.pause())")
     await page.screenshot(path='/tmp/warlock-desktop-portal-open.png')
     with_portal=await page.screenshot()
     await portal.evaluate("e => e.style.visibility='hidden'")
     without_portal=await page.screenshot()
     assert with_portal != without_portal, 'opening portal produced no screenshot paint difference'
     await portal.evaluate("e => {e.style.visibility='';e.getAnimations({subtree:true}).forEach(a => a.play())}")
     assert await page.evaluate('window.__acceptanceHost.getSnapshot().windows.length')==before+1, 'opening did not immediately create window'
     identity=await page.evaluate("() => {const s=window.__acceptanceHost.getSnapshot(), w=s.windows.at(-1); return {id:w.id,incarnation:w.incarnation,epoch:s.epoch}}")
     await page.locator('[data-portal-phase]').wait_for(state='detached',timeout=2000)
     await page.wait_for_timeout(1100)
     assert await page.evaluate("p => window.__acceptanceHost.dispatchInput({kind:'window',action:'close',windowId:p.id,incarnation:p.incarnation,epoch:p.epoch})",identity), 'close command rejected'
     assert await page.evaluate("p => !window.__acceptanceHost.getSnapshot().windows.some(w=>w.id===p.id && w.incarnation===p.incarnation)",identity), 'accepted close did not remove the window'
     await page.locator('[data-portal-phase="close"][data-effects-tier="full"]').wait_for(state='attached',timeout=2000)
     assert await page.locator('[data-portal-phase="close"]').evaluate("e => { const s=getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && e.getBoundingClientRect().width > 0 && e.getAnimations().length > 0 && getComputedStyle(e,'::before').backgroundImage.includes('gradient') && getComputedStyle(e,'::before').content !== 'none' }"), 'closing portal is not painted and animated'
     await page.wait_for_timeout(100)
     closing=page.locator('[data-portal-phase="close"]')
     await closing.evaluate("e => e.getAnimations({subtree:true}).forEach(a => a.pause())")
     await page.screenshot(path='/tmp/warlock-desktop-portal-close.png')
     assert await page.evaluate('window.__acceptanceHost.getSnapshot().windows.length')==before, 'closing did not immediately remove window'
     await page.locator('#reset-button').click(); await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     assert await page.locator('[data-portal-phase]').count()==0, 'reset retained portal decoration'
     await page.emulate_media(reduced_motion='reduce')
    async def stale():
     await ready(); old=await page.evaluate('window.__acceptanceHost.getSnapshot().epoch')
     await page.evaluate("window.__acceptanceHost.setFault('delayed')")
     await page.frame_locator('#bar').locator('[data-surface-control="bar:files"]').click()
     await page.locator('#reset-button').click(); await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     before=await page.evaluate('window.__acceptanceHost.getSnapshot()')
     await page.evaluate("epoch => window.dispatchEvent(new MessageEvent('message',{origin:location.origin,source:document.querySelector('#controller').contentWindow,data:{bridgeVersion:1,epoch,frameId:'controller',kind:'receipt',payload:{status:'completed'}}}))",old)
     await page.wait_for_timeout(300); after=await page.evaluate('window.__acceptanceHost.getSnapshot()')
     assert after['epoch']>old and after['windows']==before['windows'], 'stale receipt altered new epoch'
    async def batches():
     await ready()
     await page.frame_locator('#bar').locator('[data-surface-control="bar:system"]').click(timeout=5000)
     await page.frame_locator('#popup').locator('[data-mode="system"]').wait_for(timeout=5000)
     for i in range(20):
      await page.frame_locator('#popup').locator('[data-surface-control="system:volume-set:'+('25' if i%2==0 else '50')+'"]').click(timeout=5000)
      await page.wait_for_function('v => window.__acceptanceHost.getSnapshot().services?.system?.volume?.percent === v',arg=25 if i%2==0 else 50,timeout=5000)
     packets=await page.evaluate('window.__acceptancePackets')
     certificates=[p['value'] for p in packets if p.get('method')=='receiveBatchDisposition']
     assert len(certificates)>16, f'only {len(certificates)} batch dispositions observed'
     assert all(c.get('disposition')=='admitted' for c in certificates), 'batch disposition was not admitted'
     outcomes=[p['value'] for p in packets if p.get('value',{}).get('kind')=='system-menu-outcome']
     assert len(outcomes)>=20 and all(o.get('status')=='Committed' for o in outcomes), f'only {len(outcomes)} committed system outcomes'
     assert await page.locator('#reset-button').is_visible(), 'controls unavailable after batches'
    async def narrow_tour():
     await page.set_viewport_size({'width':320,'height':640}); await ready()
     await page.locator('#tour-button').click(); panel=page.locator('.wl-tour:not([hidden])'); await panel.wait_for()
     boxes=await page.evaluate("""() => {const p=document.querySelector('.wl-tour:not([hidden])').getBoundingClientRect(), t=document.querySelector('.desktop-tools').getBoundingClientRect();return {p:{top:p.top,bottom:p.bottom,left:p.left,right:p.right},t:{top:t.top,bottom:t.bottom},width:innerWidth,height:innerHeight}}""")
     assert boxes['p']['left']>=0 and boxes['p']['right']<=boxes['width'] and boxes['p']['bottom']<=boxes['height'], 'tour escapes viewport'
     assert boxes['t']['bottom']<=boxes['p']['top'], 'tour overlaps desktop toolbar'
     await panel.get_by_role('button',name='Exit tour').click(); await page.set_viewport_size({'width':1440,'height':900})
    async def fractional_geometry():
     await ready()
     await page.evaluate("window.__acceptanceHost.dispatchInput({kind:'viewport',width:1000.5,height:700.5})")
     snap=await page.evaluate('window.__acceptanceHost.getSnapshot()')
     assert all(all(isinstance(w['geometry'][k],(int,float)) for k in ('x','y','width','height')) for w in snap['windows']), 'invalid window geometry'
     assert await page.locator('#reset-button').is_visible(), 'fractional observation made controls unavailable'
    async def focus_race():
     await ready(); bar=page.frame_locator('#bar'); popup=page.frame_locator('#popup')
     await bar.locator('[data-surface-control="bar:applications"]').click()
     await popup.locator('[data-mode="applications"]').wait_for(timeout=5000)
     await popup.locator('[data-surface-field="control:search"]').focus()
     await page.keyboard.press('Escape')
     await bar.locator('[data-surface-control="bar:system"]').click()
     await popup.locator('[data-mode="system"]').wait_for(timeout=5000)
     await page.wait_for_function("() => window.__acceptanceHost.getSnapshot().presentation?.mode === 'system' && window.__acceptanceHost.getSnapshot().presentation?.actionable",timeout=5000)
     assert await popup.locator('[data-mode="system"]').is_visible(), 'stale dismissal closed newer popup'
    async def default_gestures():
     await ready(); bar=page.frame_locator('#bar'); popup=page.frame_locator('#popup')
     for identity,mode in [('bar:applications','applications'),('bar:system','system'),('bar:settings','settings')]:
      await bar.locator('[data-surface-control="'+identity+'"]').click(timeout=5000)
      await popup.locator('[data-mode="'+mode+'"]').wait_for(state='visible',timeout=5000)
      await page.keyboard.press('Escape')
      await popup.locator('[data-mode="'+mode+'"]').wait_for(state='hidden',timeout=5000)
    async def unpinned_group():
     await ready(); bar=page.frame_locator('#bar'); popup=page.frame_locator('#popup')
     await page.evaluate("window.__acceptanceHost.dispatchInput({kind:'application',action:'launch',intent:{entry:'warlock-files'}})")
     groups=bar.locator('[data-surface-control^="bar:group:"]')
     await groups.first.wait_for(state='visible',timeout=5000)
     group=groups.first; identity=await group.get_attribute('data-surface-control')
     await group.click(button='right',timeout=5000)
     await page.wait_for_function("() => ['picker','menu'].includes(window.__acceptanceHost.getSnapshot().presentation?.mode)",timeout=5000)
     assert await popup.locator('[data-mode="picker"], [data-mode="menu"]').is_visible(), 'unpinned group did not open its window actions: '+identity
    async def repeated_snap_restore():
     await page.goto(base+'test-drive/index.html?scenario=snap',wait_until='load')
     await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     popup=page.frame_locator('#popup')
     await popup.locator('[data-surface-control="snap:apply"]').wait_for(timeout=15000)
     original=await page.evaluate("() => {let s=window.__acceptanceHost.getSnapshot(), w=s.windows.find(w=>w.focused); return {id:w.id,incarnation:w.incarnation,epoch:s.epoch,geometry:w.geometry}}")
     for i in range(2):
      if i:
       await popup.locator('[data-mode="menu"]').wait_for(state='hidden',timeout=5000)
       await page.wait_for_function("() => {const p=window.__acceptanceHost.getSnapshot().presentation; return p?.actionable && p.applied?.bar===p.publication}",timeout=5000)
       assert await page.evaluate("() => window.__acceptanceHost.invoke('snap')"), f'snap entry failed in cycle {i+1}'
      await popup.locator('[data-surface-control="snap:region:left-half"]').click(timeout=5000)
      await popup.locator('[data-surface-control="snap:apply"]').click(timeout=5000)
      await page.wait_for_function("id => window.__acceptanceHost.getSnapshot().windows.find(w=>w.id===id)?.placementMode==='snapped'",arg=original['id'],timeout=5000)
      assert await page.evaluate("() => window.__acceptanceHost.invoke('window-menu')"), 'window menu entry failed'
      restore=popup.get_by_role('button',name='Restore size',exact=False)
      assert not await restore.is_visible(), 'snapped ordinary window incorrectly offers maximized restore'
      identity=await page.evaluate("id => {const s=window.__acceptanceHost.getSnapshot(), w=s.windows.find(w=>w.id===id); return {id:w.id,incarnation:w.incarnation,epoch:s.epoch}}",original['id'])
      assert await page.evaluate("p => window.__acceptanceHost.dispatchInput({kind:'window',action:'restore-geometry',windowId:p.id,incarnation:p.incarnation,epoch:p.epoch})",identity), 'host restore rejected'
      await page.wait_for_function("id => window.__acceptanceHost.getSnapshot().windows.find(w=>w.id===id)?.placementMode!=='snapped'",arg=original['id'],timeout=5000)
      actual=await page.evaluate("id => window.__acceptanceHost.getSnapshot().windows.find(w=>w.id===id).geometry",original['id'])
      assert actual==original['geometry'], f'restore cycle {i+1} did not recover original geometry: {actual}'
    async def stale_window_identity():
     await ready()
     before=await page.evaluate('window.__acceptanceHost.getSnapshot()')
     w=next(w for w in before['windows'] if w['focused'])
     for action in ('close','restore-geometry'):
      for epoch,incarnation in ((before['epoch']-1,w['incarnation']),(before['epoch'],'stale-incarnation')):
       accepted=await page.evaluate("p => window.__acceptanceHost.dispatchInput({kind:'window',action:p.action,windowId:p.id,incarnation:p.incarnation,epoch:p.epoch})",{'action':action,'id':w['id'],'incarnation':incarnation,'epoch':epoch})
       assert not accepted, f'{action} accepted stale window identity'
       assert await page.evaluate('window.__acceptanceHost.getSnapshot().windows')==before['windows'], f'{action} changed windows with stale identity'
    async def preview_stability():
     await page.goto(base+'test-drive/index.html?scenario=preview-states',wait_until='load')
     await page.locator('#startup').wait_for(state='hidden',timeout=15000)
     row=page.frame_locator('#popup').locator('[data-surface-control="family:4"]')
     await row.wait_for(state='visible',timeout=10000)
     before=await row.bounding_box(); await page.wait_for_timeout(1000); after=await row.bounding_box()
     assert before and after and all(abs(before[k]-after[k])<1 for k in ('x','y','width','height')), 'preview target moved after publication'
    async def client_control_overlap():
     await ready()
     overlap=await page.evaluate("""() => {let controls=[...document.querySelectorAll('.desktop-tools button')].map(e=>e.getBoundingClientRect());return [...document.querySelectorAll('.stage-client')].some(e=>{let a=e.getBoundingClientRect();return controls.some(b=>a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)})}""")
     assert not overlap, 'desktop controls overlap client content'
    await check('default desktop taskbar gestures',default_gestures)
    await check('unpinned group routing',unpinned_group)
    await check('repeated snap and restore',repeated_snap_restore)
    await check('stale window identity rejection',stale_window_identity)
    await check('preview target stability',preview_stability)
    await check('client and control overlap',client_control_overlap)
    await check('narrow tour and toolbar overlap',narrow_tour)
    await check('fractional geometry',fractional_geometry)
    await check('dismissal focus race',focus_race)
    await check('IME composition',ime)
    await check('200% zoom and desktop text scales',scaling)
    await check('focus return',focus_return)
    await check('refusal announcement ownership',announcement)
    await check('effects interruption and rapid creation',effects)
    await check('stale receipts and pending reset',stale)
    await check('sustained controller request batches',batches)
    await ctx.close()
   except Exception as e:results.append({'browser':name,'case':'browser startup','result':'NOT RUN' if ("Executable doesn't exist" in str(e) or 'Host system is missing dependencies' in str(e) or 'error while loading shared libraries' in str(e)) else 'FAIL','detail':str(e)})
   finally:
    if browser:await browser.close()
 server.shutdown();tmp.cleanup();out=json.dumps(results,indent=2);print(out)
 if a.output:Path(a.output).write_text(out+'\n')
 return int(browser_failed(results))
if __name__=='__main__':sys.exit(asyncio.run(main()))
