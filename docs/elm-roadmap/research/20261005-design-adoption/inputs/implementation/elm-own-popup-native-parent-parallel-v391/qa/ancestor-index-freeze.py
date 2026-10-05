import hashlib,json,os,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
out=ROOT/'qa'/('freeze-targeted-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'nativeAcceptance':False}
try:
    test=pathlib.Path(sys.argv[1]).resolve();targeted=pathlib.Path(sys.argv[2]).resolve();origin_report=pathlib.Path(sys.argv[3]).resolve();adoption_report=pathlib.Path(sys.argv[4]).resolve()
    assert all(p.is_relative_to(ROOT/'qa') for p in (test,targeted,origin_report,adoption_report))
    a=json.loads(test.read_bytes());b=json.loads(targeted.read_bytes());c=json.loads(origin_report.read_bytes());adopt=json.loads(adoption_report.read_bytes());assert adopt['passed'] and adopt['nativeAcceptance'] is False and len(adopt['checks'])==13
    for p,digest in adopt['inputs'].items():assert sha(p)==digest
    assert c['passed'] and c['nativeAcceptance'] is False and len(c['checks'])==31
    for p,digest in c['inputs'].items():assert sha(p)==digest
    assert a['passed'] and len(a['checks'])==35 and b['passed'] and not b['nativeAcceptance']
    for rel,digest in a['inputs'].items():assert sha(ROOT/rel)==digest
    for rel,digest in b['sourceInputs'].items():assert sha(ROOT/rel)==digest
    external={}
    review_pin=json.loads((ROOT/'index-review-pin.json').read_bytes());review=pathlib.Path(review_pin['manifest']);assert sha(review)==review_pin['sha256'];review_held=json.loads(review.read_bytes());assert review_held['sourceHeld'] and review_held['evidenceIntegrityPassed'];external[str(review)]={'sha256':review_pin['sha256']}
    for rel,row in review_held['files'].items():assert sha(review.parent/rel)==row['sha256'];external[str(review.parent/rel)]={'sha256':row['sha256']}
    for p,row in review_held.get('externalFiles',{}).items():
        if type(row) is str:row={'sha256':row}
        if 'symlink' in row:assert os.readlink(p)==row['symlink'];external[p]={'symlink':row['symlink']}
        else:assert sha(p)==row['sha256'];external[p]={'sha256':row['sha256']}
    for rel,target in review_held.get('symlinks',{}).items():assert os.readlink(review.parent/rel)==target
    for p,digest in c['proof']['files'].items():assert sha(p)==digest;external[p]={'sha256':digest}
    for name,digest in [('elm-own-popup-runtime-index-guard-v364','4d940d15d8f1cfe24d60c927939fdf9b9f5d5c7b0a778211992f067c43d9e1b6'),('elm-own-popup-parallel-guard-review-v352','881534cfb79598d7a6ffd9ff18ef32dd644558d0f33de74178391ece05c54de9')]:
        base=ROOT.parent/name;manifest=base/'component-manifest.json';assert sha(manifest)==digest;held=json.loads(manifest.read_bytes());assert held['sourceHeld'] and held['evidenceIntegrityPassed'];external[str(manifest)]={'sha256':digest}
        for rel,row in held['files'].items():assert sha(base/rel)==row['sha256'];external[str(base/rel)]={'sha256':row['sha256']}
        for rel,target in held.get('symlinks',{}).items():assert os.readlink(base/rel)==target
    for section in ('externalFiles','guardFiles'):
        for p,digest in b[section].items():assert sha(p)==digest;external[p]={'sha256':digest}
    origin=json.loads((ROOT/'targeted-origin.json').read_bytes())
    for name,key in ((pathlib.Path(origin['ancestor']).name,'manifestSHA256'),('elm-own-popup-native-mapping-runner-review-v339','reviewManifestSHA256'),('elm-own-popup-native-boot-deadline-v342','failureManifestSHA256')):
        base=ROOT.parent/name;p=base/'component-manifest.json';assert sha(p)==origin[key]
        external[str(p)]={'sha256':sha(p)};m=json.loads(p.read_bytes());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
        for rel,row in m['files'].items():assert sha(base/rel)==row['sha256'];external[str(base/rel)]={'sha256':row['sha256']}
    files={};links={}
    for p in sorted(ROOT.rglob('*')):
        if p.is_symlink():links[str(p.relative_to(ROOT))]=os.readlink(p)
        elif p.is_file() and p.name!='component-manifest.json':files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
    m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'scope':'V364 per-call indexed full guards with verified stdlib source/cache/loaded-code origins and exact original V345 native body, targeted144-library host; native boot deadline and fatal worker cleanup unqualified','files':files,'symlinks':links,'externalFiles':external,'testReport':str(test),'testReportSHA256':sha(test),'targetedReport':str(targeted),'targetedReportSHA256':sha(targeted),'runtimeGuardManifestSHA256':'4d940d15d8f1cfe24d60c927939fdf9b9f5d5c7b0a778211992f067c43d9e1b6','parallelGuardReviewManifestSHA256':'881534cfb79598d7a6ffd9ff18ef32dd644558d0f33de74178391ece05c54de9','originReport':str(origin_report),'originReportSHA256':sha(origin_report),'verifiedRuntimeOrigins':c['proof'],'indexReviewManifestSHA256':review_pin['sha256'],'adoptionReport':str(adoption_report),'adoptionReportSHA256':sha(adoption_report)}
    (ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    r.update(passed=True,ownFiles=len(files),externalFiles=len(external),manifestSHA256=sha(ROOT/'component-manifest.json'))
except BaseException as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(not r['passed'])
