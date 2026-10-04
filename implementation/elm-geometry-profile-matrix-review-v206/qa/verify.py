#!/usr/bin/env python3
"""Protected independent source/plan/pin review; no native execution."""
from pathlib import Path
import ast,collections,hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-geometry-feasible-bounds-native-v204'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    snap=json.loads((ROOT/'source-snapshot.json').read_text());count=0
    for name,row in snap['sources'].items():
        p=ROOT/row['capture'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size'] and sha(REPO/name)==row['sha256'];count+=1
    manifest=BASE/'component-manifest.json';assert sha(manifest)=='909dbbf0c2b0b12c80829e205942fa5412063fbd7802ff857d49735f36299cd3'
    held=json.loads(manifest.read_text());assert held['sourceHeld'] and held['nativeAcceptance'] is False
    for name,row in held['files'].items():
        p=BASE/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'] and p.stat().st_mode&0o777==row['mode'];count+=1
    old=ROOT/'inputs/implementation/elm-geometry-xdg-origin-native-v196/qa/native.py';current=ROOT/'inputs/implementation/elm-geometry-feasible-bounds-native-v204/qa/native.py'
    assert sha(current)=='ca4b37efeaba17152b834c3faa8913c6cfaba1f5775fe9dfdf55adb4c06d8c2a'
    def checks(p):return collections.Counter(ast.dump(n.args[0],include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check' and n.args)
    assert not (checks(old)-checks(current))
    plan=ROOT/'inputs/implementation/elm-geometry-feasible-bounds-native-v204/profiles.json';original=ROOT/'inputs/implementation/elm-geometry-feasible-bounds-profiles-v201/profiles.json';assert plan.read_bytes()==original.read_bytes()
    profiles=json.loads(plan.read_text())['profiles'];assert len(profiles)==22 and len({p['id'] for p in profiles})==22
    groups={}
    for p in profiles:groups.setdefault((tuple(p['physicalMode']),p['monitorScale']),[]).append(p['id'])
    assert {k:len(v) for k,v in groups.items()}=={((800,600),1):14,((1600,1200),2):6,((800,600),2):2}
    expected={f'{kind}-scale{scale}' for kind in ['zero','origin','finite','fixed'] for scale in [1,2]};assert {p['id'] for p in profiles if p['retainedBaseline']}==expected
    report_path=BASE/'qa/preflight-1791131747546279221/report.json';preflight=json.loads(report_path.read_text());assert preflight['passed'] and not preflight['nativeAcceptance']
    for name,digest in preflight['inputs'].items():assert sha(Path(name))==digest;count+=1
    for name,digest in preflight['artifacts'].items():assert sha(report_path.parent/name)==digest;count+=1
    assert held['acceptedPreflightSHA256']==sha(report_path)
    out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'passed':True,'kind':'independent-held-expanded-runner-source-review','filesVerified':count,'sourceBlockerFound':False,'owningManifestSHA256':sha(manifest),'owningSourceSHA256':sha(current),'original196CheckIdentitiesPreserved':True,'planProfiles':22,'sessionProfileCounts':[14,6,2],'nativeAcceptance':False,'nativeRerun':False,'scope':'Exact source/oracle/plan/current435-AQ155 preflight closure review only; no native22-profile result yet.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    target=ROOT/'component-manifest.json';assert not target.exists()
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
    target.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceBlockerFound':False,'nativeAcceptance':False,'owningManifestSHA256':sha(manifest),'scope':result['scope'],'files':files},indent=2)+'\n')
    print(json.dumps({'passed':True,'filesVerified':count,'report':str(out/'report.json'),'manifestSHA256':sha(target)}))
if __name__=='__main__':main()
