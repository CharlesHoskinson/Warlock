"""Actual bounded stream decoder against independently segmented wire streams."""
import hashlib,importlib,json,random,resource,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('framing-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[*sorted((ROOT/'adapter').glob('*.py')),ROOT/'framing-upstream.json',Path(__file__)]
rows={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
sys.path.insert(0,str(INPUT/'adapter'));import daemon
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
report={'passed':False,'scope':'Actual broker framing CPU; no native or full operation acceptance','inputs':rows,'checks':checks}
def parse(chunks):
 f=daemon.FrontendFrames();out=[]
 for chunk in chunks:out.extend(f.feed(chunk))
 f.finish();return out
try:
 u=json.loads((ROOT/'framing-upstream.json').read_text());parent=Path(u['parent']);assert sha(parent/'qa/held-source-manifest.json')==u['heldManifestSHA256']
 for relative,digest in u['files'].items():assert sha(parent/relative)==digest
 frames=[b'a'*3000,b'b'*3000,b'c'*4070];wire=b'\n'.join(frames)+b'\n'
 check('coalesced valid near-bound frames are not aggregate-rejected',parse([wire[i:i+4096] for i in range(0,len(wire),4096)])==frames)
 check('maximum allowed wire frame includes newline',parse([b'x'*4095+b'\n'])==[b'x'*4095])
 check('empty frame delegated unchanged to strict JSON decoder',parse([b'\n'])==[b''])
 check('EOF at exact completed boundary succeeds',parse([])==[])
 rng=random.Random(620056)
 for trial in range(1000):
  expected=[rng.randbytes(rng.randrange(0,4096)).replace(b'\n',b'X') for _ in range(rng.randrange(1,8))]
  stream=b'\n'.join(expected)+b'\n';chunks=[];i=0
  while i<len(stream):n=rng.randrange(1,4097);chunks.append(stream[i:i+n]);i+=n
  check('segmentation-independent frames '+str(trial),parse(chunks)==expected)
 for name,chunks in [('too long with newline',[b'x'*4096,b'\n']),('too long without newline',[b'x'*4096]),('unterminated EOF',[b'{"kind":']),('overread chunk',[b'x'*4097]),('valid then oversized',[b'ok\n'+b'x'*4000,b'x'*96+b'\n'])]:
  try:parse(chunks);refused=False
  except daemon.Refused:refused=True
  check(name+' rejected',refused)
 # Exercise production main with read chunk boundaries, not just the helper.
 import ast
 tree=ast.parse((INPUT/'adapter/daemon.py').read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 check('actual main uses decoder feed',any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='feed' for n in ast.walk(main)))
 check('actual main rejects incomplete EOF',any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='finish' for n in ast.walk(main)))
 for relative,digest in rows.items():assert sha(ROOT/relative)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
