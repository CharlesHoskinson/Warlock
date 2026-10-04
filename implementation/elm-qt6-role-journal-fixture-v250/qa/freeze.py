#!/usr/bin/python3
import hashlib,json,pathlib,stat,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/f'freeze-{time.time_ns()}';out.mkdir(mode=0o700);report={'passed':False,'nativeAcceptance':False}
 try:
  build=json.loads((ROOT/'client-build-report.json').read_text());assert build['passed'];assert sha(pathlib.Path(build['artifact']['path']))==build['artifact']['sha256']
  verified=0
  for name,row in build['sources'].items():
   assert sha(ROOT/name)==row['sha256'];assert sha(pathlib.Path(row['capture']))==row['sha256'];verified+=2
  for kind in ['dependencies','libraries','tools']:
   for name,row in build[kind].items():assert sha(pathlib.Path(name))==row['sha256'],name;verified+=1
  tests=sorted((ROOT/'qa').glob('test-*/report.json'))[-1];lifetime=sorted((ROOT/'qa').glob('lifetime-*/report.json'))[-1]
  test=json.loads(tests.read_text());life=json.loads(lifetime.read_text());assert test['passed'] and life['passed'];assert test['buildReportSHA256']==sha(ROOT/'client-build-report.json');assert life['sourceSHA256']==sha(ROOT/'native/qt-role-client.cpp')
  for name,row in test['sourceInputs'].items():assert sha(ROOT/name)==row['sha256']
  assert sha(lifetime.parent/'lifetime-test.py')==sha(ROOT/'qa/lifetime-test.py')
  ancestor=ROOT.parent/'elm-parent-keyboard-canonical-observer-v247';assert sha(ROOT/'native/private-runtime.h')==sha(ancestor/'native/private-runtime.h')
  previous=json.loads((ancestor/'component-manifest.json').read_text());assert previous['sourceHeld'] and previous['evidenceIntegrityPassed']
  for name,row in previous['files'].items():
   p=ancestor/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'] and stat.S_IMODE(p.stat().st_mode)==(int(row['mode'],8) if isinstance(row['mode'],str) else row['mode']);verified+=1
  report.update(passed=True,verifiedDependenciesAndAncestor=verified,tests={'path':str(tests),'sha256':sha(tests),'checks':len(test['checks'])},lifetime={'path':str(lifetime),'sha256':sha(lifetime),'mockAssertions':life['assertions'],'unsafeControls':len(life['controls'])},ancestorManifestSHA256=sha(ancestor/'component-manifest.json'))
 except Exception as e:report['error']=str(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if report['passed']:
  files={}
  for p in sorted(ROOT.rglob('*')):
   if p.is_file() and p.name!='component-manifest.json':
    assert not p.is_symlink(),p;st=p.stat();files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':st.st_size,'mode':oct(stat.S_IMODE(st.st_mode))}
  manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Qt6 actual compiled fixture/CPU commands and extracted mocked lifetime qualification only','sourceSHA256':sha(ROOT/'native/qt-role-client.cpp'),'build':build['artifact'],'files':files,'verificationReport':str(out/'report.json'),'verificationReportSHA256':sha(out/'report.json')}
  (ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error'),'manifestSHA256':sha(ROOT/'component-manifest.json') if report['passed'] else None}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
