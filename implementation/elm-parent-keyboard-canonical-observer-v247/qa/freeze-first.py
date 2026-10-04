#!/usr/bin/python3
import hashlib,json,pathlib,stat
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bp=sorted(ROOT.glob('build-*/report.json'))[-1];build=json.loads(bp.read_text());assert build['passed'];external={}
 for name,digest in build['inputs'].items():assert sha(ROOT/name)==digest==sha(bp.parent/'inputs'/name)
 for section in ['owningFiles','dependencies','tools','linkedLibraries']:
  for name,digest in build[section].items():p=pathlib.Path(name);assert sha(p)==digest;external[name]={'sha256':digest,'size':p.stat().st_size}
 selected={}
 for prefix in ['client','observer','guard','guard-controls','preservation']:
  p=sorted((ROOT/'qa').glob(prefix+'-*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'],p
  if prefix=='client':assert len(r['checks'])==40 and r['actualCallbackChecks']==26
  if prefix=='observer':assert r['actualChecks']==32
  if prefix=='guard':assert len(r['checks'])==29 and r['moduleSHA256']==build['moduleSHA256'];assert r['clientSourceSHA256']==sha(ROOT/'native/parent-input-client.c') and r['guardSourceSHA256']==sha(ROOT/'native/private-runtime.h')
  if prefix=='guard-controls':assert len(r['controls'])==4 and all(c['behaviorallyRejected'] for c in r['controls'])
  if prefix=='preservation':assert len(r['checks'])==42
  selected[prefix]={'path':str(p),'sha256':sha(p)}
 origin=json.loads((ROOT/'origin.json').read_text());ancestor=pathlib.Path(origin['guardParentManifest']);assert sha(ancestor)==origin['guardParentManifestSHA256'];a=json.loads(ancestor.read_text())
 for name,row in a['files'].items():p=ancestor.parent/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
 for name,digest in origin['guardParentFiles'].items():assert sha(ROOT/'original239'/name)==digest
 for name,digest in origin['legacyInputs'].items():assert sha(ROOT/'original151'/name)==digest
 for name,digest in origin['observerInputs'].items():assert sha(ROOT/'native'/name if name=='surface-observer.h' else ROOT/'original225'/name)==digest
 for name in ['legacyBuildReport','observerManifest','guardParentManifest']:
  p=pathlib.Path(origin[name]);assert sha(p)==origin[name+'SHA256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
 for kind in ['module','client']:assert sha(pathlib.Path(build[kind]))==build[kind+'SHA256']
 descriptor={'schema':1,'nativeAcceptance':False,'installed':False,'inputProtocol':7,'observerProtocol':1,'module':{'path':build['module'],'sha256':build['moduleSHA256']},'client':{'path':build['client'],'sha256':build['clientSHA256']},'buildReport':str(bp),'buildReportSHA256':sha(bp),'scope':'canonical private entry guards +preserved input7 observer1 actual ABI compile/CPU only'}
 (ROOT/'parent-probe-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
 files={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and p.name!='component-manifest.json':
   if p.is_symlink():continue
   st=p.stat();files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':st.st_size,'mode':stat.S_IMODE(st.st_mode)}
 symlinks={str(p.relative_to(ROOT)):str(p.readlink()) for p in ROOT.rglob('*') if p.is_symlink()}
 manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':descriptor['scope'],'files':files,'symlinks':symlinks,'externalFiles':external,'buildReport':str(bp),'buildReportSHA256':sha(bp),'selectedEvidence':selected,'parentProof':origin}
 (ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'external':len(external),'manifestSHA256':sha(ROOT/'component-manifest.json'),'descriptorSHA256':sha(ROOT/'parent-probe-build-report.json')}))
if __name__=='__main__':main()
