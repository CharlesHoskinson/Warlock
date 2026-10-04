"""Join exact-publication primary model inspection to observed DOM controls.
No policy/action is computed here; title/state/phase are emitted by actual Elm.
Positions add the independently audited default native popup rectangle only.
"""
import json,re
class Collector:
 def __init__(self):self.last=None
 def read(self,text):
  inspections=[];bar={};popup={};rect=None
  for line in text.splitlines():
   if line.startswith('surface-inspection: '):inspections.append(json.loads(line.split(': ',1)[1]))
   for origin,target in [('bar',bar),('popup',popup)]:
    prefix='surface-report: origin='+origin+' '
    if line.startswith(prefix):
     body=json.loads(line[len(prefix):])['body'];target[body['publication']]=body
   match=re.search(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',line)
   if match:rect=tuple(map(int,match.groups()))
  for inspection in inspections:
   publication=inspection['publication'];body=inspection['body'];b=bar.get(publication)
   p=popup.get(publication) if body['picker'] or body.get('menu') else None
   if not b or ((body['picker'] or body.get('menu')) and (not p or not rect)):continue
   def control(identity,origin):
    view=p if origin=='popup' else b
    item=next((item for item in view['buttons'] if item['id']==identity),None)
    if item is None:return None
    x,y,w,h=item['x'],item['y'],item['width'],item['height'];dx,dy=(rect[:2] if origin=='popup' else (0,0));cw,ch=(rect[2:] if origin=='popup' else (800,48));visible=x>=0 and y>=0 and x+w<=cw and y+h<=ch and w>0 and h>0
    return {'disabled':item['disabled'],'label':item['accessibleName'],'point':[dx+x+w/2,dy+y+h/2],'rect':[dx+x,dy+y,w,h],'clip':[dx,dy,dx+cw,dy+ch],'visible':visible}
   groups=[]
   for group in body['groups']:
    observed=control(group['domId'],'bar')
    if observed is None:break
    groups.append({**group,**observed})
   if len(groups)!=len(body['groups']):continue
   picker=None
   if body['picker']:
    selections=[]
    for family in body['picker']['selections']:
     observed=control(family['domId'],'popup')
     if observed is None:break
     selections.append({**family,**observed})
    close=control(body['picker']['closeId'],'popup')
    if len(selections)!=len(body['picker']['selections']) or close is None:continue
    picker={'generation':body['picker']['generation'],'selections':selections,'close':close}
   menu=None
   if body.get('menu'):
    actions=[]
    for item in body['menu']['actions']:
     observed=control(item['domId'],'popup')
     if observed is None:break
     actions.append({**item,**observed})
    close=control(body['menu']['closeId'],'popup')
    if len(actions)!=len(body['menu']['actions']) or close is None:continue
    menu={**body['menu'],'actions':actions,'close':close}
   self.last={**body,'groups':groups,'picker':picker,'menu':menu,'focus':(p if picker or menu else b)['focus'],'reconnect':control(body['reconnectId'],'bar'),'openApplications':control(body['openerId'],'bar'),'publication':publication,'lease':inspection['lease']}
  return self.last
