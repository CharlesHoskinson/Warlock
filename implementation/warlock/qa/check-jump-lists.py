"""Real private GIO actions/XBEL with exact application identity and argv proof."""
import json,os,pathlib,sys,tempfile,time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from catalog_authority import Authority
from jump_list import Lists,Refused
import gi;gi.require_version('GLib','2.0');gi.require_version('GioUnix','2.0');from gi.repository import GLib,GioUnix
checks=[]
def check(name,value):assert value,name;checks.append(name)
def wait(fn):
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  result=fn()
  if result:return result
  time.sleep(.01)
 raise AssertionError('Original GIO fixture observation deadline')
class Client:
 bound={'lifetime':'1','session':'1','frontend':'1'}
 def verify_process(self):pass
 def verify_paths(self):pass
serial=10
def request(intent=None,entry='warlock-editor'):
 global serial
 serial+=1
 return {'protocolVersion':3,'kind':'jump-list-effect' if intent else 'jump-list-request','binding':Client.bound,'requestId':str(serial),**({'intent':intent} if intent else {'entry':entry})}
def proposal(snapshot,action):return {k:snapshot[k] for k in ['service','revision','entry']}|{'action':action}
original=os.environ.copy()
with tempfile.TemporaryDirectory(prefix='warlock-jump-list-') as temporary:
 root=pathlib.Path(temporary);data=root/'data';apps=data/'applications';apps.mkdir(parents=True);empty=root/'empty';empty.mkdir();events=root/'events.jsonl'
 recorder=root/'record.py';recorder.write_text('import json,os,sys\nwith open(sys.argv[1],"a") as stream:stream.write(json.dumps({"argv":sys.argv[2:],"pid":os.getpid()})+"\\n")\n')
 entry=apps/'warlock-editor.desktop'
 entry.write_text('[Desktop Entry]\nType=Application\nName=Warlock Editor\nExec=/usr/bin/python3 '+str(recorder)+' '+str(events)+' RECENT %u\nActions=Alpha;Beta;\n[Desktop Action Alpha]\nName=New document\nExec=/usr/bin/python3 '+str(recorder)+' '+str(events)+' ALPHA\n[Desktop Action Beta]\nName=Private window\nExec=/usr/bin/python3 '+str(recorder)+' '+str(events)+' BETA\n[Desktop Action Foreign]\nName=Unsupported action\nExec=/usr/bin/false\n')
 document=root/'Document $(touch forbidden).txt';document.write_text('Private fixture document');foreign=root/'foreign.txt';foreign.write_text('Foreign application document')
 bookmarks=GLib.BookmarkFile.new()
 for file,owner,title in [(document,'warlock-editor.desktop','Warlock recent document'),(foreign,'foreign.desktop','Foreign recent document')]:
  uri=file.as_uri();bookmarks.set_title(uri,title);bookmarks.set_mime_type(uri,'text/plain');bookmarks.set_application_info(uri,owner,'/usr/bin/false %u',1,GLib.DateTime.new_now_utc())
 bookmarks.to_file(str(data/'recently-used.xbel'))
 env={'HOME':str(root),'XDG_DATA_HOME':str(data),'XDG_DATA_DIRS':str(empty),'XDG_CACHE_HOME':str(root/'cache'),'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(root/'absent'),'DBUS_SYSTEM_BUS_ADDRESS':'unix:path='+str(root/'absent')};os.environ.update(env)
 def observed():return [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
 try:
  authority=Authority(str(data),[str(empty)],str(root/'catalog-cache'))
  with Lists(authority) as lists:
   snapshot=lists.read(request(),Client())['snapshot'];ids=[a['id'] for a in snapshot['actions']];print(json.dumps(snapshot),file=sys.stderr)
   check('Exactly two catalog-declared actions are published',ids[:2]==['desktop:Alpha','desktop:Beta'] and 'desktop:Foreign' not in ids)
   check('Only application-bound supported recent file is published',len(ids)==3 and snapshot['actions'][2]['label']=='Open Warlock recent document')
   check('Native paths, Exec and URI are not frontend capabilities',not any(k in json.dumps(snapshot) for k in [str(root),'exec','uri']))
   alpha=proposal(snapshot,'desktop:Alpha');submitted=lists.effect(request(alpha),Client());wait(lambda:len(observed())==1)
   check('Real GIO invokes declared action once',submitted['status']=='Submitted' and observed()[0]['argv']==['ALPHA'])
   duplicate=lists.effect(request(alpha),Client());check('Old action generation cannot resubmit',duplicate['status']=='Refused' and len(observed())==1)
   recent=next(a['id'] for a in submitted['snapshot']['actions'] if a['kind']=='recent');opened=lists.effect(request(proposal(submitted['snapshot'],recent)),Client());wait(lambda:len(observed())==2);print(json.dumps({'recentOutcome':opened['status'],'event':observed()[1]}),file=sys.stderr)
   check('Recent file uses real GIO and exact data argv',opened['status']=='Submitted' and observed()[1]['argv'] in [['RECENT',document.as_uri()],['RECENT',str(document)]] and not (root/'forbidden').exists())
   foreign_key='recent:'+__import__('hashlib').sha256(('foreign.desktop\0'+foreign.as_uri()).encode()).hexdigest()
   refused=lists.effect(request(proposal(opened['snapshot'],foreign_key)),Client());check('Foreign recent identity never dispatches',refused['status']=='Refused' and len(observed())==2)
   bad=request(proposal(refused['snapshot'],'desktop:Alpha'));bad['intent']['exec']='/usr/bin/true'
   try:lists.effect(bad,Client());raise AssertionError('Frontend command accepted')
   except Refused:checks.append('Frontend command injection is strictly rejected')
   old=proposal(refused['snapshot'],'desktop:Beta');entry.write_text(entry.read_text().replace('Private window','Private window changed'))
   stale=lists.effect(request(old),Client());check('Catalog action changes withdraw old proposals',stale['status']=='Refused' and len(observed())==2)
   refreshed=lists.read(request(),Client())['snapshot'];old=proposal(refreshed,recent);document.write_text('Modified native document')
   changed=lists.effect(request(old),Client());check('Changed recent file cannot receive stale dispatch',changed['status']=='Refused' and len(observed())==2)
   fresh=lists.read(request(),Client())['snapshot'];original_action=GioUnix.DesktopAppInfo.launch_action
   def lost(app,action,context):original_action(app,action,context);raise RuntimeError('Lost native return after submission')
   beta=proposal(fresh,'desktop:Beta')
   with patch.object(GioUnix.DesktopAppInfo,'launch_action',lost):unknown=lists.effect(request(beta),Client())
   wait(lambda:len(observed())==3);check('Lost result is Unknown after actual GIO submission',unknown['status']=='Unknown' and observed()[2]['argv']==['BETA'])
   retry=lists.effect(request(beta),Client());check('Unknown native action is never replayed',retry['status']=='Refused' and len(observed())==3)
   (data/'recently-used.xbel').write_text('Malformed XBEL')
   malformed=lists.read(request(),Client())['snapshot'];check('Malformed recent source withdraws recent actions and preserves declared actions',len(malformed['actions'])==2 and malformed['reason']=='Recent items unavailable.')
  print(json.dumps({'passed':True,'checks':checks,'actualGioEvents':observed(),'nativeAcceptance':False,'scope':'Private real GIO/XBEL and argv observations; GUI/AT acceptance separate.'}))
 finally:os.environ.clear();os.environ.update(original)
