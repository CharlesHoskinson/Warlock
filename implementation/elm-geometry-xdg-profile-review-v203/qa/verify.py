#!/usr/bin/env python3
"""Independent original native evidence/hash review; no GUI or source mutation."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    snap=json.loads((ROOT/'source-snapshot.json').read_text());count=0
    for name,row in snap['sources'].items():
        p=ROOT/row['capture'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];assert sha(REPO/name)==row['sha256'];count+=1
    selected='implementation/elm-geometry-xdg-origin-native-v196/qa/native-1791130292488706555/report.json'
    r=json.loads((ROOT/'inputs'/selected).read_text());assert r['passed'] and r['cleanupPassed'] and len(r['checks'])==144 and all(c['passed'] for c in r['checks'])
    assert not r['profileCleanupErrors'] and not r['finalCleanupErrors']
    assert len(r['profiles'])==12 and {p['name'] for p in r['profiles']}=={f'{kind}-scale{scale}' for kind in ['zero','origin','finite','fixed'] for scale in [1,2]}
    receipts={c['name']:c['receipt'] for c in r['checks'] if ':exactGeometryReceipt' in c['name']}
    for name,receipt in receipts.items():
        expected='applied' if name.startswith('zero') else 'geometry-size-infeasible' if name.startswith('finite') else 'geometry-ineligible'
        assert receipt['reason']==expected and receipt['status']==('Committed' if expected=='applied' else 'Refused')
    for profile in r['profiles']:
        fact=profile['facts']['facts']['windows'][0];inputs=fact['sizePolicy']['inputs'];b=profile['buffer'];scale=profile['profile'][-1]
        assert b['scale']==scale and b['bufferSize']==[x*scale for x in b['surfaceSize']]
        if inputs is not None:assert inputs['monitorScale']==1
        if profile['name'].startswith('fixed'):assert fact['fixedSize'] and inputs is None and fact['sizePolicy']['maximize'] is None
        if profile['name'].startswith('origin'):assert inputs['geometryOrigin']==[16,24] and not fact['geometryEligible'] and fact['sizePolicy']['maximize'] is None
        if profile['name'].startswith('finite'):assert fact['geometryEligible'] and not fact['capabilities']['maximize'] and inputs['rawMaximum']==[400,300]
    for scale in [1,2]:
        seq=[p for p in r['profiles'] if p['name']==f'zero-scale{scale}']
        assert [p['native']['at']+p['native']['size'] for p in seq]==[[-1,-1,800,600],[1,1,798,598],[-1,-1,800,600]]
    evidence_rel='implementation/elm-geometry-xdg-profile-evidence-v202/qa/verify-1791130383980150570/report.json'
    evidence=json.loads((ROOT/'inputs'/evidence_rel).read_text());assert evidence['evidenceIntegrityPassed'] and evidence['checks']==144
    for path,row in evidence['files'].items():
        p=Path(path);assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];count+=1
    old=json.loads((ROOT/'inputs/implementation/elm-geometry-xdg-origin-native-v190/qa/native-1791129297579795954/report.json').read_text());assert not old['passed']
    out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'passed':True,'kind':'bounded-native-evidence-independent-review','filesVerified':count,'checksInOriginalNativeReport':144,'profiles':8,'observationSnapshots':12,'cleanupPassed':True,'sourceOraclesReviewed':True,'originalReportSHA256':sha(ROOT/'inputs'/selected),'nativeRerun':False,'fullNativeAcceptance':False,'pixelAcceptance':False,'physicalInputAcceptance':False,'monitorScale2Acceptance':False,'GTKAcceptance':False,'releaseAcceptance':False,'scope':'Actual bounded196 evidence/oracles and202 integrity reviewed; no behavior/GUI rerun. Original190 failure retained.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    target=ROOT/'component-manifest.json';assert not target.exists()
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
    target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedNativeEvidenceReviewed':True,'fullNativeAcceptance':False,'nativeRerun':False,'scope':result['scope'],'files':files},indent=2)+'\n')
    print(json.dumps({'passed':True,'filesVerified':count,'manifestSHA256':sha(target),'report':str(out/'report.json')}))
if __name__=='__main__':main()
