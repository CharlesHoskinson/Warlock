"""Authenticated experimental effect endpoint; canonical scene capability is false."""
from endpoint import Endpoint as ReadOnlyEndpoint, Refused, binding, canonical, exact

class Endpoint(ReadOnlyEndpoint):
 def hello(self):
  response=self.request({'protocolVersion':3,'kind':'hello'})
  exact(response,['protocolVersion','kind','binding','compositor','capabilities'])
  if response['kind']!='attached':raise Refused('Handshake kind')
  compositor=response['compositor'];exact(compositor,['pid','instance','coreHash'])
  if compositor['pid']!=self.pid or compositor['instance']!=self.instance or not isinstance(compositor['coreHash'],str):raise Refused('Wrong native session')
  if response['capabilities']!={'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore'],'canonicalScene':False}:raise Refused('Unsupported experimental capabilities')
  attached=binding(response['binding'])
  if self.bound and attached['lifetime']==self.bound['lifetime'] and attached['session']==self.bound['session'] and int(attached['frontend'])<=int(self.bound['frontend']):raise Refused('Frontend epoch did not advance')
  self.bound=attached;return response
 def snapshot(self,request_id,minimum_watermark='0'):
  if not self.bound:raise Refused('Handshake required')
  canonical(request_id);canonical(minimum_watermark,True)
  r=self.request({'protocolVersion':3,'kind':'snapshot-request','binding':self.bound,'requestId':request_id,'minimumWatermark':minimum_watermark})
  exact(r,['protocolVersion','kind','binding','requestId','sequence','revision','windows'])
  if r['kind']!='snapshot' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Snapshot correlation')
  canonical(r['sequence']);canonical(r['revision'],True)
  if int(r['sequence'])<int(minimum_watermark):raise Refused('Obsolete snapshot')
  if not isinstance(r['windows'],list) or len(r['windows'])>256:raise Refused('Window bound')
  seen=set()
  for window in r['windows']:
   exact(window,['incarnation','label','minimized']);identity=canonical(window['incarnation'])
   if identity in seen or type(window['minimized']) is not bool or not isinstance(window['label'],str) or len(window['label'].encode('utf-16-le'))//2>256 or any(ord(c)<32 for c in window['label']):raise Refused('Window projection')
   seen.add(identity)
  return r
 def scene_facts(self,request_id,minimum_watermark='0'):
  if not self.bound:raise Refused('Handshake required')
  canonical(request_id);canonical(minimum_watermark,True)
  r=self.request({'protocolVersion':3,'kind':'scene-facts-request','binding':self.bound,'requestId':request_id,'minimumWatermark':minimum_watermark})
  exact(r,['protocolVersion','kind','binding','requestId','sequence','revision','outputGeneration','facts'])
  if r['kind']!='scene-facts' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Facts correlation')
  for key in ['sequence','revision','outputGeneration']:canonical(r[key])
  if int(r['sequence'])<int(minimum_watermark):raise Refused('Obsolete facts')
  facts=r['facts'];exact(facts,['focused','windows'])
  windows=facts['windows']
  if not isinstance(windows,list) or len(windows)>256:raise Refused('Facts bound')
  bools=['workspaceVisible','hidden','pinned','allowedOverFullscreen','renderOverFullscreen','acceptsInput','shouldRenderAny','shouldRenderOwnMonitor','minimized']
  seen=set();positions=set()
  for window in windows:
   exact(window,['incarnation','owner','stackPosition','workspace','monitor','geometry','fullscreenMode',*bools])
   identity=canonical(window['incarnation'])
   if identity in seen:raise Refused('Duplicate incarnation')
   seen.add(identity)
   if window['owner'] is not None:canonical(window['owner'])
   if any(type(window[key]) is not bool for key in bools):raise Refused('Facts state')
   position=window['stackPosition']
   if type(position) is not int or position<0 or position in positions:raise Refused('Stack position')
   positions.add(position)
   if not isinstance(window['geometry'],list) or len(window['geometry'])!=4 or any(type(v) not in (float,int) for v in window['geometry']):raise Refused('Geometry')
   if type(window['fullscreenMode']) is not int:raise Refused('Fullscreen mode')
  if facts['focused'] is not None and canonical(facts['focused']) not in seen:raise Refused('Unknown focus')
  if any(w['owner'] is not None and w['owner'] not in seen for w in windows):raise Refused('Unknown owner')
  return r
 def context(self,facts):
  if binding(facts['binding'])!=self.bound:raise Refused('Context binding')
  return {'lifetime':self.bound['lifetime'],'epoch':self.bound['frontend'],'output':facts['outputGeneration'],'revision':facts['revision']}
 def effect(self,intent):
  if not self.bound:raise Refused('Handshake required')
  exact(intent,['request','generation','incarnation','operation','context']);exact(intent['context'],['lifetime','epoch','output','revision'])
  for key in ['request','generation','incarnation']:canonical(intent[key])
  for value in intent['context'].values():canonical(value)
  if intent['operation'] not in ['minimize','restore']:raise Refused('Unsupported effect')
  r=self.request({'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':self.bound,'intent':intent})
  exact(r,['protocolVersion','kind','effectProtocol','binding','intent','status','reason','revision','outputGeneration'])
  if r['kind']!='effect-outcome' or r['effectProtocol']!=1 or type(r['effectProtocol']) is not int or binding(r['binding'])!=self.bound or r['intent']!=intent or r['status'] not in ['Committed','Refused','Unknown']:raise Refused('Effect outcome correlation')
  for key in ['revision','outputGeneration']:canonical(r[key])
  return r
