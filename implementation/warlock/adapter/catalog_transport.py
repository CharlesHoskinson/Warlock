"""Catalog requests on the existing supervisor-owned, authenticated binding.

Catalog roots are selected by the native supervisor/environment, never frontend.
No application readiness or launcher activation-token qualification is implied.
"""
import json,os
from pathlib import Path
from catalog_authority import Authority,Refused as CatalogRefused
from shell_preferences import Store as SettingsStore
from motion_preferences import Store as MotionStore
from taskbar_preferences import Store
from endpoint import Refused,binding,canonical,exact

MAX_OUTPUT=1048576

class CatalogTransport:
 def __init__(self,client,roots=None):
  self.client=client;self.preferences=Store();self.settings=SettingsStore();self.motion=MotionStore()
  if roots is None:
   roots={'dataHome':os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')),'dataDirs':os.environ.get('XDG_DATA_DIRS','/usr/local/share:/usr/share').split(':'),'cacheDir':str(Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))/'elm-desktop/catalog')}
  exact(roots,['dataHome','dataDirs','cacheDir'])
  if not isinstance(roots['dataDirs'],list):raise Refused('Catalog supervisor directories')
  paths=[roots['dataHome'],roots['cacheDir'],*roots['dataDirs']]
  if any(not isinstance(p,str) or not Path(p).is_absolute() for p in paths):raise Refused('Catalog supervisor roots')
  self.authority=Authority(roots['dataHome'],roots['dataDirs'],roots['cacheDir'])
 def verify(self,request):
  if type(request.get('protocolVersion')) is not int or request['protocolVersion']!=3 or self.client.bound is None or binding(request.get('binding'))!=self.client.bound:raise Refused('Catalog binding mismatch')
  self.client.verify_process();self.client.verify_paths()
 def handle(self,request):
  kind=request.get('kind')
  if kind in {'motion-preferences-request','motion-preferences-write'}:
   write=kind=='motion-preferences-write'
   exact(request,['protocolVersion','kind','binding','requestId',*(['proposal'] if write else [])]);canonical(request['requestId']);self.verify(request)
   try:
    if write:status,snapshot=self.motion.save(request['proposal'])
    else:snapshot=self.motion.read()
   except (OSError,ValueError,Refused):
    snapshot=None
    if write:status='Refused'
   self.verify(request)
   frame={'protocolVersion':3,'kind':'motion-preferences-outcome' if write else 'motion-preferences','binding':self.client.bound,'requestId':request['requestId'],'snapshot':snapshot}
   if write:frame['status']=status
   return frame
  if kind in {'shell-settings-request','shell-settings-write'}:
   write=kind=='shell-settings-write'
   exact(request,['protocolVersion','kind','binding','requestId',*(['proposal'] if write else [])]);canonical(request['requestId']);self.verify(request)
   try:
    if write:status,snapshot=self.settings.save(request['proposal'])
    else:snapshot=self.settings.read()
   except (OSError,ValueError,Refused):
    snapshot=None
    if write:status='Refused'
   self.verify(request)
   frame={'protocolVersion':3,'kind':'shell-settings-outcome' if write else 'shell-settings','binding':self.client.bound,'requestId':request['requestId'],'snapshot':snapshot}
   if write:frame['status']=status
   return frame
  if kind=='catalog-request':
   exact(request,['protocolVersion','kind','binding','requestId']);canonical(request['requestId']);self.verify(request)
   frame={'protocolVersion':3,'kind':'application-catalog','binding':self.client.bound,'requestId':request['requestId']}
   try:frame['preferences']=self.preferences.read()
   except (OSError,ValueError):frame['preferences']=None
   try:
    frame['snapshot']=self.authority.snapshot()
    if len(json.dumps(frame,separators=(',',':'),ensure_ascii=True).encode())>MAX_OUTPUT:raise CatalogRefused('Catalog envelope capacity')
   except (OSError,ValueError,UnicodeError):
    self.authority.available=False
    frame['snapshot']=None
   self.verify(request)
   return frame
  if kind=='taskbar-pins-write':
   exact(request,['protocolVersion','kind','binding','requestId','proposal']);canonical(request['requestId']);self.verify(request)
   try:status,pins=self.preferences.save(request['proposal'])
   except (OSError,ValueError):status,pins='Refused',None
   self.verify(request)
   return {'protocolVersion':3,'kind':'taskbar-pins-outcome','binding':self.client.bound,'requestId':request['requestId'],'status':status,'preferences':pins}
  if kind=='application-launch':
   exact(request,['protocolVersion','kind','binding','intent']);self.verify(request)
   outcome=self.authority.launch(request['intent'])
   # Failure after submission retires the transport; the Elm controller must
   # preserve Unknown rather than interpret a lost receipt as refusal.
   self.verify(request)
   return {'protocolVersion':3,'kind':'application-launch-outcome','binding':self.client.bound,'outcome':outcome}
  raise Refused('Catalog request kind')
