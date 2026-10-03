"""Freeze V9 coverage provenance after offline regression. Never runs GPU code."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
from verify_quantized_over import shader_digests

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    target, checkpoint = HERE / 'manifest-v9.json', HERE / 'checkpoint-v9.json'
    if target.exists() or checkpoint.exists():
        raise SystemExit('fresh immutable freeze destination required')
    inputs, modes, links = {}, {}, {}
    def add(path, expected=None):
        path = Path(os.path.abspath(path))
        if not path.is_file():raise SystemExit('required regular input absent: '+str(path))
        digest = sha(path)
        if expected is not None and digest != expected:raise SystemExit('immutable input changed: '+str(path))
        for name in (path,path.resolve()):
            inputs[str(name)] = digest
            modes[str(name)] = stat.S_IMODE(name.stat().st_mode)
        for name in (path,*path.parents):
            if name.is_symlink():links[str(name)] = os.readlink(name)
    inherited_path = BASE / 'producer-default-readback-v8/manifest-v8.json'
    inherited = json.loads(inherited_path.read_text())
    if len(inherited['inputs']) != 1418:raise SystemExit('unexpected frozen V8 closure')
    for filename, digest in inherited['inputs'].items():
        add(filename,digest)
        if stat.S_IMODE(Path(filename).stat().st_mode)!=inherited['inputModes'][filename]:raise SystemExit('inherited V8 mode changed: '+filename)
    for filename,target_link in inherited['links'].items():
        if os.readlink(filename)!=target_link:raise SystemExit('inherited V8 link changed: '+filename)
    add(inherited_path);add(inherited_path.with_name('checkpoint-v8.json'))
    attribution_path = BASE / 'raster-attribution-v8/retained-v8-prefix-attribution.json'
    attribution = json.loads(attribution_path.read_text())
    for filename,digest in attribution['inputs'].items():add(filename,digest)
    for path in (BASE / 'raster-attribution-v8').iterdir():
        if path.is_file():add(path)
    for directory in ('family-raster-oracle-v6/attempt-private-1','family-raster-sampler-v8/attempt-1'):
        evidence = Path('/home/hoskinson/window-integration-qa') / directory
        for filename in ('report.json','root-completion.json'):
            add(evidence / filename)
    report = json.loads((HERE / 'offline-report.json').read_text())
    if not report['sourceUnchangedDuringProof'] or any(c['exit'] for c in report['commands']):raise SystemExit('offline gates not accepted')
    for filename,digest in report['sourceSHA256'].items():add(filename,digest)
    for command in report['commands']:add(command['log'],command['logSHA256'])
    failed = Path('/home/hoskinson/window-integration-qa/family-raster-default-readback-v10/attempt-1')
    for path in failed.iterdir():
        if path.is_file():add(path)
    for path in (failed / 'owned-readbacks').iterdir():
        if path.is_file():add(path)
    coverage_attribution_path=HERE/'retained-v10-coverage-attribution.json'
    coverage_attribution=json.loads(coverage_attribution_path.read_text())
    for filename,digest in coverage_attribution['inputs'].items():add(filename,digest)
    if not coverage_attribution['allBadPixelsEqualPreviousPrefix'] or coverage_attribution['comparison']['badPixels']!=83:raise SystemExit('actual immutable missing-row counterexample absent')
    for path in HERE.iterdir():
        if path.is_file():add(path)
    # Compiler-generated dependency lists include the complete system header tree.
    flags = shlex.split(subprocess.check_output(['pkg-config','--cflags','Qt6Core','libpng','egl','glesv2','wayland-client','wayland-egl'],text=True))
    dependency_commands = []
    for source in sorted(HERE.glob('*.cpp')):
        command = ['g++','-std=c++20','-fPIC','-M','-MT','dependency-target',*flags,source.name]
        text = subprocess.check_output(command,cwd=HERE,text=True)
        dependencies = shlex.split(text.replace(chr(92)+'\n',' ').split(':',1)[1])
        for filename in dependencies:add(HERE / filename)
        dependency_commands.append(command)
    binaries = [HERE / 'hypr-motion-renderer-staged']
    for name in ('g++','cc','make','pkg-config','wayland-scanner','python3','quint','node','glslangValidator'):
        path = shutil.which(name)
        if not path:raise SystemExit('proof/build tool missing: '+name)
        add(path);binaries.append(Path(path).resolve())
    for name in ('cc1plus','cc1','as','ld'):
        path = subprocess.check_output(['g++','-print-prog-name='+name],text=True).strip()
        path = Path(path) if '/' in path else Path(shutil.which(path) or '')
        add(path);binaries.append(path.resolve())
    for binary in binaries:
        if binary.read_bytes()[:4] != bytes.fromhex('7f454c46'):continue
        result = subprocess.run(['ldd',str(binary)],capture_output=True,text=True)
        if result.returncode:raise SystemExit('library closure inspection failed: '+str(binary))
        for filename in re.findall(r'(?:=> )?(/[^\s]+) \(',result.stdout):add(filename)
    binary = HERE / 'hypr-motion-renderer-staged'
    over,copy = shader_digests((HERE / 'QuantizedOver.hpp').read_text())
    packet = {
        'scope':'explicit per-layer RGBA8 source-over diagnostic only; no native pixel/reversal/cadence acceptance',
        'nativeLaunch':False,'GPUOperation':False,'original1418V8InputsUnchanged':True,
        'retainedV6V8V9V10FailuresUnchanged':True,
        'causalReadTarget':'copy complete current prefix to owned EGL default0 before each native/RGBA read pair; original pair guard unchanged','pixelComparisonsUnchanged':True,'fullImageComparisons':44,'completeReadPairs':18,
        'toleranceChanged':False,'tolerance':1,'readinessAuthority':False,'endpointAuthority':False,
        'binary':str(binary),'binarySHA256':sha(binary),'fragmentSHA256':over,'copyFragmentSHA256':copy,
        'launch':[str(binary),'--raster-fixture','--causal-readback-dir','<existing-owned-nonsymlink-0700-directory>','--quantized-over-experiment'],
        'compiledProgramRoles':'distinct positive exact over/copy program IDs; every queried pass/copy matches its role',
        'coveragePolicy':'top-left-half-open-pixel-centers-v1','coverageContract':'full-screen over with exact queried per-member/control pixel-center bounds/sample rectangle, viewport, vertex state, and actual output geometry; ordinary path unchanged',
        'resourceContract':'two separate bounded RGBA8 prefix textures/framebuffers per output generation/extent; transparent reset; partial allocation retirement; failed teardown refuses reuse',
        'offlineReport':str(HERE / 'offline-report.json'),'retainedAttribution':str(attribution_path),'retainedCoverageFailureAttribution':str(coverage_attribution_path),
        'dependencyCommands':dependency_commands,'inputs':dict(sorted(inputs.items())),
        'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
    # Recheck the complete byte/mode/link closure immediately before publishing.
    for filename,digest in inputs.items():
        path = Path(filename)
        if sha(path)!=digest or stat.S_IMODE(path.stat().st_mode)!=modes[filename]:raise SystemExit('closure changed before freeze: '+filename)
    for filename,value in links.items():
        if os.readlink(filename)!=value:raise SystemExit('symlink changed before freeze: '+filename)
    target.write_text(json.dumps(packet,indent=2)+'\n')
    record = {'manifest':str(target),'manifestSHA256':sha(target),'inputCount':len(inputs),'modeCount':len(modes),'linkCount':len(links),
        'binarySHA256':sha(binary),'fragmentSHA256':over,'copyFragmentSHA256':copy,'nativeLaunch':False,'GPUOperation':False,
        'currentStageFrozen':True,'offline':report,
        'pending':'root independent source/mode review, fresh private unchanged44-image native campaign, then held continuous reversal/recovery and cadence; no native grant assumed'}
    checkpoint.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'manifestSHA256':sha(target),'checkpointSHA256':sha(checkpoint),'binarySHA256':sha(binary),
        'fragmentSHA256':over,'copyFragmentSHA256':copy,'inputs':len(inputs),'modes':len(modes),'links':len(links)}))

if __name__ == '__main__':main()
