import hashlib,json,pathlib,resource,stat,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OWNER=ROOT.parent/'elm-own-popup-runtime-closure-guard-v334'
OLD=ROOT.parent/'elm-own-popup-runtime-closure-guard-v330'
PIN='e0bcfefdd82d137518b179cbce261fe38912a155e54956b44efd97ca54c66e90'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'nativeAcceptance':False,'scope':'Independent source/CPU guard review only'}
sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'qa/verify.py',ROOT/'REVIEW.md',ROOT/'REQUIREMENTS.md']}
try:
 p=OWNER/'component-manifest.json';assert sha(p)==PIN;m=json.loads(p.read_text());assert m['sourceHeld'] is True and m['evidenceIntegrityPassed'] is True
 for rel,row in m['files'].items():
  q=pathlib.Path(rel);assert not q.is_absolute() and '..' not in q.parts
  p=OWNER/q;assert p.is_file() and not p.is_symlink()
  assert sha(p)==row['sha256'] and p.stat().st_size==row['size'] and oct(stat.S_IMODE(p.stat().st_mode))==row['mode']
 old=json.loads(pathlib.Path(json.loads((OLD/'component-manifest.json').read_text())['testReport']).read_text())
 test=pathlib.Path(m['testReport']);e=json.loads(test.read_text());assert e['passed'] is True and len(e['checks'])==43 and len(e['mutants'])==5 and all(v['killed'] for v in e['mutants'])
 assert set(old['checks'])-set(e['checks'])=={'conflicting inode'}
 assert 'ambiguous required artifact mapping' in e['checks']
 for source,digest in e['inputs'].items():assert sha(pathlib.Path(source))==digest
 for rel,digest in e['artifacts'].items():assert sha(test.parent/rel)==digest
 for p,digest in e['tuple']['libraries'].items():assert sha(pathlib.Path(p))==digest
 for p,digest in e['tuple']['artifacts'].items():assert sha(pathlib.Path(p))==digest
 assert len(e['tuple']['libraries'])==171
 (out/'guard.py').write_bytes((OWNER/'guard.py').read_bytes());(out/'test.py').write_bytes((OWNER/'qa/test.py').read_bytes())
 child=subprocess.run([sys.executable,'-B',str(out/'test.py'),'--exercise',str(out/'guard.py')],capture_output=True,timeout=30)
 (out/'stdout').write_bytes(child.stdout);(out/'stderr').write_bytes(child.stderr);assert child.returncode==0,child.stderr
 cases=json.loads(child.stdout);assert cases==e['checks']
 assert sha(OWNER/'component-manifest.json')==PIN
 for rel,digest in sources.items():assert sha(ROOT/rel)==digest
 r.update(passed=True,ownerManifestSHA256=PIN,ownerFiles=len(m['files']),reproducedCases=len(cases),original330Cases=len(old['checks']),pinnedLibraries=171,ownerMutantsVerified=5)
except BaseException as error:r['error']=repr(error)
r['reviewInputs']=sources;(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 rows={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))} for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='component-manifest.json'}
 (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'ownerManifestSHA256':PIN,'verificationReport':str(out/'report.json'),'verificationReportSHA256':sha(out/'report.json'),'files':rows},indent=2)+'\n')
print(out/'report.json');raise SystemExit(not r['passed'])
