"""Reviewed source-only native blocker/B12 components. Import never launches."""
import json
from minimal_controller import MinimalController,require
CASES={'B11':('B11',),'B12':('B12',),'B11+B12':('B11','B12')}
CONTEXT=['owner','mapped','hidden','noFocus','priorityFocus','pinned','floating','internalMode','clientMode','fullscreenHandler','target','space','workspace','output','logicalBox','visualBox','restoreValid','restoreGeneration','restoreLogicalBox','restoreVisualBox','restoreFloating','restoreLayoutHandled','restoreTarget','restoreLayoutTarget','restoreSpace','restoreOrigin','restoreManaged','ownedUnpinReady','group','groupMembers']

class BlockController(MinimalController):
 def actual_workspace(self,workspace,layout,windows,last=None):
  values=self.raw('actual strong-owning tiledLayout public projection',lambda:self.session.data('workspaces'))
  require(type(values)is list,'actual complete workspace list')
  rows=[r for r in values if type(r)is dict and type(r.get('id'))is int and r['id']==workspace]
  require(len(rows)==1,'one selected actual native workspace')
  row=rows[0]
  require(type(row.get('monitorID'))is int and row['monitorID']==0 and row.get('tiledLayout')==layout and type(row.get('windows'))is int and row['windows']==windows and row.get('hasfullscreen')is False,'current owning algorithm/output/member count/no native fullscreen')
  if last is not None:require(row.get('lastwindow')==last['address'],'actual owning workspace current target')
  return row
 def scope(self,actor,tokens,active):
  require(active in {'owner','peer'},'fixed selected active target')
  captures={name:self.capture(actor,name)for name in ['owner','peer']}
  require(self.decoder.exact(captures,tokens),'same exact source/root/member lifetimes')
  owned={name:self.snapshot(token)for name,token in captures.items()}
  for name,record in owned.items():
   body=record['body']
   require(body['mapped']is True and body['hidden']is False and body['noFocus']is False and body['floating']is False and type(body['internalMode'])is int and body['internalMode']==0 and type(body['clientMode'])is int and body['clientMode']==0,'isolated mapped/unhidden/noFocusFalse normal tiled members')
   require(body['group']=='0x0'and self.decoder.exact(body['groupMembers'],[]),'no native group block or inherited group intent')
   require(body['pinned']is (name=='owner'),'independent selected pin intent only')
   require(body['acceptsInput']is (name==active),'actual source-selected native active/inactive input state')
   public=self.public(actor,name)
   require(type(public.get('workspace'))is dict and type(public['workspace'].get('id'))is int and public['workspace']['id']==11 and type(public.get('monitor'))is int and public['monitor']==0,'same current public workspace/output')
  require(all(self.decoder.exact(owned['owner']['body'][k],owned['peer']['body'][k])for k in ['space','workspace','output']),'same actual native workspace/output scope')
  native=self.old_probe('state');self.authority.input_safe(native);seat=self.old_probe('keyboard_state')
  require(self.authority.matches(native.get('nativeFocus'),tokens[active])and self.authority.matches(seat.get('keyboardOwner'),tokens[active])and seat.get('keyboardSurfacePresent')is True and seat.get('keyboardResourcePresent')is True,'actual current native core and Seat active target')
  workspace=self.actual_workspace(11,'monocle',2,tokens[active])
  confirmed={name:self.capture(actor,name)for name in tokens}
  require(self.decoder.exact(confirmed,tokens),'fresh post-read exact current members')
  return dict(captures=captures,owned=owned,native=native,seat=seat,workspace=workspace,numericReasonObserved=False,renderedOwnerVisibleProved=False)
 def conserve(self,before,after):
  require(self.decoder.exact(before['captures'],after['captures']),'exact current input-block scope conserved')
  require(all(self.decoder.exact(before['owned'][name]['body'][k],after['owned'][name]['body'][k])for name in ['owner','peer']for k in CONTEXT),'all owning/member/mode/group/context fields conserved across native block transition')
 def monocle_case(self,actor):
  case='B11';owner=self.capture(actor);self.focus(actor,owner)
  reached=self.retained_tiled(case,actor)
  tokens={name:self.capture(actor,name)for name in ['owner','peer']}
  initial=self.scope(actor,tokens,'owner')
  self.focus(actor,tokens['peer'])
  blocked=self.wait('actual source-native isolated input block',lambda:self.scope(actor,tokens,'peer'),4)
  self.conserve(initial,blocked)
  point=self.qt_point(actor,'owner',tokens['owner'])
  require(self.point_inside(point,self.qt_box(actor,'peer',tokens['peer'])),'same actual source-native owner/eligible-peer button point')
  before=self.fixture_state(actor)
  for name in ['owner','peer']:require(type(before['windows'][name]['clicks'])is int and before['windows'][name]['clicks']>=0,'typed original real member callback count')
  proc,row=self.registry.launch(case,'pointer',1);pointer=dict(proc=proc,row=row,held=False)
  try:
   self.move_pointer(pointer,point,tokens['peer'],excluded=(tokens['owner'],))
   query=self.snapshot(tokens['owner'],0)
   require(not self.authority.matches(query['hitOwner'],tokens['owner'])and self.authority.matches(query['hitOwner'],tokens['peer']),'native blocked protected owner not revived; eligible peer is actual query winner')
   prefix=self.old_probe('events');self.pointer_write(pointer,'button 272 1\n');pointer['held']=True;self.pointer_write(pointer,'button 272 0\n');pointer['held']=False
   def complete():
    rows=self.old_probe('events');require(self.decoder.exact(rows[:len(prefix)],prefix),'actual exclusion button prefix exact')
    if len(rows)==len(prefix):return None
    if len(rows)<len(prefix)+2:return None
    require(len(rows)==len(prefix)+2,'exact physical exclusion press/release')
    for r,(code,state)in zip(rows[len(prefix):],[(272,1),(272,0)],strict=True):
     require(type(r.get('button'))is int and type(r.get('buttonState'))is int and r['button']==code and r['buttonState']==state and type(r.get('native'))is dict,'typed actual exclusion buttons')
     require(not self.authority.matches(r['native'].get('hitOwner'),tokens['owner'])and self.authority.matches(r['native'].get('hitOwner'),tokens['peer']),'blocked owner not hit during real press/release')
    native=self.old_probe('state');seat=self.old_probe('keyboard_state')
    require(not self.authority.matches(native.get('nativeFocus'),tokens['owner'])and not self.authority.matches(seat.get('keyboardOwner'),tokens['owner']),'excluded owner not actual core or Seat accepted target')
    require(self.authority.matches(native.get('nativeFocus'),tokens['peer'])and self.authority.matches(seat.get('keyboardOwner'),tokens['peer'])and seat.get('keyboardSurfacePresent')is True and seat.get('keyboardResourcePresent')is True,'actual eligible independent peer core/Seat')
    state=self.fixture_state(actor);owner_count=state['windows']['owner']['clicks'];peer_count=state['windows']['peer']['clicks']
    require(type(owner_count)is int and owner_count==before['windows']['owner']['clicks'],'no excluded owner Qt callback')
    if peer_count==before['windows']['peer']['clicks']:return None
    require(type(peer_count)is int and peer_count==before['windows']['peer']['clicks']+1,'one actual eligible peer Qt callback')
    return dict(buttons=rows[len(prefix):],native=native,seat=seat,qt=state)
   actual=self.wait('actual excluded real-input closure/current core+Seat',complete,4)
   after=self.scope(actor,tokens,'peer');self.conserve(blocked,after)
  finally:self.close_pointer(pointer)
  self.focus(actor,tokens['owner'])
  cleared=self.wait('actual source-native owner input block cleared before unpin',lambda:self.scope(actor,tokens,'owner'),4)
  self.conserve(initial,cleared)
  report,unpin=self.pin_keyboard(case,actor,2)
  require(report['after']['pinned']is False and unpin['owned']['body']['acceptsInput']is True,'actual cleared current owner before genuine same-owned unpin')
  return dict(case=case,component='native-monocle-mapped-unhidden-input-nonrevival',reached=reached,initial=initial,blocked=blocked,query=query,point=point,actual=actual,after=after,cleared=cleared,unpin=report,alphaZeroDuringInactiveSourceHonest=True,numericReasonObserved=False,presentationROIAccepted=False,fullDesignCaseAccepted=False)
 def run_components(self,selection):
  require(selection in CASES,'explicit reviewed independent component selector')
  results=[]
  for case in CASES[selection]:
   workspace=11 if case=='B11'else 1
   self.setup('explicit private component workspace','hl.dsp.focus({workspace='+json.dumps(str(workspace))+'})')
   if case=='B11':self.actual_workspace(11,'monocle',0)
   self.attest('before-component-'+case);actor=self.launch_actor(case)
   try:
    result=self.monocle_case(actor)if case=='B11'else self.exclusion_case('B12',actor)
    self.attest('after-component-'+case);self.trace.append(dict(caseResult=result));self.persist();results.append(result)
   finally:self.retire_actor(actor)
  self.registry.seal_before_host_close()
  return dict(actualComponentResults=results,componentCases=list(CASES[selection]),originalTwelveCaseIncrementAccepted=False,fullCampaignBAccepted=False,original14Credit=False)
