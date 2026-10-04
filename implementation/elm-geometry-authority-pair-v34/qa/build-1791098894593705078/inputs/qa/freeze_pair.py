"""Bind the passed captured build to the exact frozen owning component."""
import hashlib
import json
import os
from pathlib import Path
import resource

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT.parents[1] / 'implementation/maximized-stack-v1/native-core-v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


report_path = sorted((ROOT / 'qa').glob('build-*/report.json'))[-1]
build = json.loads(report_path.read_text())
assert build['passed'] and not build['nativeAcceptance']
out = report_path.parent
for rel, digest in build['inputs'].items():
    assert sha(ROOT / rel) == sha(out / 'inputs' / rel) == digest, rel
for rel, digest in build['owningHeaders'].items():
    assert sha(OWNER / rel) == sha(out / 'owning-headers' / rel) == digest, rel
for path, digest in build['dependencies'].items():
    assert sha(path) == digest, path
core = build['core']
assert sha(core['path']) == core['sha256']
assert sha(core['buildReport']) == core['buildReportSHA256']
assert sha(core['componentManifest']) == core['componentManifestSHA256']
component = Path(core['inventoryBase'])
for entry in json.loads(Path(core['componentManifest']).read_text())['files']:
    p = component / entry['path']
    if 'symlink' in entry:
        assert p.is_symlink() and os.readlink(p) == entry['symlink'], str(p)
    else:
        assert not p.is_symlink() and sha(p) == entry['sha256'] and p.stat().st_size == entry['size'], str(p)
for path, digest in build['coreDependencies'].items(): assert sha(path) == digest, path
for path, digest in build['linkedLibraries'].items(): assert sha(path) == digest, path
assert sha(build['linkClosureReport']) == build['linkClosureReportSHA256']
assert sha(build['coreClosureReport']) == build['coreClosureReportSHA256']
assert sha(build['binary']) == build['binarySHA256']
assert sha(build['inheritedBuildReport']) == build['inheritedBuildReportSHA256']
upstream = json.loads((ROOT / 'upstream.json').read_text())
parent = Path(upstream['parent'])
assert sha(parent / 'qa/build-pair-manifest.json') == upstream['parentPairManifestSHA256']
for rel, digest in build['inheritedFiles'].items():
    local = ROOT / upstream['inheritedPaths'][rel]
    assert sha(parent / rel) == sha(local) == digest, rel
descriptor = ROOT / 'native-build-report.json'
assert not descriptor.exists(), 'Do not overwrite an exact pair descriptor'
core_descriptor = json.loads((ROOT / 'core-build-report.json').read_text())
pair_descriptor = dict(core_descriptor)
pair_descriptor.update(scope='Exact owning core/rebuilt unchanged authority compile tuple only',
                       nativeAcceptance=False, installed=False,
                       plugin={'path': build['binary'], 'sha256': build['binarySHA256']},
                       pluginBuildReport=str(report_path), pluginBuildReportSHA256=sha(report_path),
                       linkClosureReport=build['linkClosureReport'], linkClosureReportSHA256=build['linkClosureReportSHA256'],
                       coreComponentManifest=core['componentManifest'],
                       coreComponentManifestSHA256=core['componentManifestSHA256'])
descriptor.write_text(json.dumps(pair_descriptor, indent=2) + '\n')
target = ROOT / 'qa/build-pair-manifest.json'
assert not target.exists(), 'Do not overwrite a frozen pair'
manifest = {'schema': 1, 'passed': True, 'scope': 'Exact captured owning binary/plugin compile tuple only',
            'nativeAcceptance': False, 'parentPresentationQualified': False, 'releaseAcceptance': False,
            'nativePair': {'core': core, 'plugin': {'path': build['binary'], 'sha256': build['binarySHA256']}},
            'buildReport': str(report_path.relative_to(ROOT)), 'buildReportSHA256': sha(report_path),
            'upstreamSHA256': sha(ROOT / 'upstream.json'),
            'files': {str(p.relative_to(ROOT)): sha(p) for p in sorted(ROOT.rglob('*'))
                      if p.is_file() and not p.is_symlink() and p != target}}
target.write_text(json.dumps(manifest, indent=2) + '\n')
print(target, flush=True)
