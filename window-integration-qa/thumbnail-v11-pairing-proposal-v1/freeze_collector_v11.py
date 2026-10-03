"""External V10 complete union proposal; freeze belongs to root, no GUI launch."""
import argparse,hashlib,importlib.util,json,os,stat,sys
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa'); BASE=QA/'family-preparation-thumbnail-v10'; B=QA/'family-preparation-thumbnail-v11'; DESIGN=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26')
PACKETS=((BASE/'frozen-inputs.json','bcabc3433ce35d76a9fb403fc9dac9f4c6f5444b0e14e83108a213ee688811d9','symlinks'),(SERVICE/'manifest-housekeeping-admission-v26.json','e98809f3cee21c3fc8a0447c98c76915cc3083df2ac1090f1531c7fa3b25a1b2','links'))
REVIEW=QA/'housekeeping-admission-v26-root-full-proof-review-v1.json'; REVIEW_SHA='cf074ce30926bb918d55e86f05b00b30c6c679454476e63b1a338b311deca49f'
EXTRA_REVIEWS=[('/home/hoskinson/window-integration-qa/housekeeping-admission-v26-root-frozen-review-v1.json', '0079e936585a6c0aec0fe40613537dba03c09e9454af83f95a8706337af6feb5'), ('/home/hoskinson/window-integration-qa/thumbnail-helper-failure-drain-root-source-review-v1.json', 'bcc383d4a59ac36a04ea43c864eaee3dc775bc6be43de16eab1387f5b7d37616')]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_closure():
 p=BASE/'collector_v9_closure.py'
 if sha(p)!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('approved alias source changed')
 s=importlib.util.spec_from_file_location('v10_closure',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
C=load_closure()
def verify(row):
 if set(row['inputs'])!=set(row['inputModes']):raise ValueError('complete modes required')
 C.verify_links(row['symlinks'])
 for n,d in row['inputs'].items():C.retained_file(n,d,row['inputModes'][n],row['inputs'],row['inputModes'],row['symlinks'])
 C.verify_links(row['symlinks'])
def save(path,row):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as stream:json.dump(row,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
def inventory(review=None):
 inputs={};modes={};links={}
 def merge(n,d,m):
  if n in inputs and (inputs[n]!=d or modes[n]!=m):raise ValueError('selected byte/mode conflict: '+n)
  inputs[n]=d;modes[n]=m
 def add(p):
  p=Path(p).absolute()
  for a in (p,*p.parents):
   if a.is_symlink():
    t=os.readlink(a)
    if str(a)in links and links[str(a)]!=t:raise ValueError('selected link conflict')
    links[str(a)]=t
  d=sha(p);m=stat.S_IMODE(p.stat().st_mode);merge(str(p),d,m);merge(str(p.resolve(strict=True)),d,m)
 for p,h,key in PACKETS:
  if p.is_symlink()or sha(p)!=h:raise ValueError('selected frozen packet changed')
  r=json.loads(p.read_text());verify({**r,'symlinks':r[key]})
  for n,t in r[key].items():
   if n in links and links[n]!=t:raise ValueError('retained link conflict')
   links[n]=t
  for n,d in r['inputs'].items():merge(n,d,r['inputModes'][n])
  add(p)
 if sha(REVIEW)!=REVIEW_SHA:raise ValueError('root V26 proof review changed')
 add(REVIEW)
 for p,h in EXTRA_REVIEWS:
  if sha(p)!=h:raise ValueError('explicit root review changed: '+p)
  add(p)
 proof=QA/'thumbnail-v11-full-proof-v1/report.json'
 report=json.loads(proof.read_text())
 if report.get('result')!='pass' or report.get('pythonTests')!=169 or report.get('quintNamedScenarios')!=205 or report.get('quintModels')!=14 or len(report.get('checks',[]))!=43 or not report.get('sourceUnchangedDuringProof'):raise ValueError('required complete B11 CPU/formal proof absent')
 for c in report['checks']:
  if c['exitCode']!=0 or sha(c['log'])!=c['sha256']:raise ValueError('actual proof log differs')
 for p,w in report['sources'].items():
  if sha(p)!=w['sha256'] or stat.S_IMODE(Path(p).stat().st_mode)!=w['mode']:raise ValueError('actual proof source changed')
 plan=json.loads((DESIGN/'intended-source-map.json').read_text())
 if not B.is_dir():raise ValueError('fresh reviewed V11 derivative not installed')
 inherited=0;changed=[]
 for p in BASE.rglob('*'):
  rel=p.relative_to(BASE)
  if '__pycache__'in rel.parts or any(v.startswith('attempt-')for v in rel.parts)or rel==Path('frozen-inputs.json'):continue
  q=B/rel
  if p.is_symlink():
   if not q.is_symlink()or os.readlink(p)!=os.readlink(q):raise ValueError('copied source symlink changed: '+str(rel))
  elif p.is_file():
   if not q.is_file()or stat.S_IMODE(p.stat().st_mode)!=stat.S_IMODE(q.stat().st_mode):raise ValueError('copied source/mode absent: '+str(rel))
   inherited+=1
   if sha(p)!=sha(q):
    if str(rel)not in plan or sha(p)!=plan[str(rel)]['originalSHA256']or sha(q)!=plan[str(rel)]['proposedSHA256']:raise ValueError('unapproved collector delta: '+str(rel))
    changed.append(str(rel))
 if sorted(changed)!=sorted(plan):raise ValueError('exact three approved collector deltas required')
 for folder in (B,DESIGN,BASE/'attempt-baseline-1',QA/'thumbnail-v11-full-proof-v1',QA/'thumbnail-helper-failure-drain-design-v1',QA/'thumbnail-helper-failure-drain-design-v2',QA/'thumbnail-helper-failure-drain-design-v3'):
  for p in folder.rglob('*'):
   if not p.is_file()or '__pycache__'in p.parts:continue
   if p.is_relative_to(B)and (p==B/'frozen-inputs.json'or any(v.startswith('attempt-')for v in p.relative_to(B).parts)):continue
   add(p)
 if review:
  r=json.loads(review.read_text())
  if r.get('result')!='pass':raise ValueError('root collector review must pass')
  add(review)
 row={'version':'thumbnail-v11-complete-union','inputs':dict(sorted(inputs.items())),'inputModes':dict(sorted(modes.items())),'symlinks':dict(sorted(links.items())),'inheritedLocalFiles':inherited,'changedCollectorSources':sorted(changed),'selectedServiceManifest':str(PACKETS[1][0]),'selectedServiceManifestSHA256':PACKETS[1][1],'originalBaselineRequired':38,'originalFaultsRequired':34,'nativeAccepted':False,'mainChanges':False}
 verify(row);return row

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 for flag in ('collect','freeze','verify'):g.add_argument('--'+flag,action='store_true')
 p.add_argument('--review',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.verify:r=json.loads((B/'frozen-inputs.json').read_text());verify(r)
 elif a.collect:
  if not a.output:raise ValueError('fresh external output required')
  r=inventory(a.review);save(a.output,r)
 else:
  if not a.review:raise ValueError('explicit root source review required')
  union=inventory(a.review);sys.path.insert(0,str(QA));sys.path.insert(0,str(B))
  spec=importlib.util.spec_from_file_location('v10_native_freezer',B/'native_integration.py');candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate);original_save=candidate.save
  def complete_save(path,row):
   if Path(path)!=B/'frozen-inputs.json':return original_save(path,row)
   row={**row};inputs=dict(row['inputs']);modes=dict(row['inputModes']);links=dict(row['symlinks'])
   for n,d in union['inputs'].items():
    if n in inputs and (inputs[n]!=d or modes[n]!=union['inputModes'][n]):raise ValueError('native union conflict')
    inputs[n]=d;modes[n]=union['inputModes'][n]
   for n,t in union['symlinks'].items():
    if n in links and links[n]!=t:raise ValueError('native link union conflict')
    links[n]=t
   row.update(inputs=inputs,inputModes=modes,symlinks=links,selectedServiceManifest=union['selectedServiceManifest'],selectedServiceManifestSHA256=union['selectedServiceManifestSHA256'],collectorUnionReview=str(a.review),collectorUnionReviewSHA256=sha(a.review),originalBaselineRequired=38,originalFaultsRequired=34,nativeAccepted=False)
   verify(row);save(path,row)
  candidate.save=complete_save;candidate.freeze();r=json.loads((B/'frozen-inputs.json').read_text());verify(r)
 print(json.dumps({'result':'pass','inputs':len(r['inputs']),'modes':len(r['inputModes']),'links':len(r['symlinks']),'nativeAccepted':False}))
if __name__=='__main__':main()
