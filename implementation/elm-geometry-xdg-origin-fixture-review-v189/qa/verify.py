#!/usr/bin/env python3
"""Independent integrity/lineage review only; no client execution or GUI."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    snap=json.loads((ROOT/'snapshot.json').read_text());count=0
    for row in snap['sources'].values():
        p=ROOT/row['capture'];assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'];count+=1
    rel='qa/client-build-1791128443207969331/report.json'
    build=json.loads((ROOT/'inputs'/rel).read_text());assert build['passed']
    base=REPO/'implementation/elm-geometry-xdg-origin-fixture-v184'
    build_packet=base/Path(rel).parent
    for section in ['inputs','dependencies','linkedLibraries','tools']:
        for path,digest in build[section].items():assert sha(Path(path))==digest,(section,path);count+=1
    for section in ['generated','artifacts']:
        for path,digest in build[section].items():assert sha(build_packet/path)==digest,(section,path);count+=1
    assert sha(Path(build['client']))==build['clientSHA256'];count+=1
    assert build['inputs'][str(base/'native/xdg-origin-client.c')]==snap['sources']['native/xdg-origin-client.c']['sha256']
    rel='qa/test-1791128474911399590/report.json';test=json.loads((ROOT/'inputs'/rel).read_text());assert test['passed']
    assert test['runs']['actual']['helperChecks']==50 and test['runs']['actual']['failures']==0 and test['runs']['actual']['connections']==0
    assert len(test['cli'])==25
    assert len(test['runs'])==4 and all(row['failures']>0 and row['exitCode']==1 for name,row in test['runs'].items() if name!='actual')
    assert test['runs']['actual']['sourceSHA256']==snap['sources']['native/xdg-origin-client.c']['sha256']
    for name,digest in test['artifacts'].items():assert sha(base/Path(rel).parent/name)==digest;count+=1
    assert json.loads((ROOT/'inputs/qa/test-1791128172404075843/report.json').read_text())['passed'] is False
    files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and 'review-' not in str(p.relative_to(ROOT))}
    out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    report={'schema':1,'passed':True,'kind':'independent-source-evidence-integrity-review','filesVerified':count,'sourceSHA256':snap['sources']['native/xdg-origin-client.c']['sha256'],'files':files,'sourceBlockerFound':False,'nativeAcceptance':False,'scope':'Exact final-owner-stable source, actual build/dependency/library/artifact lineage and existing50+25+3 CPU evidence; no behavior rerun or GUI.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'filesVerified':count,'report':str(out/'report.json')}))
if __name__=='__main__':main()
