"""Source proposal only: B13–B16 methods after separate registry scope review.
No entry point, imports do not launch; existing core/observer/controller untouched.
"""
CASES=('B13','B14','B15','B16')

def require(ok,message):
 if ok is not True:raise ValueError(message)

def selected(c,actor):
 captures={name:c.capture(actor,name)for name in ['owner','peer']}
 return captures,{name:c.snapshot(token)['body']for name,token in captures.items()}

def conserved(c,before,after,fields):
 require(all(c.decoder.exact(before[name][k],after[name][k])for name in before for k in fields),'same actual masks-query scope/ordinary input/pin/mode/geometry')

FIELDS=['owner','mapped','hidden','acceptsInput','noFocus','priorityFocus','pinned','floating','internalMode','clientMode','target','space','workspace','output','logicalBox','visualBox','restoreValid','restoreGeneration','restoreLogicalBox','restoreVisualBox']

def query(c,actor,captured,point,mask,ignore=False):
 tokens,before=selected(c,actor)
 require(c.decoder.exact(tokens['owner']if c.authority.matches(tokens['owner'],captured)else tokens['peer'],captured),'same full current selected query token')
 probe=c.old_probe('state');c.authority.input_safe(probe)
 coordinates=probe.get('cursor');require(type(coordinates)is list and len(coordinates)==2 and all(type(v)in {int,float}for v in coordinates)and coordinates==point,'actual physical recorded current point before native query')
 result=c.snapshot(captured,mask,ignore)
 after_tokens,after=selected(c,actor);require(c.decoder.exact(tokens,after_tokens),'mask query cannot replace current selected members')
 conserved(c,before,after,FIELDS)
 hit=result['hitOwner']
 if ignore:require(not c.authority.matches(hit,captured),'selected exact ignoreWindow excluded owner never returned')
 require(hit is None or any(c.authority.matches(hit,t)for t in tokens.values()),'no unknown query winner admitted')
 # A returned candidate is checked against actual current owning metadata.
 # No assumption that a nonphysical mask is used by InputManager.
 if hit is not None:
  name=next(name for name,t in tokens.items()if c.authority.matches(hit,t));candidate=after[name]
  require(candidate['mapped']is True and candidate['hidden']is False and candidate['acceptsInput']is True and candidate['noFocus']is False,'actual query candidate eligibility')
  if mask==1:require(candidate['floating']is True,'FLOATING_ONLY cannot revive tiled target')
  if mask==2:require(candidate['priorityFocus']is True,'FOCUS_PRIORITY cannot fabricate native async-dialog priority')
  if mask==4 and candidate['pinned']is True:require(candidate['floating']is False,'WINDOW_ONLY cannot revive protected floating target')
 return dict(raw=result,point=point,before=before,after=after,maskId=mask,ignoreOwner=ignore,nativeQueryComponentOnly=True,physicalCallerUsesMaskAccepted=False,blanketNoNativeWrites=False)

def with_pointer(c,case,ordinal):
 proc,row=c.registry.launch(case,'pointer',ordinal)
 return dict(proc=proc,row=row,held=False)

def run_case(c,case,actor):
 require(case in CASES,'only four mask/exclusion source-proposal cases')
 if case=='B13':
  reached=c.retained_tiled(case,actor);owner=c.capture(actor);peer=c.capture(actor,'peer')
  c.setup('explicit ordinary independent floating peer','hl.dsp.window.float({action="set",window='+__import__('json').dumps('address:'+peer['address'])+'})')
  c.wait('actual independent ordinary peer floating',lambda:c.public(actor,'peer')if c.public(actor,'peer')['floating']is True else None)
  point=c.qt_point(actor,'peer',peer);owner_box=c.snapshot(owner)['body']['visualBox']
  require(not c.point_inside(point,owner_box),'actual independent peer button point outside protected owner return box; no geometry compensation')
  tokens,before=selected(c,actor);click=c.click_fixture(case,actor,'peer',1,point_override=point)
  after_tokens,after=selected(c,actor);require(c.decoder.exact(tokens,after_tokens),'same current outside-box members')
  conserved(c,before,after,FIELDS);require(c.authority.matches(click['native']['hitOwner'],peer),'actual outside-box peer hit')
  c.pin_keyboard(case,actor,2)
  return dict(case=case,reached=reached,ownerVisualBox=owner_box,click=click,actualOutsideBoxComponent=True,belowFullscreenBlockedPeerPresent=False,fullDesignCaseAccepted=False)
 if case=='B14':
  maximum=c.native_mode(actor,'owner','maximized','set');c.pin_keyboard(case,actor,1);owner=c.capture(actor)
  point=c.qt_point(actor,'owner',owner);click=c.click_fixture(case,actor,'owner',1,point_override=point)
  pointer=with_pointer(c,case,2)
  try:
   c.move_pointer(pointer,point,owner);ignored=query(c,actor,owner,point,0,True)
  finally:c.close_pointer(pointer)
  c.pin_keyboard(case,actor,2);c.native_mode(actor,'owner','maximized','unset')
  return dict(case=case,maximum=maximum,realDefaultInput=click,ignoredQuery=ignored,nativeIgnoreQueryAccepted=True,physicalIgnoredCallerAccepted=False,fullDesignCaseAccepted=False)
 if case=='B15':
  reached=c.retained_tiled(case,actor);owner=c.capture(actor);peer=c.capture(actor,'peer')
  c.setup('explicit independent ordinary floating peer','hl.dsp.window.float({action="set",window='+__import__('json').dumps('address:'+peer['address'])+'})')
  c.wait('actual current floating peer',lambda:c.public(actor,'peer')if c.public(actor,'peer')['floating']is True else None)
  c.pin_keyboard(case,actor,2,'peer');peer=c.capture(actor,'peer');point=c.qt_point(actor,'peer',peer)
  pointer=with_pointer(c,case,1)
  try:
   c.move_pointer(pointer,point,peer);floating=query(c,actor,owner,point,1)
   require(c.authority.matches(floating['raw']['hitOwner'],peer),'real protected floating lifetime positive FLOATING_ONLY native query')
   window_only=query(c,actor,peer,point,4)
   require(not c.authority.matches(window_only['raw']['hitOwner'],peer),'protected floating owner excluded by no-ALLOW_FLOATING mask')
   owner_point=c.qt_point(actor,'owner',owner);c.move_pointer(pointer,owner_point)
   tile_excluded=query(c,actor,owner,owner_point,1)
   require(not c.authority.matches(tile_excluded['raw']['hitOwner'],owner),'FLOATING_ONLY excludes actual protected tiled lifetime')
  finally:c.close_pointer(pointer)
  c.pin_keyboard(case,actor,3,'peer');c.pin_keyboard(case,actor,4)
  return dict(case=case,reached=reached,floatingOnly=floating,windowOnly=window_only,tiledExcluded=tile_excluded,fixedMaskQueryComponentAccepted=True,physicalMaskedCallerAccepted=False,fullDesignCaseAccepted=False)
 # B16: actual Qt modal does NOT imply core CAsyncDialogBox priorityFocus.
 reached=c.retained_tiled(case,actor);owner=c.capture(actor)
 ordinary=c.native_mode(actor,'peer','maximized','set');tokens,before=selected(c,actor)
 require(all(row['priorityFocus']is False for row in before.values()),'actual ordinary Qt native priority false; no invented priority dialog')
 point=c.qt_point(actor,'owner',owner);pointer=with_pointer(c,case,1)
 try:
  c.move_pointer(pointer,point,owner);priority=query(c,actor,owner,point,2)
  require(priority['raw']['hitOwner']is None,'all selected Qt targets ineligible under genuine FOCUS_PRIORITY query')
  skipped=query(c,actor,owner,point,3)
  require(c.authority.matches(skipped['raw']['hitOwner'],owner),'genuine protected tiled hit survives skip ordinary MAX priority')
 finally:c.close_pointer(pointer)
 c.native_mode(actor,'peer','maximized','unset');c.pin_keyboard(case,actor,2)
 return dict(case=case,reached=reached,ordinaryMaximum=ordinary,priorityNegative=priority,skipFullscreen=skipped,positiveNativePriorityReachability=False,physicalMaskedCallerAccepted=False,fullDesignCaseAccepted=False)
