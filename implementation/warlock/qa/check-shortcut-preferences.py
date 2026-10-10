"""Actual private-store, authenticated transport and strict decoder checks.

Native input/binding mutation is qualified by the separate protected journey.
"""
import copy,json,os,pathlib,sys,tempfile,stat
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from shortcut_preferences import Store,snapshot,ROUTES
from effect_endpoint import Endpoint
from endpoint import Refused
from catalog_transport import CatalogTransport
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def refuses(name,fn):
 try:fn()
 except (Refused,OSError,ValueError):checks.append(name);return
 raise AssertionError(name)
bound={'lifetime':'1','session':'1','frontend':'1'}
chords={'applications':('SUPER + ALT + SPACE','SUPER + CTRL + ALT + SPACE'),'system':('SUPER + ESCAPE','SUPER + CTRL + ESCAPE'),'notifications':('SUPER + SHIFT + ALT + comma','SUPER + CTRL + ALT + comma')}
inventory={'fingerprint':'a'*64,**{r:{'defaultChord':c[0],'alternateChord':c[1],'defaultAvailable':r!='applications','alternateAvailable':True,'active':'keep'} for r,c in chords.items()}}
class Client(Endpoint):
 def __init__(self,reply=None):self.bound=bound;self.reply=reply;self.sent=[];self.live=copy.deepcopy(inventory)
 def verify_process(self):pass
 def verify_paths(self):pass
 def request(self,wire):
  self.sent.append(copy.deepcopy(wire))
  if self.reply is not None:return copy.deepcopy(self.reply)
  apply=wire['kind']=='shortcut-bindings-apply'
  if apply:
   for route in ROUTES:self.live[route]['active']=wire['choices'][route]
  return {'protocolVersion':3,'kind':'shortcut-bindings-outcome' if apply else 'shortcut-bindings','binding':bound,'requestId':wire['requestId'],'inventory':copy.deepcopy(self.live),**({'status':'Applied'} if apply else {})}
with tempfile.TemporaryDirectory(prefix='warlock-shortcuts-') as temp:
 store=Store(temp);old=store.read();check('Unconfigured decisions stay explicit',all(v=='undecided' for v in old['choices'].values()))
 refuses('Unresolved choice cannot save',lambda:store.save(old))
 wanted={**old,'choices':{'applications':'alternate','system':'default','notifications':'keep'}}
 status,saved=store.save(wanted);check('Explicit decisions persist across fresh store',status=='Saved' and Store(temp).read()==saved)
 path=pathlib.Path(temp)/'warlock/shortcuts.json';before=path.read_bytes()
 check('Private storage modes',stat.S_IMODE(path.stat().st_mode)==0o600 and stat.S_IMODE(path.parent.stat().st_mode)==0o700)
 check('Stale CAS preserves approved choice',store.save({**wanted,'choices':dict.fromkeys(ROUTES,'keep')})==('Refused',saved) and path.read_bytes()==before)
 check('Explicit apply of unchanged choice never rewrites storage',store.save(saved)==('Saved',saved) and path.read_bytes()==before)
 for value in ['exec','/tmp/program',True,None]:
  bad=copy.deepcopy(saved);bad['choices']['applications']=value;refuses('Unknown decision '+repr(value),lambda:snapshot(bad))
 future={**saved,'schema':2};path.write_text(json.dumps(future));before=path.read_bytes();refuses('Unsupported schema preserved',store.read);check('Unsupported bytes unchanged',path.read_bytes()==before);path.write_text(json.dumps(saved));path.chmod(0o600)
 real_fsync=os.fsync
 def uncertain(fd):
  if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError('lost directory sync')
  return real_fsync(fd)
 with patch('shortcut_preferences.os.fsync',uncertain):status,observed=store.save({**saved,'choices':dict.fromkeys(ROUTES,'keep')})
 check('Post-rename failure is Unknown',status=='Unknown' and observed is None)
 check('Read reconciles file without applying binding',Store(temp).read()['choices']==dict.fromkeys(ROUTES,'keep'))
 client=Client();roots={'dataHome':temp+'/data','dataDirs':[],'cacheDir':temp+'/cache'};transport=CatalogTransport(client,roots);transport.shortcuts=Store(temp+'/transport')
 request={'protocolVersion':3,'kind':'shortcut-preferences-write','binding':bound,'requestId':'4','proposal':{'preferences':wanted,'fingerprint':'b'*64}}
 check('Stale native fingerprint refuses before storage',transport.handle(request)['status']=='Refused' and not (transport.shortcuts.path/'shortcuts.json').exists() and not any(w['kind']=='shortcut-bindings-apply' for w in client.sent))
 request['proposal']['fingerprint']='a'*64;request['proposal']['preferences']['choices']['applications']='default'
 check('Conflicting default never writes or applies',transport.handle(request)['status']=='Refused' and not (transport.shortcuts.path/'shortcuts.json').exists())
 request['proposal']['preferences']['choices']['applications']='alternate';outcome=transport.handle(request)
 check('One explicit saved decision applies exact native choices once',outcome['status']=='Saved' and len([w for w in client.sent if w['kind']=='shortcut-bindings-apply'])==1 and outcome['inventory']['applications']['active']=='alternate')
 before=len(client.sent);read=transport.handle({'protocolVersion':3,'kind':'shortcut-preferences-request','binding':bound,'requestId':'5'})
 check('Refresh is native/file read only',read['snapshot']==outcome['snapshot'] and all(w['kind']=='shortcut-bindings-request' for w in client.sent[before:]))
 wire={'protocolVersion':3,'kind':'shortcut-bindings','binding':bound,'requestId':'8','inventory':inventory}
 check('Strict native reply is admitted',Client(wire).shortcut_bindings('8')==wire)
 for name,mutate in [('wrong request',lambda r:r.update(requestId='9')),('foreign binding',lambda r:r.update(binding={**bound,'frontend':'2'})),('command field',lambda r:r['inventory']['applications'].update(command='/tmp/false')),('invented chord',lambda r:r['inventory']['applications'].update(defaultChord='SUPER + F6')),('nonboolean availability',lambda r:r['inventory']['applications'].update(defaultAvailable=1)),('claimed active conflict',lambda r:r['inventory']['applications'].update(active='default'))]:
  bad=copy.deepcopy(wire);mutate(bad);refuses(name,lambda:Client(bad).shortcut_bindings('8'))
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Actual private storage and production transport/decoder; fake native replies do not qualify binding or physical input.'}))
