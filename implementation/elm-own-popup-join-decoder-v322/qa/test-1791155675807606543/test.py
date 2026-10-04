import copy,hashlib,importlib.util,json,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def exercise(path):
    spec=importlib.util.spec_from_file_location('join',path);m=importlib.util.module_from_spec(spec);sys.modules['join']=m;spec.loader.exec_module(m)
    def s(i,pid=456,connection=1):return {'id':i,'pid':pid,'uid':1000,'connection':connection}
    base={'schema':1,'pid':123,'sequence':'1','complete':True,'surfaceCount':2,'surfaceClientCount':1,
        'grabPresent':True,'grabKeyboard':True,'grabPointer':True,'xdgGrab':True,'sessionLocked':False,'exclusiveLayerPresent':False,'layoutDragPresent':False,'heldButtons':False,
        'members':[{'surface':s(12),'mapped':True},{'surface':s(11),'mapped':True}],
        'popups':[{'surface':s(12),'parent':None,'root':s(11),'layerRoot':True,'owner':True,'mapped':True,'rootAccepted':True}]}
    checks=[]
    def parsed(o):return m.parse(json.dumps(o).encode(),core_pid=123)
    def matched(o):return m.match_layer_popup(parsed(o),host_pid=456,host_uid=1000,popup_id=12,root_id=11)
    def reject(name,f):
        try:f()
        except m.Refused:checks.append(name);return
        raise AssertionError('unsafe acceptance: '+name)
    out=matched(base);assert out['authenticated'] is False and out['ownBlockerGrantQualified'] is False;checks.append('layer diagnostic positive never grant')
    empty=copy.deepcopy(base);empty.update(surfaceCount=0,surfaceClientCount=0,grabPresent=False,grabKeyboard=False,grabPointer=False,xdgGrab=False,members=[],popups=[])
    parsed(empty);checks.append('empty native snapshot');reject('empty no own match',lambda:matched(empty))
    for key,value in [('schema',True),('pid',999),('complete',False),('sequence','01'),('sequence',1),('sequence','18446744073709551616'),('surfaceCount',4097),('surfaceClientCount',3),('grabPresent',False),('xdgGrab',False),('grabKeyboard',1)]:
        o=copy.deepcopy(base);o[key]=value;reject('schema '+key+' '+str(value),lambda o=o:parsed(o))
    for key in ['sessionLocked','exclusiveLayerPresent','layoutDragPresent','heldButtons']:
        o=copy.deepcopy(base);o[key]=True;reject('blocked '+key,lambda o=o:matched(o))
    for key in ['grabKeyboard','grabPointer']:
        o=copy.deepcopy(base);o[key]=False;reject('missing '+key,lambda o=o:matched(o))
    for key in ['surface','root']:
        o=copy.deepcopy(base);o['popups'][0][key]['pid']=457;reject('changed credential '+key,lambda o=o:parsed(o))
    o=copy.deepcopy(base);o['members'].append(copy.deepcopy(o['members'][0]));o['surfaceCount']=3;reject('duplicate member',lambda:parsed(o))
    o=copy.deepcopy(base);o['popups'].append(copy.deepcopy(o['popups'][0]));reject('duplicate popup',lambda:parsed(o))
    o=copy.deepcopy(base);o['popups'][0]['owner']=False;reject('missing owner',lambda:parsed(o))
    o=copy.deepcopy(base);o['popups'][0]['mapped']=False;reject('unmapped popup',lambda:parsed(o))
    o=copy.deepcopy(base);o['popups'][0]['rootAccepted']=False;reject('root membership disagreement',lambda:parsed(o))
    o=copy.deepcopy(base);o['surfaceCount']=3;o['members'].append({'surface':s(13),'mapped':True});reject('extra samehost surface',lambda:matched(o))
    o=copy.deepcopy(base);o['members'][1]['mapped']=False;reject('unmapped member',lambda:matched(o))
    o=copy.deepcopy(base);o['surfaceCount']=3;o['popups'][0]['parent']=s(13);reject('unjoined parent',lambda:matched(o))
    o=copy.deepcopy(base);o['popups'][0]['layerRoot']=False;reject('wrong root role',lambda:matched(o))
    o=copy.deepcopy(base);o['surfaceCount']=3;o['surfaceClientCount']=2;o['members'].append({'surface':s(12,456,2),'mapped':True});parsed(o);checks.append('same PID resource IDs on distinct connections decode');reject('extra second connection',lambda:matched(o))
    reject('stale native sequence',lambda:m.parse(json.dumps(base).encode(),core_pid=123,previous_sequence=1))
    reject('unknown field',lambda:parsed({**base,'binding':{}}))
    reject('duplicate JSON key',lambda:m.parse(b'{"schema":1,'+json.dumps(base).encode()[1:],core_pid=123))
    reject('invalid UTF8',lambda:m.parse(b'\xff',core_pid=123))
    reject('nonfinite JSON',lambda:m.parse(b'{"schema":NaN}',core_pid=123))
    reject('oversize',lambda:m.parse(b' '*65537,core_pid=123))
    reject('boolean requested owner',lambda:m.match_layer_popup(parsed(base),host_pid=True,host_uid=1000,popup_id=12,root_id=11))
    return checks
if len(sys.argv)==3 and sys.argv[1]=='--exercise':
    print(json.dumps(exercise(Path(sys.argv[2]))));raise SystemExit(0)
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual strict parser/diagnostic matcher against synthetic hostile native records; no native query/host authentication/operation grant','mutants':[]}
try:
    for p in [ROOT/'join.py',Path(__file__)]:shutil.copy2(p,OUT/p.name)
    r['inputs']={str(p):sha(p) for p in [ROOT/'join.py',Path(__file__)]}
    r['checks']=exercise(OUT/'join.py')
    source=(OUT/'join.py').read_text()
    for name,old,new in [('lock-bypass',' or snapshot.locked',''),('extra-member','{m.surface for m in snapshot.members}!=allowed','False'),('duplicate-key','if k in result:','if False:'),('stale-sequence','if seq<=previous_sequence:','if False:')]:
        assert source.count(old)==1
        p=OUT/(name+'.py');p.write_text(source.replace(old,new))
        child=subprocess.run([sys.executable,'-B',str(OUT/'test.py'),'--exercise',str(p)],capture_output=True,timeout=30)
        (OUT/(name+'.stdout')).write_bytes(child.stdout);(OUT/(name+'.stderr')).write_bytes(child.stderr)
        assert child.returncode!=0 and b'unsafe acceptance:' in child.stderr,(name,child.stderr)
        r['mutants'].append({'name':name,'exitCode':child.returncode,'killed':True})
    for p,digest in r['inputs'].items():assert sha(p)==digest
    r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'checks':len(r.get('checks',[])),'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
