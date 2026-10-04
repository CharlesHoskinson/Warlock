import copy,hashlib,importlib.util,json,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-join-decoder-v322';OUT=ROOT/('witness-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
for rel in ['join.py','qa/test.py']:
 p=OUT/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,p);p.chmod(0o444)
p=OUT/'inputs/join.py';spec=importlib.util.spec_from_file_location('join',p);m=importlib.util.module_from_spec(spec);sys.modules['join']=m;spec.loader.exec_module(m)
def s(i):return {'id':i,'pid':456,'uid':1000,'connection':1}
b={'schema':1,'pid':123,'sequence':'1','complete':True,'surfaceCount':2,'surfaceClientCount':1,'grabPresent':True,'grabKeyboard':True,'grabPointer':True,'xdgGrab':True,'sessionLocked':False,'exclusiveLayerPresent':False,'layoutDragPresent':False,'heldButtons':False,'members':[{'surface':s(12),'mapped':True},{'surface':s(11),'mapped':True}],'popups':[{'surface':s(12),'parent':None,'root':s(11),'layerRoot':True,'owner':True,'mapped':True,'rootAccepted':True}]}
r={'passed':False,'nativeAcceptance':False,'scope':'Actual captured322 decoder/matcher structural parent characterization; no native input or grant','inputs':{str(x.relative_to(OUT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in (OUT/'inputs').rglob('*') if x.is_file()},'cases':[]}
try:
 for name,o in [('valid-layer',copy.deepcopy(b)),('self-parent',copy.deepcopy(b)),('cycle',copy.deepcopy(b)),('valid-nested',copy.deepcopy(b))]:
  if name=='self-parent':o['popups'][0]['parent']=s(12)
  if name in ['cycle','valid-nested']:
   o['surfaceCount']=3;o['members'].append({'surface':s(13),'mapped':True});child=copy.deepcopy(o['popups'][0]);child.update(surface=s(13),parent=s(12),owner=False);o['popups'].append(child)
   if name=='cycle':o['popups'][0]['parent']=s(13)
  raw=json.dumps(o).encode();(OUT/(name+'.json')).write_bytes(raw);snapshot=m.parse(raw,core_pid=123);result=m.match_layer_popup(snapshot,host_pid=456,host_uid=1000,popup_id=12,root_id=11);assert result['authenticated'] is False and result['ownBlockerGrantQualified'] is False
  r['cases'].append({'name':name,'accepted':True,'result':result,'structurallyInvalid':name in ['self-parent','cycle']})
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS unsafe structural acceptance preserved' if r['passed'] else r['error'])
if not r['passed']:raise SystemExit(1)
