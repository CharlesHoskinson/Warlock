"""Validate the actual core build and exported interface before private QA."""
import hashlib,json,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
BUILD=ROOT/'build-1791096651129914247/report.json'
OUT=ROOT/'qa'/('closure-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Build source/dependency closure and exported symbol preservation; no plugin execution or native acceptance','inputs':{str(Path(__file__).resolve()):sha(__file__),str(BUILD):sha(BUILD)}}
try:
 b=json.loads(BUILD.read_text());assert b['passed'] and b['unchangedArchiveMembers']==431
 assert set(b['changedArchiveMembers'])=={'Window.cpp.o','FullscreenController.cpp.o'}
 binary=Path(b['binary']);assert sha(binary)==b['binarySHA256']
 for rel,value in b['inputs'].items():assert sha(ROOT/rel)==value,rel
 for path,value in b['dependencies'].items():assert sha(path)==value,path
 for path,value in b['retainedPolicyHeaders'].items():assert sha(path)==value,path
 ancestor=Path(b['ancestor']['binary']);assert sha(ancestor)==b['ancestor']['binarySHA256']
 symbols={}
 for name,path in [('ancestor',ancestor),('candidate',binary)]:
  p=subprocess.run(['/usr/bin/nm','-D','--defined-only',str(path)],capture_output=True,timeout=30)
  (OUT/(name+'.symbols')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);assert p.returncode==0
  rows=[line.split() for line in p.stdout.decode().splitlines()]
  assert all(len(row)==3 for row in rows)
  symbols[name]={(row[1],row[2]) for row in rows}
 missing=sorted(symbols['ancestor']-symbols['candidate']);r['missingSymbols']=missing
 assert not missing,'Owning core exported symbols removed or type changed'
 r.update(passed=True,binary=str(binary),sha256=sha(binary),buildReport=str(BUILD),buildReportSHA256=sha(BUILD),dependencyCount=len(b['dependencies']),ancestorExportCount=len(symbols['ancestor']),candidateExportCount=len(symbols['candidate']),additionalSymbols=sorted(symbols['candidate']-symbols['ancestor']))
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()}
report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 descriptor=ROOT/'native-build-report.json';assert not descriptor.exists(),'Never overwrite an existing selected build descriptor'
 descriptor.write_text(json.dumps({'result':'pass','binary':r['binary'],'sha256':r['sha256'],'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'closureReport':str(report),'closureReportSHA256':sha(report),'nativeAcceptance':False},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
