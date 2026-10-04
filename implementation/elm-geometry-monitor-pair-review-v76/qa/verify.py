"""Independent protected, read-only closure review of the V75/V73 tuple."""
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope

require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PAIR = REPO / 'implementation/elm-geometry-monitor-owning-pair-v75'
OUT = ROOT / 'qa' / ('review-' + str(time.time_ns()))
OUT.mkdir(mode=0o700)
report = {'passed': False, 'nativeAcceptance': False, 'releaseAcceptance': False,
          'scope': 'Independent current byte integrity and strong-symbol report linkage; no loading or ABI behavioral acceptance',
          'verified': {}}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(path, wanted):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    assert sha(path) == wanted, str(path)
    report['verified'][str(path)] = wanted

def load(path, wanted=None):
    if wanted is not None:
        verify(path, wanted)
    return json.loads(Path(path).read_text())

try:
    descriptor_path = PAIR / 'native-build-report.json'
    descriptor = load(descriptor_path)
    verify(descriptor_path, sha(descriptor_path))
    assert descriptor['result'] == 'pass' and descriptor['nativeAcceptance'] is False
    plugin_report_path = Path(descriptor['pluginBuildReport'])
    plugin = load(plugin_report_path, descriptor['pluginBuildReportSHA256'])
    assert plugin['passed'] and plugin['nativeAcceptance'] is False
    verify(descriptor['plugin']['path'], descriptor['plugin']['sha256'])
    assert plugin['binary'] == descriptor['plugin']['path']
    assert plugin['binarySHA256'] == descriptor['plugin']['sha256']
    assert plugin['core']['path'] == descriptor['binary']
    assert plugin['core']['sha256'] == descriptor['sha256']
    core_path = Path(descriptor['buildReport'])
    core = load(core_path, descriptor['buildReportSHA256'])
    assert plugin['core']['buildReport'] == str(core_path)
    assert plugin['core']['buildReportSHA256'] == descriptor['buildReportSHA256']
    assert core['passed'] and core['binary'] == descriptor['binary']
    assert core['binarySHA256'] == descriptor['sha256']
    verify(core['binary'], core['binarySHA256'])
    manifest_path = Path(descriptor['coreComponentManifest'])
    manifest = load(manifest_path, descriptor['coreComponentManifestSHA256'])
    assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed']
    assert manifest['nativeAcceptance'] is False and manifest['releaseAcceptance'] is False
    assert manifest['buildReport'] == str(core_path)
    for relative, row in manifest['files'].items():
        path = manifest_path.parent / relative
        verify(path, row['sha256'])
        assert path.stat().st_size == row['size'], relative
    upstream = load(PAIR / 'upstream.json')
    assert upstream == plugin['sourceLineage']
    assert upstream['coreComponent'] == str(manifest_path.parent)
    assert upstream['coreManifestSHA256'] == descriptor['coreComponentManifestSHA256']
    parent = Path(upstream['parent'])
    verify(parent / 'native-build-report.json', upstream['parentDescriptorSHA256'])
    for relative, wanted in upstream['sourceFiles'].items():
        for base in [parent, PAIR, plugin_report_path.parent / 'inputs']:
            verify(base / relative, wanted)
    for relative, wanted in plugin['inputs'].items():
        verify(PAIR / relative, wanted)
        verify(plugin_report_path.parent / 'inputs' / relative, wanted)
    assert plugin['owningHeaders'] == core['owningHeaders']
    assert len(core['owningHeaders']) == 694
    for relative, wanted in core['owningHeaders'].items():
        verify(core_path.parent / 'owning-headers' / relative, wanted)
        verify(plugin_report_path.parent / 'owning-headers' / relative, wanted)
    for path, wanted in core['retainedPolicyHeaders'].items():
        verify(path, wanted)
        name = Path(path).name
        assert plugin['inheritedPolicies'][name] == wanted
        verify(plugin_report_path.parent / 'inputs/candidate' / name, wanted)
    for data in [core, plugin]:
        for section in ['dependencies', 'tools', 'linkedLibraries']:
            for path, wanted in data[section].items():
                verify(path, wanted)
    for path, wanted in core['linkDependencies'].items():
        verify(path, wanted)
    for relative, wanted in plugin['artifacts'].items():
        verify(plugin_report_path.parent / relative, wanted)
    closure = load(descriptor['linkClosureReport'], descriptor['linkClosureReportSHA256'])
    assert closure['passed'] and closure['nativeAcceptance'] is False
    assert closure['core'] == plugin['core']
    assert closure['plugin'] == descriptor['plugin']
    assert closure['strongUndefinedCount'] == plugin['strongUndefinedCount'] == 152
    assert closure['missingSymbols'] == plugin['missingSymbols'] == []
    assert closure['linkedLibraries'] == plugin['linkedLibraries']
    verify(PAIR / 'PAIR.md', sha(PAIR / 'PAIR.md'))
    inventory = {}
    for path in sorted(PAIR.rglob('*')):
        if path.is_file() and not path.is_symlink():
            inventory[str(path.relative_to(PAIR))] = {
                'sha256': sha(path), 'size': path.stat().st_size}
    report['pairInventory'] = inventory
    report.update(passed=True, descriptor=str(descriptor_path),
                  descriptorSHA256=sha(descriptor_path), coreManifestFiles=len(manifest['files']),
                  owningHeaders=694, strongUndefinedResolved=152,
                  pluginBuildReport=str(plugin_report_path), pluginBuildReportSHA256=sha(plugin_report_path))
except Exception as error:
    report['error'] = repr(error)
report['reviewerSourceSHA256'] = sha(__file__)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'),
                  'verifiedFiles': len(report['verified']), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
