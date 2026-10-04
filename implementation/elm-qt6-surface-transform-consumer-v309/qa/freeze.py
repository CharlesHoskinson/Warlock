import hashlib,json,os,pathlib,stat,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def row(p):return {'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
def main():
 out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False}
 try:
  origin=json.loads((ROOT/'origin.json').read_text());parent=pathlib.Path(origin['ancestor']);manifest=parent/'component-manifest.json';assert sha(manifest)==origin['manifestSHA256'];packet=json.loads(manifest.read_text());assert packet['sourceHeld']
  external={str(manifest):row(manifest)}
  def verify(path,data):
   path=pathlib.Path(path)
   if isinstance(data,str):data={'sha256':data}
   if 'symlink' in data:assert path.is_symlink() and os.readlink(path)==data['symlink'];external[str(path)]={'symlink':data['symlink']};return
   assert path.is_file();assert sha(path)==data['sha256'],str(path)
   if 'size' in data:assert path.stat().st_size==data['size'],str(path)
   if 'mode' in data:assert stat.S_IMODE(path.stat().st_mode)==(int(data['mode'],8) if isinstance(data['mode'],str) else data['mode']),str(path)
   external[str(path)]=row(path)
  for section,base in [('files',parent),('externalFiles',None),('symlinks',parent)]:
   for name,data in packet.get(section,{}).items():verify(base/name if base else name,data)
  selected={}
  for p in ROOT.glob('qa/*/report.json'):
   v=json.loads(p.read_text());selected[str(p.relative_to(ROOT))]={'sha256':sha(p),'passed':v.get('passed')}
  if (ROOT/'client-build-report.json').is_file():
   build=json.loads((ROOT/'client-build-report.json').read_text());assert build['passed'];verify(build['artifact']['path'],build['artifact'])
   for name,data in build['sources'].items():assert sha(ROOT/name)==data['sha256'],name
   for section in ('dependencies','libraries','tools'):
    for name,data in build[section].items():verify(name,data)
  else:
   measured=ROOT.parents[0]/'elm-qt6-surface-transform-fixture-v308/component-manifest.json';mp=json.loads(measured.read_text());assert mp['sourceHeld'];external[str(measured)]=row(measured)
   for name,data in mp['files'].items():verify(measured.parent/name,data)
   for name,data in mp['externalFiles'].items():verify(name,data)
  files={};links={}
  for p in sorted(ROOT.rglob('*')):
   if p in (ROOT/'component-manifest.json',out/'report.json'):continue
   name=str(p.relative_to(ROOT));s=p.lstat()
   if stat.S_ISREG(s.st_mode):files[name]=row(p)
   elif stat.S_ISLNK(s.st_mode):links[name]={'symlink':os.readlink(p)}
   elif not stat.S_ISDIR(s.st_mode):raise RuntimeError(name)
  result={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativeReadiness':False,'scope':'Measured Qt translation source/CPU only; actual GUI correspondence and full Qt01–08 remain required.','files':files,'symlinks':links,'externalFiles':external,'selectedEvidence':selected,'origin':origin}
  for name,data in files.items():assert row(ROOT/name)==data,name
  (ROOT/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n');report.update(passed=True,ownFiles=len(files),externalFiles=len(external),manifestSHA256=sha(ROOT/'component-manifest.json'))
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),**report}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
