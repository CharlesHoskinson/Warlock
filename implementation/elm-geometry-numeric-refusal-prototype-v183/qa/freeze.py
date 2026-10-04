#!/usr/bin/env python3
"""Freeze exact isolated prototype bytes and successful/negative CPU evidence."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    report=ROOT/'qa/numeric-1791127799736899141/report.json'
    data=json.loads(report.read_text());assert data['passed'] and data['decoderCaseCount']==190
    for name,row in data['files'].items():
        p=report.parent/name;assert not p.is_symlink() and digest(p)==row['sha256'] and p.stat().st_size==row['size']
    upstream=json.loads((ROOT/'upstream.json').read_text());assert digest(REPO/upstream['heldManifest'])==upstream['heldManifestSHA256']
    held={r['path']:r for r in json.loads((REPO/upstream['heldManifest']).read_text())['files']}
    changes=[]
    for owning,row in upstream['files'].items():
        original=ROOT/'original/adapter'/Path(owning).name
        assert digest(original)==row['sha256']==held[owning]['sha256']
        candidate=ROOT/'candidate/adapter'/original.name
        if digest(candidate)!=digest(original):changes.append(original.name)
    assert changes==['geometry_size_policy.py']
    files={}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.name=='held-source-manifest.json' or any(part.startswith('freeze-') for part in p.relative_to(ROOT).parts):continue
        assert not p.is_symlink()
        files[str(p.relative_to(ROOT))]={'sha256':digest(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
    manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'productionAdoption':False,'scope':'Isolated numeric typed-refusal prototype;190 actual copied-decoder CPU cases and original/finite-bypass controls. Synthetic received-envelope boundary, no transport/model/GUI.','files':files,'selectedReport':str(report.relative_to(ROOT)),'selectedReportSHA256':digest(report),'owningAncestorManifestSHA256':upstream['heldManifestSHA256']}
    target=ROOT/'qa/held-source-manifest.json';assert not target.exists();target.write_text(json.dumps(manifest,indent=2)+'\n')
    out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir(mode=0o700)
    for name,row in files.items():assert digest(ROOT/name)==row['sha256']
    (out/'report.json').write_text(json.dumps({'passed':True,'kind':'prototype-evidence-integrity','filesVerified':len(files),'manifestSHA256':digest(target),'sourceHeld':True,'nativeAcceptance':False,'productionAdoption':False},indent=2)+'\n')
    print(json.dumps({'passed':True,'files':len(files),'manifest':str(target),'sha256':digest(target),'report':str(out/'report.json')}))
if __name__=='__main__':main()
