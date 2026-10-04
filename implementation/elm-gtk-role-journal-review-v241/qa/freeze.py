#!/usr/bin/python3
import hashlib,json,pathlib,stat,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 selected=sorted((ROOT/'qa').glob('characterization-*/report.json'))[-1];r=json.loads(selected.read_text());assert r['passed'] and len(r['cases'])==35
 for name,digest in r['sourceInputs'].items():assert sha(ROOT/name)==digest
 header=pathlib.Path(r['gdkHeader']['path']);assert sha(header)==r['gdkHeader']['sha256']
 files={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and p.name!='component-manifest.json':
   assert not p.is_symlink();st=p.stat();files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':st.st_size,'mode':oct(stat.S_IMODE(st.st_mode))}
 m={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'unsafe predecessor decoder characterization; not corrected consumer acceptance','selectedReport':str(selected),'selectedReportSHA256':sha(selected),'files':files}
 (ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'component-manifest.json')}))
if __name__=='__main__':main()
