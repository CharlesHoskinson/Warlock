"""Strict admission of native shortcut journals; physical keyboard evidence is separate."""
import copy,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from effect_endpoint import Endpoint
from endpoint import Refused
bound={'lifetime':'1','session':'1','frontend':'1'}
reply={'protocolVersion':3,'kind':'shell-shortcuts','shortcutProtocol':1,'binding':bound,'requestId':'1','serial':'3','blocked':False,'events':[{'serial':str(i+1),'route':route} for i,route in enumerate(['applications','system','notifications'])]}
checks=[]
class Client(Endpoint):
 def __init__(self,value):self.bound=bound;self.value=value;self.submitted=None
 def request(self,value):self.submitted=value;return copy.deepcopy(self.value)
client=Client(reply);value=client.shell_shortcuts('1')
assert value==reply and client.submitted=={'protocolVersion':3,'kind':'shell-shortcuts-request','binding':bound,'requestId':'1'};checks.append('Read-only request carries exact native binding')
empty=copy.deepcopy(reply);empty.update(serial='0',events=[]);assert Client(empty).shell_shortcuts('1')==empty;checks.append('Initial empty journal establishes baseline')
for name,change in [
 ('Boolean protocol refused',lambda r:r.update(shortcutProtocol=True)),
 ('Foreign binding refused',lambda r:r['binding'].update(frontend='2')),
 ('Wrong request refused',lambda r:r.update(requestId='2')),
 ('Unknown route refused',lambda r:r['events'][0].update(route='exec')),
 ('Command field refused',lambda r:r['events'][0].update(exec='/usr/bin/false')),
 ('Noncanonical serial refused',lambda r:r['events'][0].update(serial='01')),
 ('Nonboolean blocked refused',lambda r:r.update(blocked=1)),
 ('Watermark mismatch refused',lambda r:r.update(serial='9')),
 ('Journal hole refused',lambda r:r['events'][1].update(serial='9')),
 ('Duplicate ordinal refused',lambda r:r['events'][1].update(serial='1')),
 ('Oversized journal refused',lambda r:r.update(serial='65',events=[{'serial':str(i+1),'route':'system'} for i in range(65)]))]:
 bad=copy.deepcopy(reply);change(bad)
 try:Client(bad).shell_shortcuts('1');raise AssertionError(name)
 except Refused:checks.append(name)
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Production strict native decoder; no physical keyboard or GUI claim.'}))
