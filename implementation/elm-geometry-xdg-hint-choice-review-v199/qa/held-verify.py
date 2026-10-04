#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'elm-geometry-xdg-hint-choice-fixture-v197'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    expected='8c38a16e0787ef991ae6f5505e7eff89e96bfb979a699cba3d3969ed496757ad'
    held=ROOT/'inputs/component-manifest.json';assert sha(held)==expected==sha(BASE/'component-manifest.json')
    m=json.loads(held.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed'] and m['nativeAcceptance'] is False
    for name,row in m['files'].items():
        p=BASE/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'] and p.stat().st_mode&0o777==row['mode'],name
    assert m['sourceSHA256']==sha(ROOT/'inputs/native/xdg-origin-client.c')=='bfd9ae895fcba50f90690cdc1b8b207ecc31e2240b36e93935a7288e37857b31'
    report=ROOT/'qa/review-1791130028093348253/report.json';r=json.loads(report.read_text());assert r['passed'] and r['sourceBlockerFound'] is False
    out=ROOT/'qa'/('held-review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'passed':True,'filesVerified':len(m['files']),'owningManifestSHA256':expected,'reviewReportSHA256':sha(report),'sourceBlockerFound':False,'nativeAcceptance':False,'scope':'Independent final held197 protocol/source/evidence review; actual build/75+25+7+5 existing CPU proofs verified, no behavior rerun/native.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    target=ROOT/'component-manifest.json';assert not target.exists()
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
    component={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceBlockerFound':False,'nativeAcceptance':False,'owningManifestSHA256':expected,'scope':result['scope'],'files':files}
    target.write_text(json.dumps(component,indent=2)+'\n');print(json.dumps({'passed':True,'filesVerified':len(m['files']),'report':str(out/'report.json'),'manifestSHA256':sha(target)}))
if __name__=='__main__':main()
