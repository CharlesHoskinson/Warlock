"""Production ownership decoder: schema, correlation and release ownership."""
import copy,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'adapter'))
from effect_endpoint import Endpoint,Refused
bound={'lifetime':'1','session':'2','frontend':'3'}
class Client(Endpoint):
 def __init__(self,value):self.bound=bound;self.value=value
 def request(self,packet):
  assert packet=={'protocolVersion':3,'kind':'pointer-ownership-request','binding':bound,'requestId':'1'}
  return self.value
base={'protocolVersion':3,'kind':'pointer-ownership','ownershipProtocol':1,'binding':bound,'requestId':'1','serial':'2','state':'move','owner':'9'}
checks=[]
for state,owner in [('move','9'),('resize','9'),('move',None),('idle',None)]:
 row={**base,'state':state,'owner':owner};assert Client(row).pointer_ownership('1')==row;checks.append(state+str(owner))
for name,patch in [('foreign',{'binding':{**bound,'frontend':'4'}}),('wrong-request',{'requestId':'2'}),('extra',{'extra':0}),('mode',{'state':'drag'}),('idle-owner',{'state':'idle'}),('zero-serial',{'serial':'0'}),('leading-zero',{'serial':'02'}),('owner-zero',{'owner':'0'}),('owner-number',{'owner':9}),('protocol-bool',{'ownershipProtocol':True}),('version-bool',{'protocolVersion':True})]:
 try:Client({**copy.deepcopy(base),**patch}).pointer_ownership('1');raise AssertionError(name)
 except Refused:checks.append(name)
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False}))
