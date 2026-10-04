#!/usr/bin/env python3
"""Read-only source integrity verification; no validator/native behavior run."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-geometry-client-journal-v192'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    snap=json.loads((ROOT/'source-snapshot.json').read_text());count=0
    for row in snap['sources'].values():
        p=ROOT/row['capture'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];assert sha(REPO/row['original'])==row['sha256'];count+=1
    manifest=json.loads((ROOT/'inputs/component-manifest.json').read_text());assert manifest['sourceHeld']
    for name,row in manifest['files'].items():assert sha(BASE/name)==row['sha256'] and (BASE/name).stat().st_size==row['size'];count+=1
    report=json.loads((ROOT/'inputs/qa/test-1791128646280127431/report.json').read_text());assert report['passed'] and len(report['checks'])==19 and report['nativeAcceptance'] is False
    assert report['sourceSHA256']==sha(ROOT/'inputs/journal.py')
    out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'schema':1,'passed':True,'scope':'Independent source/contract review and frozen byte/evidence integrity;19 original synthetic checks verified, no behavior rerun. Gaps documented, not full validator/native acceptance.','filesVerified':count,'findings':['per-buffer64MiB bound omitted','ACK/commit/current-generation modes not correlated','wrap oracle stale terminal header','exponent overflow can evade global nonfinite guarantee','pointer/landmark fields unvalidated','buffer/barrier ledger not reconstructed'],'nativeAcceptance':False,'behavioralRerun':False,'owningSourceSHA256':sha(ROOT/'inputs/journal.py')}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
    held={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':result['scope'],'owningManifestSHA256':sha(ROOT/'inputs/component-manifest.json'),'files':files}
    target=ROOT/'component-manifest.json';assert not target.exists();target.write_text(json.dumps(held,indent=2)+'\n')
    print(json.dumps({'passed':True,'filesVerified':count,'report':str(out/'report.json'),'manifestSHA256':sha(target)}))
if __name__=='__main__':main()
