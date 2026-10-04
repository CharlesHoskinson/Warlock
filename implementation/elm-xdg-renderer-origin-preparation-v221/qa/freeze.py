import hashlib
import json
from pathlib import Path
import shutil
import stat
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    latest=sorted((ROOT/'qa').glob('provenance-*/report.json'))[-1];report=json.loads(latest.read_text());assert report['passed']
    for name,value in report['inputs'].items():assert sha(Path(name))==value,name
    captures=ROOT/'source-captures';captures.mkdir();origins={}
    for index,(name,value) in enumerate(report['inputs'].items()):
        source=Path(name)
        if source.suffix not in ('.cpp','.hpp','.json','.md','.h'):continue
        destination=captures/(str(index)+'-'+source.name);shutil.copy2(source,destination);assert sha(destination)==value
        origins[str(destination.relative_to(ROOT))]={'origin':name,'sha256':value}
    (ROOT/'capture-origins.json').write_text(json.dumps(origins,indent=2)+'\n')
    packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'read-only owning renderer provenance and repair gates; no compiler/native/model/source changes','acceptedReport':str(latest),'files':{}}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.name=='component-manifest.json' or '__pycache__' in path.parts:continue
        assert not path.is_symlink()
        packet['files'][str(path.relative_to(ROOT))]={'sha256':sha(path),'size':path.stat().st_size,'mode':stat.S_IMODE(path.stat().st_mode)}
    dest=ROOT/'component-manifest.json';assert not dest.exists();dest.write_text(json.dumps(packet,indent=2)+'\n')
    for name,row in packet['files'].items():assert sha(ROOT/name)==row['sha256']
    print(json.dumps({'passed':True,'manifest':str(dest),'sha256':sha(dest),'files':len(packet['files'])}))
if __name__=='__main__':main()
