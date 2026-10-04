#!/usr/bin/python3
import hashlib,json,pathlib,stat
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 selected=sorted((ROOT/'qa').glob('characterization-*/report.json'))[-1];r=json.loads(selected.read_text());assert r['passed'] and len(r['cases'])==71 and not r['typedErrorGaps']
 for name,digest in r['sourceInputs'].items():assert sha(ROOT/name)==digest;assert sha(REPO/'implementation/elm-gtk-role-native-v238/qa'/pathlib.Path(name).name)==digest
 assert sha(pathlib.Path(r['gdkHeader']['path']))==r['gdkHeader']['sha256']
 controls=sorted((ROOT/'qa').glob('mutations-*/report.json'))[-1];m=json.loads(controls.read_text());assert m['passed'] and len(m['controls'])==5
 for c in m['controls']:assert c['rejected'] and c['exit']!=0 and sha(pathlib.Path(c['report']))==c['reportSHA256']
 ancestor=REPO/'implementation/elm-gtk-role-journal-review-v241/component-manifest.json';assert sha(ancestor)=='ac44f37d7f9c447144494ec6d101d27cc78ca9c0a6800cf707c1e7f086e36cf9'
 a=json.loads(ancestor.read_text())
 for name,row in a['files'].items():p=ancestor.parent/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
 integer=REPO/'implementation/elm-gtk-journal-integer-overflow-v242/qa/characterization-1791138883395887393/report.json';assert integer.is_file()
 files={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and p.name!='component-manifest.json':
   assert not p.is_symlink();st=p.stat();files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':st.st_size,'mode':oct(stat.S_IMODE(st.st_mode))}
 result={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'corrected actual journal CPU71 +5unsafe source controls; mock Actor.close only','selectedReport':str(selected),'selectedReportSHA256':sha(selected),'mutationReport':str(controls),'mutationReportSHA256':sha(controls),'predecessors':{str(ancestor):sha(ancestor),str(integer):sha(integer)},'sourceInputs':r['sourceInputs'],'files':files}
 (ROOT/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'component-manifest.json')}))
if __name__=='__main__':main()
