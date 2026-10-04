import hashlib, json, resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
buildPath = ROOT/'qa/build-1791152783542475489/report.json'
testPath = ROOT/'qa/test-1791152885205658250/report.json'
b = json.loads(buildPath.read_text()); t = json.loads(testPath.read_text())
assert b['passed'] and t['passed'] and not b['nativeAcceptance'] and not t['nativeAcceptance']
assert len(b['owningHeaders']) == 694 and not b['missingSymbols']
assert len(t['mutants']) == 4 and all(x['killed'] and x['exitCode'] != 0 for x in t['mutants'])
assert sha(b['binary']) == b['binarySHA256']
assert b['core']['sha256'] == 'bda6ce0094961c285673589afa2b61fe2b97321a1d86b248823b482122fec0f5'
for rel, digest in b['inputs'].items(): assert sha(ROOT/rel) == digest
for name, digest in t['inputs'].items(): assert sha(name) == digest
external = {}
for r, base in [(b, buildPath.parent), (t, testPath.parent)]:
    for rel, digest in r['artifacts'].items(): assert sha(base/rel) == digest
    for section in ['dependencies', 'linkedLibraries', 'tools']:
        for path, digest in r.get(section, {}).items():
            assert sha(path) == digest
            if not Path(path).is_relative_to(ROOT): external[path] = digest
core = b['core']
for pathKey, digestKey in [('path','sha256'), ('buildReport','buildReportSHA256'), ('componentManifest','componentManifestSHA256')]:
    assert sha(core[pathKey]) == core[digestKey]
    external[core[pathKey]] = core[digestKey]
files = {str(p.relative_to(ROOT)): {'sha256':sha(p), 'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p.name != 'component-manifest.json'}
result = {'sourceHeld':True, 'evidenceIntegrityPassed':True, 'nativeAcceptance':False, 'installed':False,
          'scope':'Read-only bounded full live surface census source/build/budget controls; no blocker grant/production transport/native execution',
          'buildReport':str(buildPath), 'buildReportSHA256':sha(buildPath), 'testReport':str(testPath), 'testReportSHA256':sha(testPath),
          'files':files, 'external':external}
p = ROOT/'component-manifest.json'
assert not p.exists()
p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'held':True,'manifest':str(p),'sha256':sha(p),'files':len(files),'external':len(external),'nativeAcceptance':False}))
