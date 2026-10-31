/** Tour controls observe the live renderer and never dispatch product actions themselves. */
export function mountTour({host, stage, root}) {
  let steps=[], index=0, opener=null, unsubscribe=null, generation=0, complete=false, epoch=null, observer=null, documents=[], confirmationSeen=false, pendingFocus=null, baseline=null, pendingSelection=null, selectionBaseline=null, faultPolicy='success', activationRequested=false;
  const panel=document.createElement('section'); panel.className='wl-tour'; panel.hidden=true; panel.setAttribute('aria-label','Desktop tour'); root.append(panel);
  const outline=document.createElement('div'); outline.className='wl-tour-anchor'; outline.hidden=true; outline.setAttribute('aria-hidden','true'); root.append(outline);
  // A tour changes the usable desktop height without resizing the browser.
  // Publish that geometry through the same viewport input used by bootstrap.
  const desktop=document.getElementById('desktop');
  const desktopSize=new ResizeObserver(()=>{
    if(desktop) host.dispatchInput({kind:'viewport',width:desktop.clientWidth,height:desktop.clientHeight});
  });
  if(desktop) desktopSize.observe(desktop);
  const definitions={
    '1':['bar','[data-surface-control^="bar:pin:"][aria-pressed="false"]'], '2':['popup','[data-surface-field="control:search"]'],
    '3':['popup','[data-surface-control^="switcher:family:"]'], '4':['popup','[data-surface-control="overview:all"]'],
    '5':['popup','[data-surface-control="overview:go:3"]'], '6':['popup','[data-surface-control^="overview:transfer:"], [data-surface-control^="overview:destination:"]'],
    'focus-group':['popup','[data-surface-control^="switcher:family:"]'], '7':['popup','[data-surface-control^="family:"]'], activate:['popup','[data-surface-control^="family:"]'], '8':['popup','[data-surface-control="snap:apply"]'],
    '9':['popup','[data-mode="menu"]'], '10':['popup','[data-mode="jump"]'], '11':['popup','[data-mode="notifications"]'],
    '12':['popup','[data-surface-control="settings:theme:night"]'], motion:['popup','[data-surface-control="settings:motion:reduced"]'],
    shortcuts:['popup','[data-surface-control="settings:shortcuts:applications:keep"]'], help:['popup','[data-surface-control="settings:help"]'],
    '14':['popup','[data-surface-control="files:refresh"]'], '15':['popup','[data-mode="system"]'],
    '16':['popup','[data-mode="system"]'], '17':['popup','[data-surface-control="files:refresh"]']
  };
  function frame(name){return stage.getAnchors()?.[name];}
  function live(name){
    const f=frame(name), doc=f?.contentDocument, surface=doc?.querySelector(name==='popup'?'.surface-popup':'[data-publication]');
    const snapshot=host.getSnapshot();
    if(!f || f.hidden || !surface || !snapshot.presentation?.actionable || surface.dataset.publication!==snapshot.presentation.publication) return null;
    return {f,doc,surface};
  }
  function target(step){const definition=definitions[step?.id];if(!definition)return null;const [name,selector]=definition;const entry=live(name);if(!entry)return null;const node=entry.surface.matches(selector)?entry.surface:entry.surface.querySelector(selector);return node?{...entry,node}:null;}
  function position(){
    const t=target(steps[index]||{}); if(!t){outline.hidden=true;return;}
    const a=t.f.getBoundingClientRect(), b=t.node.getBoundingClientRect();
    const left=Math.max(a.left,a.left+b.left), top=Math.max(a.top,a.top+b.top), right=Math.min(a.right,a.left+b.right), bottom=Math.min(a.bottom,a.top+b.bottom);
    if(right<=left||bottom<=top){outline.hidden=true;return;}
    Object.assign(outline.style,{left:`${left}px`,top:`${top}px`,width:`${right-left}px`,height:`${bottom-top}px`});outline.hidden=false;
  }
  function button(label, action){const b=document.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',action);return b;}
  function render(announce=false){
    const step=steps[index];if(!step)return;
    const focused=panel.contains(document.activeElement)?document.activeElement.textContent:null;panel.replaceChildren();
    const progress=document.createElement('p');progress.textContent=`Step ${index+1} of ${steps.length}`;
    const title=document.createElement('h2');title.textContent=step.title;
    const instruction=document.createElement('p');instruction.textContent=step.instruction;if(announce){instruction.setAttribute('role','status');instruction.setAttribute('aria-live','polite');}
    const link=document.createElement('a');link.href=`../components/${step.component}/index.html`;link.textContent='Read component guidance';
    const progressDetails=document.createElement('details');const progressSummary=document.createElement('summary');progressSummary.textContent='Tour progress';progressDetails.append(progressSummary);
    const list=document.createElement('ol');list.className='wl-tour-progress';list.setAttribute('aria-label','Tour progress');steps.forEach((item,i)=>{const li=document.createElement('li');li.textContent=item.title;if(i===index)li.setAttribute('aria-current','step');list.append(li);});progressDetails.append(list);
    const notice=document.createElement('p');notice.textContent=complete?'Action observed. Continue when ready.':'Complete the action to continue, or skip this step.';
    const controls=document.createElement('div');controls.className='wl-tour-controls';
    const move=delta=>{pendingFocus?.();pendingFocus=null;index+=delta;complete=false;confirmationSeen=false;activationRequested=false;pendingSelection=null;baseline=host.getSnapshot();selectionBaseline=selection(steps[index]);render(true);update();};
    const back=button('Back',()=>move(-1));back.disabled=index===0;
    const next=button(index===steps.length-1?'Finish':'Next',()=>index===steps.length-1?stop():move(1));next.disabled=!complete;
    const show=button('Show me',async()=>{const token=generation;if(step.id==='float-window'){const s=host.getSnapshot(),w=s.windows.find(w=>w.focused&&!w.minimized&&!w.owner&&(w.workspace===s.activeWorkspace||w.pinned));if(!w){notice.textContent='Activate a window first.';return;}const input={kind:'pointer',windowId:w.id,incarnation:w.incarnation,epoch:s.epoch,pointerId:1,mode:'move',x:w.geometry.x,y:w.geometry.y};if(host.dispatchInput({...input,action:'start'})) host.dispatchInput({...input,action:'end',currentX:w.geometry.x+8,currentY:w.geometry.y+8});update();return;}const desired=step.scenario==='confirmation'?'system':step.scenario==='status-recovery'?'files':step.scenario;if(target(step))return;const result=await host.invoke(desired);if(token===generation&&result===false)notice.textContent='This desktop entry is not available. Use the taskbar to focus a window, then try again.';});
    controls.append(back,next,show,button('Skip',()=>index===steps.length-1?stop():move(1)),button('Exit tour',stop));
    const diagnostics=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Diagnostics';diagnostics.append(summary);
    const label=document.createElement('label');label.textContent='Simulated service response ';const select=document.createElement('select');for(const [value,text] of [['success','Success'],['delayed','Delayed'],['refusal','Refused'],['unknown','Unknown'],['connection-loss','Unavailable']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}select.value=faultPolicy;select.addEventListener('change',()=>{host.setFault(select.value);faultPolicy=select.value;});label.append(select);diagnostics.append(label);
    panel.append(progress,title,instruction,link,controls,notice,progressDetails,diagnostics);if(focused)[...panel.querySelectorAll('button')].find(b=>b.textContent===focused&&!b.disabled)?.focus();position();
  }
  function mark(){if(!complete){complete=true;render();}}
  function selection(step){const surface=live('popup')?.surface;if(!surface)return null;const prefix=step?.id==='motion'?'settings:motion:':step?.id==='shortcuts'?'settings:shortcuts:applications:':null;if(prefix)return surface.querySelector(`[data-surface-control^="${prefix}"][aria-current="true"]`)?.dataset.surfaceControl||null;if(step?.id==='help')return surface.querySelector('[data-surface-control="settings:help"]')?.getAttribute('aria-expanded')||null;return null;}
  function update(){if(panel.hidden)return;const snapshot=host.getSnapshot();if(snapshot.epoch!==epoch){stop();return;}const step=steps[index];if(step.id==='1'&&snapshot.windows.find(w=>w.focused)?.id!==baseline?.windows.find(w=>w.focused)?.id)mark();if(step.id==='5'&&snapshot.activeWorkspace==='3')mark();if(step.id==='focus-group'&&snapshot.windows.some(w=>w.focused&&!w.minimized&&(w.workspace===snapshot.activeWorkspace||w.pinned)&&snapshot.windows.filter(other=>other.application===w.application).length>1))mark();if(step.id==='float-window'&&snapshot.windows.some(w=>w.focused&&!w.minimized&&!w.owner&&(w.workspace===snapshot.activeWorkspace||w.pinned)&&['floating','snapped'].includes(w.placementMode)))mark();if(step.id==='activate'&&snapshot.windows.some(w=>w.focused&&!w.minimized&&(w.workspace===snapshot.activeWorkspace||w.pinned)&&w.incarnation!==baseline?.windows.find(previous=>previous.focused)?.incarnation))mark();const selected=selection(step);if(step.id==='help'&&selected==='true')mark();if(selected&&selectionBaseline&&selected!==selectionBaseline&&(['motion','shortcuts'].includes(step.id)||(step.id==='help'&&selected==='true')))mark();const t=target(step);if(t&&['3','4','6','7','8','9','10','11','12','14','15'].includes(step.id)&&(step.id!=='6'||t.surface.querySelector('[data-surface-control^="overview:destination:"]')))mark();position();}
  function onInteraction(event){
    if(panel.hidden || !event.isTrusted)return;
    const step=steps[index], node=event.target.closest?.('[data-surface-control], [data-surface-field]');if(!node)return;
    const name=event.currentTarget===frame('bar')?.contentDocument?'bar':'popup';const surface=event.currentTarget.querySelector(name==='popup'?'.surface-popup':'[data-publication]');if(!surface?.contains(node))return;
    const id=node.dataset.surfaceControl||node.dataset.surfaceField;
    if(event.type==='input'&&step.id==='2'&&id==='control:search'&&node.value.trim())mark();
    if(event.type!=='click')return;
    if(step.id==='1'&&name==='bar'&&id.startsWith('bar:pin:')) {const before=host.getSnapshot().windows.find(w=>w.focused)?.id;pendingFocus?.();pendingFocus=host.subscribe(s=>{if(s.epoch!==epoch||s.windows.find(w=>w.focused)?.id!==before){pendingFocus?.();pendingFocus=null;if(s.epoch===epoch)mark();}});return;}
    if(step.id==='activate'&&id.startsWith('family:')){activationRequested=id.slice('family:'.length);update();return;}
    if(step.id==='5')return;
    if(step.id==='6'&&id.startsWith('overview:transfer:'))return;
    if(step.id==='16'){if(id==='system:cancel')mark();return;}
    if(step.id==='17'&&id==='files:refresh')mark();
    if(step.id==='motion'&&id.startsWith('settings:motion:')&&!['settings:motion:save','settings:motion:refresh'].includes(id)&&node.getAttribute('aria-current')!=='true')pendingSelection={id,attribute:'aria-current'};
    if(step.id==='shortcuts'&&id.startsWith('settings:shortcuts:applications:')&&!id.endsWith(':state')&&node.getAttribute('aria-current')!=='true')pendingSelection={id,attribute:'aria-current'};
    if(step.id==='help'&&id==='settings:help'&&node.getAttribute('aria-expanded')==='false')pendingSelection={id,attribute:'aria-expanded'};
  }
  function observe(){
    observer?.disconnect();documents.forEach(d=>{d.removeEventListener('click',onInteraction,true);d.removeEventListener('input',onInteraction,true);});documents=[];
    observer=new MutationObserver(()=>{if(panel.hidden)return;const step=steps[index], t=target(step);if(pendingSelection){const selected=live('popup')?.surface.querySelector(`[data-surface-control="${pendingSelection.id}"]`);if(selected?.getAttribute(pendingSelection.attribute)==='true'){pendingSelection=null;mark();}}if(step.id==='16'&&live('popup')?.surface.querySelector('[data-surface-control="system:cancel"]'))confirmationSeen=true;
      if(t&&['3','4','6','7','8','9','10','11','12','14','15'].includes(step.id)) {if(step.id!=='6'||t.surface.querySelector('[data-surface-control^="overview:destination:"]'))mark();}update();});
    for(const name of ['bar','popup']){const doc=frame(name)?.contentDocument;if(!doc)continue;documents.push(doc);doc.addEventListener('click',onInteraction,true);doc.addEventListener('input',onInteraction,true);observer.observe(doc,{subtree:true,childList:true,attributes:true,characterData:true});}
  }
  async function start(){if(!panel.hidden)stop();const current=++generation;opener=document.activeElement;host.setFault('success');faultPolicy='success';const response=await fetch(new URL('./steps.json',import.meta.url));if(!response.ok)throw new Error('Could not load tour');const data=await response.json();if(current!==generation)return;steps=data.steps;index=0;complete=false;baseline=host.getSnapshot();epoch=baseline.epoch;panel.hidden=false;observe();render(true);panel.querySelector('button:not(:disabled)')?.focus();unsubscribe?.();unsubscribe=host.subscribe(update);update();}
  function stop(){generation++;host.setFault('success');faultPolicy='success';pendingFocus?.();pendingFocus=null;pendingSelection=null;unsubscribe?.();unsubscribe=null;observer?.disconnect();documents.forEach(d=>{d.removeEventListener('click',onInteraction,true);d.removeEventListener('input',onInteraction,true);});documents=[];outline.hidden=true;panel.hidden=true;panel.replaceChildren();if(opener?.isConnected)opener.focus();opener=null;}
  addEventListener('resize',position);addEventListener('scroll',position,true);
  return {start,stop,destroy(){stop();desktopSize.disconnect();removeEventListener('resize',position);removeEventListener('scroll',position,true);outline.remove();panel.remove();}};
}
