import hashlib,json,os,pathlib,stat,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def row(p):return {'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
def main():
 out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir();r={'passed':False,'nativeAcceptance':False,'nativeReadiness':False}
 try:
  selected={};external={}
  for rel in ('qa/preflight-1791155843494217979/report.json','qa/test-1791155922296991118/report.json','qa/fresh-import-1791156115100577522/report.json'):
   p=ROOT/rel;x=json.loads(p.read_text());assert x['passed'] is True;selected[rel]=row(p)
   for name,data in x.get('inputs',{}).items():
    p=pathlib.Path(name)
    if 'symlink' in data:assert p.is_symlink() and os.readlink(p)==data['symlink'];external[name]=data
    else:assert sha(p)==data['sha256'];external[name]=row(p)
  preflight=json.loads((ROOT/'qa/preflight-1791155843494217979/report.json').read_text());descriptor=json.loads((ROOT/'runtime/native-build-report.json').read_text());assert sha(ROOT/'runtime/native-build-report.json')==preflight['descriptorSHA256'];assert descriptor['binary']==preflight['descriptor']['binary'] and descriptor['plugin']==preflight['descriptor']['plugin']
  for p in [pathlib.Path(descriptor['linkClosureReport'])]:assert sha(p)==descriptor['linkClosureReportSHA256']
  files={};links={}
  for p in sorted(ROOT.rglob('*')):
   if p in (ROOT/'component-manifest.json',out/'report.json'):continue
   s=p.lstat();name=str(p.relative_to(ROOT))
   if stat.S_ISREG(s.st_mode):files[name]=row(p)
   elif stat.S_ISLNK(s.st_mode):links[name]={'symlink':os.readlink(p)}
   elif not stat.S_ISDIR(s.st_mode):raise RuntimeError(name)
  packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativeReadiness':False,'compileRuntimeLookupClosurePassed':True,'liveProcessMapsProven':False,'hostControllerScopeProven':False,'scope':'Exact307/319/315 metadata/native ABI and current AQ155 library lookup qualification; inert proposal only, no GUI or own-popup grant.','files':files,'symlinks':links,'externalFiles':external,'selectedCPUReports':selected,'nativeTuple':descriptor,'missingNativePrerequisites':['Reviewed322 full DTO/matcher','Actual trusted current host root/popup/controller publication scope','Actual307/319/315/AQ155 process maps and layer-popup/wholegrab/close witness'],'historicalAcceptanceTransferred':False}
  for name,data in files.items():assert row(ROOT/name)==data,name
  (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n');r.update(passed=True,ownFiles=len(files),externalFiles=len(external),manifestSHA256=sha(ROOT/'component-manifest.json'))
 except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),**r}));return 0 if r['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
