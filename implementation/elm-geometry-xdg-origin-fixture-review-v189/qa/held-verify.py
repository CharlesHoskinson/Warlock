#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'elm-geometry-xdg-origin-fixture-v184'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    held=ROOT/'inputs/component-manifest.json'
    expected='50aae9ec53dab7e8df54da9b1cef249e6e2d3eec440f9024bd0dce45888f536e'
    assert sha(held)==expected==sha(BASE/'component-manifest.json')
    manifest=json.loads(held.read_text());assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed'] and manifest['nativeAcceptance'] is False
    for name,row in manifest['files'].items():
        p=BASE/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'] and p.stat().st_mode&0o777==row['mode'],name
    assert manifest['sourceSHA256']=='fee17bd9680bd2c236a624fddc80acfff25d83f275180e4db22b4fa5f04de626'==sha(ROOT/'inputs/native/xdg-origin-client.c')
    report=ROOT/'qa/review-1791128652923145237/report.json';review=json.loads(report.read_text());assert review['passed'] and review['sourceBlockerFound'] is False
    for name,row in review['files'].items():assert sha(ROOT/name)==row['sha256'] and (ROOT/name).stat().st_size==row['size'],name
    assert manifest['helperChecks']==50 and manifest['cliCases']==25 and manifest['unsafeCompiledControlsRejected']==3
    out=ROOT/'qa'/('held-review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'passed':True,'filesVerified':len(manifest['files']),'owningManifestSHA256':expected,'priorReviewSHA256':sha(report),'sourceBlockerFound':False,'nativeAcceptance':False,'scope':'Independent final held source530-file verification; review current fixture and50+25+3 existing CPU evidence; no native launch.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
    component={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'sourceBlockerFound':False,'scope':result['scope'],'owningManifestSHA256':expected,'files':files}
    target=ROOT/'component-manifest.json';assert not target.exists();target.write_text(json.dumps(component,indent=2)+'\n')
    print(json.dumps({'passed':True,'report':str(out/'report.json'),'manifestSHA256':sha(target)}))
if __name__=='__main__':main()
