import hashlib
import json
from pathlib import Path
import stat
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    packet={'sourceHeld':True,'evidenceIntegrityPassed':False,'nativeAcceptance':False,'full22Coverage':False,'scope':'four-profile screenshot source-only; CPU and preflight closure only','files':{}}
    tests=sorted((ROOT/'qa').glob('test-*/report.json'));preflights=sorted((ROOT/'qa').glob('preflight-*/report.json'))
    for selected in (tests[-1],preflights[-1]):
        data=json.loads(selected.read_text());assert data['passed']
        for name,digest in data['inputs'].items():assert sha(Path(name))==digest,name
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name=='component-manifest.json':continue
        assert not p.is_symlink(),str(p)
        packet['files'][str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
    packet['acceptedCPUReport']=str(tests[-1]);packet['acceptedPreflight']=str(preflights[-1]);packet['evidenceIntegrityPassed']=True
    destination=ROOT/'component-manifest.json';assert not destination.exists();destination.write_text(json.dumps(packet,indent=2)+'\n')
    for name,row in packet['files'].items():assert sha(ROOT/name)==row['sha256'],name
    print(json.dumps({'passed':True,'manifest':str(destination),'sha256':sha(destination),'files':len(packet['files'])}))
if __name__=='__main__':main()
