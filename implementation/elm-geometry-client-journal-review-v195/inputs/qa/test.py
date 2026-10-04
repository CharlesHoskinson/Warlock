import copy,hashlib,json,sys,time
from pathlib import Path
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p));from journal import parse,InvalidJournal
out=p/'qa'/('test-'+str(time.time_ns()));out.mkdir();pid=123;profile=[16,24,8,12,2]
base={'pid':pid,'sequence':1,'monotonicNs':1,'serial':4294967295,'ackedSerial':0,'width':320,'height':180,'maximized':False,'fullscreen':False}
rows=[]
for kind in ['configure','ack-configure','buffercommit','ready','normalexit']:
 r={**base,'event':kind,'sequence':len(rows)+1,'monotonicNs':len(rows)+1}
 if kind!='configure':r['ackedSerial']=r['serial']
 if kind=='buffercommit':r.update(bufferSerial=r['serial'],geometry=[16,24,320,180],surfaceSize=[344,216],bufferSize=[688,432],scale=2,inflight=1,allocatedBytes=688*432*4,argb='ffabcdef')
 if kind=='ready':r.update(title='ELM-XDG-ORIGIN-PROBE-123',appId='elm-xdg-origin-probe')
 rows.append(r)
def wire(x):return ('\n'.join(json.dumps(r) for r in x)+'\n').encode()
checks=[]
def check(name,data,expected,observed_profile=profile):
 try:parse(data,pid,observed_profile,terminal=True);accepted=True
 except InvalidJournal:accepted=False
 checks.append({'name':name,'passed':accepted==expected})
check('complete synthetic lifecycle',wire(rows),True)
for name,index,key,value in [('foreign PID',2,'pid',456),('sequence reuse',2,'sequence',2),('wrong ACK',1,'ackedSerial',12),('wrong buffer serial',2,'bufferSerial',12),('missing scale',2,'scale',1),('oversized buffer',2,'allocatedBytes',2**30),('bool width',2,'width',True),('wrong ready title',3,'title','other'),('event object',2,'event',{}),('floating scale',2,'scale',2.0),('underdeclared allocation',2,'allocatedBytes',1),('floating buffer serial',2,'bufferSerial',4294967295.0),('ACK mode mismatch',1,'maximized',True),('commit mode mismatch',2,'fullscreen',True),('stale ready serial',3,'serial',12)]:
 bad=copy.deepcopy(rows);bad[index][key]=value;check(name,wire(bad),False)
check('omitted ACK',wire([rows[0],rows[2]]),False)
check('truncated line',wire(rows)[:-1],False)
check('duplicate JSON key',wire(rows).replace(b'"pid": 123',b'"pid": 123, "pid": 123',1),False)
check('nonfinite JSON',wire(rows).replace(b'"monotonicNs": 1',b'"monotonicNs": NaN',1),False)
check('missing normal exit',wire(rows[:-1]),False)
wrapped=copy.deepcopy(rows[:-2]);wrapped+=copy.deepcopy(wrapped);wrapped[3]['serial']=0;wrapped[3]['ackedSerial']=4294967295;wrapped[4]['serial']=0;wrapped[4]['ackedSerial']=0;wrapped[5]['serial']=0;wrapped[5]['ackedSerial']=0;wrapped[5]['bufferSerial']=0;wrapped+=copy.deepcopy(rows[-2:])
for i,r in enumerate(wrapped,1):r['sequence']=i;r['monotonicNs']=i
for r in wrapped[-2:]:r['serial']=0;r['ackedSerial']=0
check('ordered serial wrap',wire(wrapped),True)
bad=copy.deepcopy(rows);bad[3]['extra']=float('inf');check('global nonfinite extra',wire(bad).replace(b'Infinity',b'1e400'),False)
big=copy.deepcopy(rows)
for r in big:r['width']=4096;r['height']=4096
big[2].update(geometry=[16,24,4096,4096],surfaceSize=[4120,4132],bufferSize=[4120,4132],scale=1,allocatedBytes=68095360)
check('per-buffer64MiB cap',wire(big),False,[16,24,8,12,1])
report={'passed':all(c['passed'] for c in checks),'checks':checks,'sourceSHA256':hashlib.sha256((p/'journal.py').read_bytes()).hexdigest(),'nativeAcceptance':False,'scope':'Synthetic journal validator tests; no native capture'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(checks)}));raise SystemExit(0 if report['passed'] else 1)
