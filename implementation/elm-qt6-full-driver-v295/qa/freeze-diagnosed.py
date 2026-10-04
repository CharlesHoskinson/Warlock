"""Freeze source/CPU characterization, explicitly excluding native readiness."""
import hashlib, importlib.util, json, os, pathlib, resource, stat, sys, time, traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def row(p):
 s=p.lstat()
 return {'sha256':sha(p),'size':s.st_size,'mode':oct(stat.S_IMODE(s.st_mode))}
def main():
 assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=ROOT/'qa'/('freeze-diagnosed-'+str(time.time_ns()));out.mkdir()
 report={'passed':False,'nativeAcceptance':False,'nativeReadiness':False}
 try:
  spec=importlib.util.spec_from_file_location('qt295_preflight',ROOT/'qa/preflight.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  *_,external=m.verify()
  evidence={}
  for rel in ('qa/preflight-1791152797491999102/report.json','qa/domains-test-1791151815309070496/report.json','qa/driver-test-1791152760593442130/report.json','qa/capture-scope-1791152191152348149/report.json'):
   p=ROOT/rel;value=json.loads(p.read_text());assert value['passed'] is True,rel;evidence[rel]=row(p)
  descriptor=json.loads((ROOT/'qt-domains-build-report.json').read_text());assert sha(descriptor['report'])==descriptor['sha256'];assert sha(descriptor['binary'])==descriptor['binarySHA256']
  artifact=json.loads(pathlib.Path(descriptor['report']).read_text());assert artifact['passed'] and artifact['sourceSHA256']==sha(ROOT/'native/qt-domains.cpp')
  files={};links={}
  for p in sorted(ROOT.rglob('*')):
   if p==ROOT/'component-manifest.json' or p==out/'report.json':continue
   rel=str(p.relative_to(ROOT));s=p.lstat()
   if stat.S_ISLNK(s.st_mode):links[rel]={'symlink':os.readlink(p)}
   elif stat.S_ISREG(s.st_mode):files[rel]=row(p)
   elif not stat.S_ISDIR(s.st_mode):raise RuntimeError('Unexpected source object '+rel)
  packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativeReadiness':False,'fullCampaignPassed':False,'scope':'Diagnosed full Qt01–08 executable source and CPU characterization only; no Qt GUI campaign.','knownBlockers':['Borrowed GTK297 shell right-click path times out; source303 is not an authority bypass.','Qt289 lacks measured decorated surface-to-window translation; inherited296 zero-margin mapping unqualified.'],'files':files,'symlinks':links,'externalFiles':external,'selectedEvidence':evidence,'compiledQtArtifact':descriptor,'historicalEvidence':'Copied290 and pre-correction301 reports remain ancestor/failed diagnostic evidence, never Qt native acceptance.'}
  for rel,r in files.items():assert row(ROOT/rel)==r,rel
  (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
  report.update(passed=True,regularFiles=len(files),symlinks=len(links),externalFiles=len(external),manifestSHA256=sha(ROOT/'component-manifest.json'))
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),**report}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
