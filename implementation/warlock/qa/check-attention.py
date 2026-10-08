"""Changed native schema/coherent join checks. Physical native evidence is separate."""
import copy,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from effect_endpoint import Endpoint
from taskbar_projection import coherent_scene
from endpoint import Refused
bound={'lifetime':'1','session':'1','frontend':'1'}
window={'incarnation':'1','owner':None,'application':'Editor','stackPosition':0,'workspace':'1','monitor':'0','geometry':[0,0,300,200],'fullscreenMode':0,**{key:False for key in ['hidden','pinned','allowedOverFullscreen','renderOverFullscreen','minimized']},**{key:True for key in ['workspaceVisible','acceptsInput','shouldRenderAny','shouldRenderOwnMonitor']},'attention':True}
reply={'protocolVersion':3,'kind':'scene-facts','binding':bound,'requestId':'1','sequence':'1','revision':'1','outputGeneration':'1','attentionProtocol':1,'facts':{'focused':None,'windows':[window]}}
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
class Client(Endpoint):
 def __init__(self,value):self.bound=bound;self.value=value;self.submitted=None
 def request(self,value):self.submitted=value;return copy.deepcopy(self.value)
client=Client(reply);before=client.scene_facts('1',attention=True)
check('Attention read explicitly negotiates version one',client.submitted['attentionProtocol']==1 and before['facts']['windows'][0]['attention'])
snapshot={'windows':[{'incarnation':'1','application':'Editor','label':'Editor document','minimized':False}]}
check('Attention joins its exact incarnation',coherent_scene(before,snapshot,before)['windows'][0]['attention'])
changed=copy.deepcopy(before);changed['facts']['windows'][0]['attention']=False
check('Contradictory same revision facts are unavailable',coherent_scene(before,snapshot,changed) is None)
changed['revision']='2';check('Cross revision attention never joins',coherent_scene(before,snapshot,changed) is None)
changed=copy.deepcopy(before);changed['facts']['windows'][0]['incarnation']='2';check('Foreign incarnation never borrows attention',coherent_scene(before,snapshot,changed) is None)
legacy=copy.deepcopy(reply);legacy.pop('attentionProtocol');legacy['facts']['windows'][0].pop('attention');client=Client(legacy);old=client.scene_facts('1')
check('Original native read shape remains supported','attentionProtocol' not in client.submitted and 'attention' not in coherent_scene(old,snapshot,old)['windows'][0])
for name,transform in [('Downgrade refused',lambda value:value.pop('attentionProtocol')),('Boolean version refused',lambda value:value.update(attentionProtocol=True)),('Nonboolean native attention refused',lambda value:value['facts']['windows'][0].update(attention=1)),('Missing attention refused',lambda value:value['facts']['windows'][0].pop('attention')),('Unknown window fields refused',lambda value:value['facts']['windows'][0].update(exec='/usr/bin/false'))]:
 value=copy.deepcopy(reply);transform(value)
 try:Client(value).scene_facts('1',attention=True);raise AssertionError(name)
 except Refused:checks.append(name)
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Changed strict native observation decoder and production coherent scene join; physical native urgency/pixels separate.'}))
