"""Read-only protected binder for held332; no native launch or imports."""
import hashlib,json,pathlib,stat,time,resource
ROOT=pathlib.Path(__file__).resolve().parents[1]
OWNER=ROOT.parent/'elm-own-popup-native-diagnostic-selector-v332'
def sha(p):
 with p.open('rb') as f:
  h=hashlib.file_digest(f,'sha256')
 return h.hexdigest()
def run():
 assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
 report={'passed':False,'nativeAcceptance':False,'sourceReviewOnly':True}
 sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'qa/verify.py',ROOT/'REQUIREMENTS.md',ROOT/'REVIEW.md',ROOT/'owner-pin.json']}
 try:
  pin=json.loads((ROOT/'owner-pin.json').read_text());p=OWNER/'component-manifest.json'
  assert sha(p)==pin['sha256'];m=json.loads(p.read_text())
  assert m['sourceHeld'] is True and m['evidenceIntegrityPassed'] is True
  count=0
  for rel,row in m['files'].items():
   path=pathlib.Path(rel);assert not path.is_absolute() and '..' not in path.parts
   p=OWNER/path;assert p.is_file() and not p.is_symlink()
   assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
   assert oct(stat.S_IMODE(p.stat().st_mode))==row['mode'];count+=1
  for rel,target in m.get('symlinks',{}).items():
   p=OWNER/rel;assert p.is_symlink() and str(p.readlink())==target
  external=0
  for name,value in m['externalFiles'].items():
   p=pathlib.Path(name);assert p.is_file()
   digest=value if isinstance(value,str) else value['sha256']
   assert sha(p)==digest;external+=1
  test=pathlib.Path(m['testReport']);assert sha(test)==m['testReportSHA256']
  t=json.loads(test.read_text());assert t['passed'] is True
  for rel,digest in t['inputs'].items():assert sha(OWNER/rel)==digest
  selected=pathlib.Path(m['selectorReport']);assert sha(selected)==m['selectorReportSHA256']
  e=json.loads(selected.read_text());assert e['passed'] is True and len(e['checks'])==27
  for name,digest in e['inputs'].items():assert sha(pathlib.Path(name))==digest
  import ast
  origin=json.loads((OWNER/'origin.json').read_text())
  old=ast.parse((pathlib.Path(origin['ancestor'])/'qa/native.py').read_text());new=ast.parse((OWNER/'qa/native.py').read_text())
  for tree in (old,new):tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='point']
  assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
  report['selectorReport']=str(selected);report['selectorChecks']=len(e['checks'])
  assert sha(OWNER/'component-manifest.json')==pin['sha256']
  for rel,digest in sources.items():assert sha(ROOT/rel)==digest
  report.update(passed=True,ownerManifestSHA256=pin['sha256'],ownFiles=count,externalFiles=external,testReport=str(test),checks=len(t['checks']),nativeSourceSHA256=sha(OWNER/'qa/native.py'))
 except BaseException as e:report['error']=repr(e)
 report['reviewInputs']=sources
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if report['passed']:
  rows={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))} for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='component-manifest.json'}
  (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Independent held source readiness for corrected picker selector diagnostic only','ownerManifestSHA256':pin['sha256'],'verificationReport':str(out/'report.json'),'verificationReportSHA256':sha(out/'report.json'),'files':rows},indent=2)+'\n')
 print(out/'report.json');return report
if __name__=='__main__':raise SystemExit(not run()['passed'])
