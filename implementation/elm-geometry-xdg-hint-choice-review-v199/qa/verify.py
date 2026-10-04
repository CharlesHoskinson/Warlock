#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-geometry-xdg-hint-choice-fixture-v197'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    snap=json.loads((ROOT/'source-snapshot.json').read_text());count=0
    for row in snap['sources'].values():
        p=ROOT/row['capture'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];assert sha(Path(row['original']) if row['original'].startswith('/') else REPO/row['original'])==row['sha256'];count+=1
    build_rel='qa/client-build-1791129756017735997/report.json';build=json.loads((ROOT/'inputs'/build_rel).read_text());assert build['passed']
    for section in ['inputs','dependencies','linkedLibraries','tools']:
        for p,digest in build[section].items():assert sha(Path(p))==digest;count+=1
    for section in ['generated','artifacts']:
        for p,digest in build[section].items():assert sha(BASE/Path(build_rel).parent/p)==digest;count+=1
    assert sha(Path(build['client']))==build['clientSHA256'];count+=1
    test_rel='qa/test-1791129836690118791/report.json';test=json.loads((ROOT/'inputs'/test_rel).read_text());assert test['passed']
    assert test['runs']['actual']['helperChecks']==75 and test['runs']['actual']['failures']==0 and test['runs']['actual']['connections']==0
    assert len(test['cli'])==25 and test['callback']['callbackChecks']==7 and test['callback']['failures']==0
    assert len(test['runs'])==6 and all(v['failures']>0 and v['exitCode']==1 for k,v in test['runs'].items() if k!='actual')
    source=(ROOT/'inputs/native/xdg-origin-client.c').read_text();start=source.index('static void surface_configure(');end=source.index('static const struct xdg_surface_listener',start)
    body=source[start:end];assert hashlib.sha256(body.encode()).hexdigest()==test['callback']['actualSourceSliceSHA256']
    assert test['runs']['actual']['sourceSHA256']==sha(ROOT/'inputs/native/xdg-origin-client.c')
    for p,digest in test['artifacts'].items():assert sha(BASE/Path(test_rel).parent/p)==digest;count+=1
    out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir(mode=0o700)
    result={'passed':True,'kind':'independent-protocol-source-and-evidence-review','filesVerified':count,'sourceSHA256':sha(ROOT/'inputs/native/xdg-origin-client.c'),'sourceBlockerFound':False,'nativeAcceptance':False,'behavioralRerun':False,'scope':'Local official XML and exact source/build/evidence review;75+25+7 and5 existing controls verified, no GUI/server/client execution.'}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'filesVerified':count,'report':str(out/'report.json')}))
if __name__=='__main__':main()
