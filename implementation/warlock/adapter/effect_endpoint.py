"""Authenticated experimental effect endpoint; canonical scene capability is false."""
import math,re
from endpoint import Endpoint as ReadOnlyEndpoint, Refused, binding, canonical, exact

class Endpoint(ReadOnlyEndpoint):
 def hello(self):
  response=self.request({'protocolVersion':3,'kind':'hello'})
  fields=['protocolVersion','kind','binding','compositor','capabilities']
  descriptor='previewFdAddress' in response
  exact(response,[*fields,'previewFdAddress'] if descriptor else fields)
  if response['kind']!='attached':raise Refused('Handshake kind')
  compositor=response['compositor'];exact(compositor,['pid','instance','coreHash'])
  if compositor['pid']!=self.pid or compositor['instance']!=self.instance or not isinstance(compositor['coreHash'],str):raise Refused('Wrong native session')
  caps=response['capabilities']
  if not isinstance(caps,dict) or any(type(caps.get(k)) is not bool for k in ['observe','effects','minimizedState','canonicalScene']) or any(type(caps.get(k)) is not int for k in ['effectProtocol','taskbarProjectionProtocol','effectInvalidationProtocol']):raise Refused('Capability types')
  if response['capabilities']!={'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}:raise Refused('Unsupported experimental capabilities')
  attached=binding(response['binding'])
  if self.bound and attached['lifetime']==self.bound['lifetime'] and attached['session']==self.bound['session'] and int(attached['frontend'])<=int(self.bound['frontend']):raise Refused('Frontend epoch did not advance')
  address=response.get('previewFdAddress')
  if descriptor and (type(address) is not str or address!='elm-preview-'+str(self.pid)+'-'+attached['lifetime']):raise Refused('Native preview descriptor address')
  self.preview_fd_address=address
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
   exact(window,['incarnation','application','label','minimized']);identity=canonical(window['incarnation'])
   if identity in seen or type(window['minimized']) is not bool or not isinstance(window['label'],str) or len(window['label'].encode('utf-16-le'))//2>256 or any(ord(c)<32 for c in window['label']):raise Refused('Window projection')
   if not isinstance(window['application'],str) or len(window['application'].encode('utf-16-le'))//2>256 or any(ord(c)<32 for c in window['application']):raise Refused('Application hint')
   seen.add(identity)
  return r
 def scene_facts(self,request_id,minimum_watermark='0',*,attention=False):
  if not self.bound:raise Refused('Handshake required')
  canonical(request_id);canonical(minimum_watermark,True)
  if type(attention) is not bool:raise Refused('Attention observation option')
  r=self.request({'protocolVersion':3,'kind':'scene-facts-request','binding':self.bound,'requestId':request_id,'minimumWatermark':minimum_watermark,**({'attentionProtocol':1} if attention else {})})
  exact(r,['protocolVersion','kind','binding','requestId','sequence','revision','outputGeneration','facts',*(['attentionProtocol'] if attention else [])])
  if attention and (type(r['attentionProtocol']) is not int or r['attentionProtocol']!=1):raise Refused('Attention protocol')
  if r['kind']!='scene-facts' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Facts correlation')
  for key in ['sequence','revision','outputGeneration']:canonical(r[key])
  if int(r['sequence'])<int(minimum_watermark):raise Refused('Obsolete facts')
  facts=r['facts'];exact(facts,['focused','windows'])
  windows=facts['windows']
  if not isinstance(windows,list) or len(windows)>256:raise Refused('Facts bound')
  bools=['workspaceVisible','hidden','pinned','allowedOverFullscreen','renderOverFullscreen','acceptsInput','shouldRenderAny','shouldRenderOwnMonitor','minimized']+(['attention'] if attention else [])
  seen=set();positions=set()
  for window in windows:
   exact(window,['incarnation','owner','application','stackPosition','workspace','monitor','geometry','fullscreenMode',*bools])
   identity=canonical(window['incarnation'])
   if not isinstance(window['application'],str) or len(window['application'].encode('utf-16-le'))//2>256 or any(ord(c)<32 for c in window['application']):raise Refused('Application hint')
   if identity in seen:raise Refused('Duplicate incarnation')
   seen.add(identity)
   if window['owner'] is not None:canonical(window['owner'])
   if any(type(window[key]) is not bool for key in bools):raise Refused('Facts state')
   position=window['stackPosition']
   if type(position) is not int or position<0 or position in positions:raise Refused('Stack position')
   positions.add(position)
   if not isinstance(window['geometry'],list) or len(window['geometry'])!=4 or any(type(v) not in (float,int) for v in window['geometry']):raise Refused('Geometry')
   workspace=window['workspace']
   if workspace is not None and (not isinstance(workspace,str) or not re.fullmatch(r'(?:0|-?[1-9][0-9]{0,18})',workspace) or not -(1<<63)<=int(workspace)<(1<<63)):raise Refused('Workspace identity')
   if window['monitor'] is not None:canonical(window['monitor'],True)
   if any(not math.isfinite(v) for v in window['geometry']):raise Refused('Nonfinite geometry')
   if type(window['fullscreenMode']) is not int:raise Refused('Fullscreen mode')
  if facts['focused'] is not None and canonical(facts['focused']) not in seen:raise Refused('Unknown focus')
  if any(w['owner'] is not None and w['owner'] not in seen for w in windows):raise Refused('Unknown owner')
  return r
 def activation_history(self,request_id):
  if not self.bound:raise Refused('Handshake required')
  canonical(request_id)
  r=self.request({'protocolVersion':3,'kind':'activation-history-request','binding':self.bound,'requestId':request_id,'minimumWatermark':'0'})
  exact(r,['protocolVersion','kind','binding','requestId','context','roots'])
  if type(r['protocolVersion']) is not int or r['protocolVersion']!=3 or r['kind']!='activation-history' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('History scope')
  exact(r['context'],['lifetime','epoch','output','revision'])
  for value in r['context'].values():canonical(value)
  if r['context']['lifetime']!=self.bound['lifetime'] or r['context']['epoch']!=self.bound['frontend']:raise Refused('History authority')
  if not isinstance(r['roots'],list) or len(r['roots'])>256 or len(set(canonical(value) for value in r['roots']))!=len(r['roots']):raise Refused('History bound/identity')
  return r
 def motion_profile(self,request_id,profile):
  if not self.bound or profile not in ('reduced','full'):raise Refused('Motion profile scope')
  canonical(request_id)
  r=self.request({'protocolVersion':3,'kind':'motion-profile-set','binding':self.bound,'requestId':request_id,'profile':profile})
  exact(r,['protocolVersion','kind','binding','requestId','profile'])
  if type(r['protocolVersion']) is not int or r['protocolVersion']!=3 or r['kind']!='motion-profile' or binding(r['binding'])!=self.bound or r['requestId']!=request_id or r['profile']!=profile:raise Refused('Motion profile correlation')
  return r
 def pointer_ownership(self,request_id):
  canonical(request_id)
  r=self.request({'protocolVersion':3,'kind':'pointer-ownership-request','binding':self.bound,'requestId':request_id})
  exact(r,['protocolVersion','kind','ownershipProtocol','binding','requestId','serial','state','owner'])
  if type(r['protocolVersion']) is not int or r['protocolVersion']!=3 or r['kind']!='pointer-ownership' or type(r['ownershipProtocol']) is not int or r['ownershipProtocol']!=1 or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Pointer ownership correlation/protocol')
  canonical(r['serial'])
  if r['state'] not in ['idle','move','resize']:raise Refused('Pointer ownership state')
  if r['state']=='idle':
   if r['owner'] is not None:raise Refused('Idle pointer owner')
  elif r['owner'] is not None:canonical(r['owner'])
  # A grouped/retiring target may have no mapped root identity. Active state
  # still blocks shell input; null never turns a native grab into idle.
  return r
 def shortcut_bindings(self,request_id,choices=None,fingerprint=None):
  from shortcut_preferences import ROUTES,choices as valid_choices,fingerprint as valid_fingerprint
  canonical(request_id)
  apply=choices is not None
  payload={'protocolVersion':3,'kind':'shortcut-bindings-apply' if apply else 'shortcut-bindings-request','binding':self.bound,'requestId':request_id}
  if apply:
   valid_choices(choices);valid_fingerprint(fingerprint)
   if 'undecided' in choices.values():raise Refused('Unresolved shortcut choices')
   payload.update(choices=choices,fingerprint=fingerprint)
  r=self.request(payload)
  exact(r,['protocolVersion','kind','binding','requestId','inventory',*(['status'] if apply else [])])
  if type(r['protocolVersion']) is not int or r['protocolVersion']!=3 or r['kind']!=('shortcut-bindings-outcome' if apply else 'shortcut-bindings') or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Shortcut binding correlation')
  if apply and r['status'] not in ('Applied','Refused','Unknown'):raise Refused('Shortcut binding outcome')
  inventory=r['inventory'];exact(inventory,['fingerprint',*ROUTES]);valid_fingerprint(inventory['fingerprint'])
  chords={'applications':('SUPER + ALT + SPACE','SUPER + CTRL + ALT + SPACE'),'system':('SUPER + ESCAPE','SUPER + CTRL + ESCAPE'),'notifications':('SUPER + SHIFT + ALT + comma','SUPER + CTRL + ALT + comma')}
  for route in ROUTES:
   row=inventory[route];exact(row,['defaultChord','alternateChord','defaultAvailable','alternateAvailable','active'])
   if (row['defaultChord'],row['alternateChord'])!=chords[route] or type(row['defaultAvailable']) is not bool or type(row['alternateAvailable']) is not bool or row['active'] not in ('keep','default','alternate'):raise Refused('Shortcut binding inventory')
   if row['active']=='default' and not row['defaultAvailable'] or row['active']=='alternate' and not row['alternateAvailable']:raise Refused('Shortcut active conflict')
  return r
 def shell_shortcuts(self,request_id):
  canonical(request_id)
  r=self.request({'protocolVersion':3,'kind':'shell-shortcuts-request','binding':self.bound,'requestId':request_id})
  exact(r,['protocolVersion','kind','shortcutProtocol','binding','requestId','serial','blocked','events'])
  if r['protocolVersion']!=3 or r['kind']!='shell-shortcuts' or type(r['shortcutProtocol']) is not int or r['shortcutProtocol']!=3 or binding(r['binding'])!=self.bound or r['requestId']!=request_id or type(r['blocked']) is not bool:raise Refused('Shortcut correlation/protocol')
  high=int(canonical(r['serial'],True));rows=r['events']
  if not isinstance(rows,list) or len(rows)>64:raise Refused('Shortcut capacity')
  previous=None
  for row in rows:
   exact(row,['serial','route','output','outputGeneration']);serial=int(canonical(row['serial']));canonical(row['outputGeneration'])
   box=row['output']
   if box is not None and (not isinstance(box,list) or len(box)!=4 or any(type(v) is not int or v<-(2**31) or v>=2**31 for v in box) or box[2]<=0 or box[3]<=0):raise Refused('Shortcut output bounds')
   if row['route'] not in ['applications','system','notifications'] or (previous is not None and serial!=previous+1):raise Refused('Shortcut route/order')
   previous=serial
  if previous is not None and previous!=high:raise Refused('Shortcut watermark')
  return r
 def switcher_journal(self,request_id,observe=False):
  canonical(request_id)
  kind='switcher-journal-observe-request' if observe else 'switcher-journal-request'
  r=self.request({'protocolVersion':3,'kind':kind,'binding':self.bound,'requestId':request_id})
  return self.check_switcher_journal(r,request_id)
 def check_switcher_journal(self,r,request_id):
  exact(r,['protocolVersion','kind','binding','requestId','chord'])
  if r['kind']!='switcher-journal' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Chord correlation')
  c=r['chord'];exact(c,['generation','roots','history','origin','steps','released','cancelled','consumed']);canonical(c['generation'],True)
  for field in ['roots','history']:
   rows=c[field]
   if not isinstance(rows,list) or len(rows)>256 or len(set(canonical(value) for value in rows))!=len(rows):raise Refused('Chord membership')
  if any(value not in c['roots'] for value in c['history']):raise Refused('Chord history membership')
  if c['origin'] is not None:canonical(c['origin'])
  if not isinstance(c['steps'],list) or len(c['steps'])>4096 or any(type(v) is not int or v not in [-1,1] for v in c['steps']):raise Refused('Chord ordinal/direction')
  if any(type(c[v]) is not bool for v in ['released','cancelled','consumed']):raise Refused('Chord phase')
  if (c['generation']=='0')!=(len(c['steps'])==0):raise Refused('Chord generation/entry')
  return r
 def switcher_cancel(self,request_id,chord):
  canonical(request_id);canonical(chord)
  r=self.request({'protocolVersion':3,'kind':'switcher-cancel-request','binding':self.bound,'requestId':request_id,'chord':chord})
  return self.check_switcher_journal(r,request_id)
 def switcher_selection(self,request_id,chord,root):
  canonical(request_id);canonical(chord);canonical(root)
  r=self.request({'protocolVersion':3,'kind':'switcher-selection-request','binding':self.bound,'requestId':request_id,'chord':chord,'root':root})
  exact(r,['protocolVersion','kind','binding','requestId'])
  if r['kind']!='switcher-selection' or binding(r['binding'])!=self.bound or r['requestId']!=request_id:raise Refused('Chord selection correlation')
  return r
 def context(self,facts):
  if binding(facts['binding'])!=self.bound:raise Refused('Context binding')
  return {'lifetime':self.bound['lifetime'],'epoch':self.bound['frontend'],'output':facts['outputGeneration'],'revision':facts['revision']}
 def effect(self,intent):
  if not self.bound:raise Refused('Handshake required')
  exact(intent,['request','generation','incarnation','operation','context']);exact(intent['context'],['lifetime','epoch','output','revision'])
  for key in ['request','generation','incarnation']:canonical(intent[key])
  for value in intent['context'].values():canonical(value)
  if intent['operation'] not in ['minimize','restore','activate']:raise Refused('Unsupported effect')
  r=self.request({'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':self.bound,'intent':intent})
  exact(r,['protocolVersion','kind','effectProtocol','binding','intent','status','reason','revision','outputGeneration'])
  if r['kind']!='effect-outcome' or r['effectProtocol']!=1 or type(r['effectProtocol']) is not int or binding(r['binding'])!=self.bound or r['intent']!=intent or r['status'] not in ['Committed','Refused','Unknown']:raise Refused('Effect outcome correlation')
  for key in ['revision','outputGeneration']:canonical(r[key])
  return r
