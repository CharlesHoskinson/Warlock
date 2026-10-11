"""Protected manifest rebuild and actual consumed-input tamper negatives."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
import release_builder as builder

OUT = ROOT / 'qa/runs' / ('release-input-lock-' + str(time.time_ns()))
OUT.mkdir(parents=True)
report = {'passed': False, 'requirements': ['ELM-DEL-003'], 'scenarios': ['delivery-003'],
          'nativeAcceptance': False, 'fullReleaseAccepted': False, 'checks': []}

def check(name, condition):
    report['checks'].append({'name': name, 'passed': bool(condition)})
    assert condition, name

try:
    lock = builder.capture(ROOT.parents[1])
    original_lock = OUT / 'build-lock.json'
    original_lock.write_text(json.dumps(lock, indent=2) + '\n')
    check('OriginalInputLockVerifies', builder.verify(lock) == len(lock['inputs']))
    # One fresh source snapshot for a real build and reversible consumed-source
    # negatives. No candidate sources or external compiler/header files mutate.
    snapshot = OUT / 'input-candidate'; snapshot.mkdir()
    relocated = copy.deepcopy(lock)
    source_paths = {str(ROOT / name): str(snapshot / name) for name in lock['sources']}
    for old, new in source_paths.items():
        target = Path(new); target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
        row = relocated['inputs'].pop(old)
        row['resolved'] = str(target.resolve()); relocated['inputs'][new] = row
    relocated['candidate'] = str(snapshot)
    relocated['hostDependencies'] = sorted(source_paths.get(p, p) for p in lock['hostDependencies'])
    (OUT / 'relocated-build-lock.json').write_text(json.dumps(relocated, indent=2) + '\n')
    check('FreshRelocatedSourceSnapshotVerifies', builder.verify(relocated) == len(lock['inputs']))
    built = builder.build(relocated, OUT / 'build')
    check('ManifestBuildCompleted', built['passed'])
    check('AllThreeCompiledProductionAssetsMatch', all(
        built['compiledAssets'][name] == builder.sha(ROOT / 'assets' / name)
        for name in ('elm.js', 'bar.js', 'popup.js')))
    check('DirectCompiledReducerRegressionPasses', len(built['typedChecks']) == 19
          and all(built['typedChecks'].values()))
    check('CurrentExactNativePairRetained', all(builder.sha(OUT / 'build/package' /
          built['packageManifest']['nativePair'][role]['path']) == row['sha256']
          for role, row in lock['nativePair'].items()))
    pointer = builder.read(ROOT / 'qa/current-search-build.json')
    prior = builder.read(ROOT.parents[1] / pointer['report'])
    check('RebuiltHostMatchesQualifiedArtifactBytes', built['hostSHA256'] == prior['binarySHA256'])
    check('ArchiveAndEmbeddedPayloadManifestExist', builder.sha(OUT / 'build/warlock-candidate.tar') == built['archiveSHA256']
          and builder.read(OUT / 'build/package/MANIFEST.json') == built['packageManifest'])
    check('RequiredAquamarineLoaderAliasRetained', all(
          (OUT / 'build/package/native' / alias).is_symlink()
          and os.readlink(OUT / 'build/package/native' / alias) == target
          for alias, target in lock['loaderAliases'].items()))
    altered = snapshot / 'src/Main.elm'; before = altered.read_bytes()
    altered.write_bytes(before + b'\n// altered locked build dependency\n')
    refused = False
    try:
        builder.build(relocated, OUT / 'must-not-build')
    except builder.ChangedInput as error:
        refused = str(altered) in str(error)
        report['alteredDependencyOutcome'] = str(error)
    finally:
        altered.write_bytes(before)
    check('AlteredActualBuildSourceRefused', refused and not (OUT / 'must-not-build').exists())
    check('RestoredDependencyVerifiesWithoutRebaseline', builder.verify(relocated) == len(lock['inputs']))
    # A byte-identical alias still must resolve to the recorded artifact. This
    # protects tool/library symlink selection, separately from SHA comparisons.
    alias = OUT / 'tool-alias'; alias.symlink_to('/usr/bin/python3')
    alias_lock = copy.deepcopy(relocated)
    builder.add(alias_lock['inputs'], alias, 'test-alias')
    # Use a private byte copy to prove changed identity even when its hash is
    # identical; no installed tool or symlink changes.
    same_bytes = OUT / 'same-tool-bytes'; shutil.copyfile('/usr/bin/python3', same_bytes)
    alias.unlink(); alias.symlink_to(same_bytes)
    refused = False
    try:
        builder.verify(alias_lock)
    except builder.ChangedInput as error:
        refused = str(alias) in str(error)
    check('ChangedArtifactAliasRefusedEvenWithSameBytes', refused)
    report.update(passed=True, inputCount=len(lock['inputs']),
        originalLockSHA256=builder.sha(original_lock), relocatedLockSHA256=builder.sha(OUT / 'relocated-build-lock.json'),
        builderSHA256=builder.sha(ROOT / 'adapter/release_builder.py'),
        rebuiltHostSHA256=built['hostSHA256'], compiledAssets=built['compiledAssets'],
        archiveSHA256=built['archiveSHA256'], packageManifest=built['packageManifest'],
        nativePair=lock['nativePair'], toolVersions=lock['tools'],
        scope='Fixed manifest rebuild of three production Elm roots and all eleven native host units, native self-tests and compiled reducer; retained core/plugin artifacts and actual consumed-source/alias tamper refusal. No complete upstream source-provenance, offline clean reproducibility, native GUI or redistribution acceptance.',
        missingObservations=lock['missingObservations'] + ['Independent original-scenario review.'])
except Exception as error:
    report.update(error=repr(error), traceback=traceback.format_exc())
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
