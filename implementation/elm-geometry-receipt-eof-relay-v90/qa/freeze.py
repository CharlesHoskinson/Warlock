"""Protected exact source/evidence hold; no GUI or native acceptance."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parents=json.loads((ROOT/'parent.json').read_text())
for info in parents.values():
 p=REPO/info['path'];assert sha(p)==info['sha256'];m=json.loads(p.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
 for rel,e in m['files'].items():
  f=p.parent.parent/rel
  if 'symlink' in e:assert f.is_symlink() and os.readlink(f)==e['symlink']
  else:
   assert not f.is_symlink() and f.is_file() and f.stat().st_size==e['size'] and sha(f)==e['sha256']
   if 'mode' in e:assert stat.S_IMODE(f.stat().st_mode)==e['mode']
 for rel,target in m.get('symlinks',{}).items():assert os.readlink(p.parent.parent/rel)==target
for name in ['test.py','edges.py','deadline.py']:assert sha(ROOT/'qa'/name)==sha(REPO/'implementation/elm-geometry-broker-eof-deadline-v92/qa'/name)
reports=[]
for name,count in [('test-1791109060303661045',19),('edges-1791109060301660591',7),('deadline-1791109060302741537',7),('profile-1791109052193226122',24)]:
 p=ROOT/'qa'/name/'report.json';m=json.loads(p.read_text());assert m['passed'] and len(m['checks'])==count and all(c['passed'] for c in m['checks']);assert sha(ROOT/'qa/relay.py')==sha(p.parent/'inputs/qa/relay.py')
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
failed=ROOT/'qa/profile-1791109029811155623/report.json';assert not json.loads(failed.read_text())['passed']
files={}
for p in sorted(ROOT.rglob('*')):
 if p.is_symlink():files[str(p.relative_to(ROOT))]={'symlink':os.readlink(p)}
 elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'full09Accepted':False,'releaseAcceptance':False,'completedRequirementIds':[],'scope':'Fixed broker/receipt profile CPU57; native scenario09 and owning broker lifecycle remain unqualified','parents':parents,'reports':reports,'failure':{'path':str(failed.relative_to(ROOT)),'sha256':sha(failed)},'files':files,'api':{'entrypoint':'qa/relay.py ABS_PRIVATE_CONFIG','profiles':['broker','receipt'],'EOFDeadlineSeconds':3,'queueBytesPerDirection':8192}}
p=ROOT/'qa/held-source-manifest.json'
with p.open('x') as f:f.write(json.dumps(m,indent=2)+'\n')
p.chmod(0o444);print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(files)}))
