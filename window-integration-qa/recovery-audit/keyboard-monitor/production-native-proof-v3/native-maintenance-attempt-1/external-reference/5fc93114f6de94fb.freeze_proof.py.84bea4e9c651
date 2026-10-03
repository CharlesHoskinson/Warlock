"""Freeze only this offline proof plus exact accepted source closures; no launch."""
from pathlib import Path
import hashlib,json,os,stat
ROOT=Path(__file__).resolve().parent
QA=Path('/home/hoskinson/window-integration-qa')
KEYBOARD=ROOT.parent
V3=KEYBOARD/'production-maintenance-v3'
V5=KEYBOARD/'pointer-private-host-v5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v3=json.loads((V3/'stage-manifest.json').read_text());v5=json.loads((V5/'pointer-frozen-stage-report.json').read_text())
external={};links={};external_modes={}
def record(path,expected=None):
    path=Path(path).absolute()
    if path.is_symlink():links[str(path)]=str(path.readlink())
    path=path.resolve(strict=True)
    digest=sha(path)
    if expected is not None and digest!=expected:raise RuntimeError('retained source drift: '+str(path))
    if str(path) in external and external[str(path)]!=digest:raise RuntimeError('conflicting actual source '+str(path))
    external[str(path)]=digest;external_modes[str(path)]=stat.S_IMODE(path.stat().st_mode)
for path,digest in v5['externalDependencies'].items():record(path,digest)
for path,digest in v3['external'].items():record(path,digest)
for path,value in {**v5['externalSymlinks'],**v3['links']}.items():
    p=Path(path)
    if not p.is_symlink() or str(p.readlink())!=value:raise RuntimeError('retained link drift '+path)
    links[path]=value
for path,digest in v3['local'].items():
    record(V3/path,digest)
    if stat.S_IMODE((V3/path).stat().st_mode)!=v3['localModes'][path]:raise RuntimeError('V3 mode drift '+path)
for path,digest in v5['dependencies'].items():record(V5/path,digest)
for path in (ROOT.parent/'production-native-proof-v1/proof-frozen-stage-report.json',ROOT.parent/'production-native-proof-v1/native-maintenance-attempt-1/root-completion.json',V3/'stage-manifest.json',V3/'stage-report.json',KEYBOARD/'production-v3-root-review.json',V5/'pointer-frozen-stage-report.json',V5/'native-pointer-attempt-5/native-pointer-report.json',V5/'native-pointer-attempt-5/root-completion.json',QA/'qa_run.py',QA/'qa_launch.py',QA/'private-weston-aq-host-v4/frozen-inputs.json'):
    record(path)
excluded={'__pycache__','payload-v2-reference','external-reference'}
excluded_files={'proof-frozen-stage-report.json','proof-stage-report.json','freeze-verification.json','runtime-import-preflight.json'}
local={};modes={}
for path in sorted(ROOT.rglob('*')):
    rel=path.relative_to(ROOT)
    if any(part in excluded or part.startswith('native-maintenance-attempt-') for part in rel.parts) or path.name in excluded_files:continue
    if path.is_symlink():raise RuntimeError('undeclared local symlink '+str(rel))
    if not path.is_file():continue
    mode=stat.S_IMODE(path.stat().st_mode)
    if mode&0o7022:raise RuntimeError('unsafe proof file mode '+str(rel))
    local[str(rel)]=sha(path);modes[str(rel)]=mode
for name,digest in v3['local'].items():
    if name.startswith('payload/'):
        if local.get(name)!=digest or modes.get(name)!=v3['localModes'][name]:raise RuntimeError('copied actual V3 payload differs '+name)
manifest=dict(kind='private actual production V3 control/reader maintenance proof',frozen=True,nativeLaunched=False,
    hostAdapter=str(QA/'private-weston-aq-host-v4'),dependencies=local,dependencyModes=modes,externalDependencies=external,externalModes=external_modes,externalSymlinks=links,
    retainedV3ManifestSHA256=sha(V3/'stage-manifest.json'),retainedV5ManifestSHA256=sha(V5/'pointer-frozen-stage-report.json'),inheritedPrivateAcceptance=185,inheritedPrivatePreservation=19,
    exclusions=sorted(excluded),nativeAccepted=False,productionAccepted=False,privateFixtureInjection='actual Control approved=False factory only; canonical main refused before transport',
    command=['python3',str(QA/'qa_run.py'),'--','python3',str(ROOT/'native_probe_maintenance.py'),'--execute','--output',str(ROOT/'native-maintenance-attempt-1')])
(ROOT/'proof-frozen-stage-report.json').write_text(json.dumps(manifest,indent=2)+'\n')
report=dict(manifestSHA256=sha(ROOT/'proof-frozen-stage-report.json'),localInputs=len(local),externalInputs=len(external),symlinks=len(links),allLocalModes=True,allExternalModes=True,
    actualProductionSO=sha(ROOT/'payload/native/libomarchy-a11y-prod-v2.so'),actualProductPackage=sha(ROOT/'payload/package.json'),actualCases=sha(ROOT/'proof_cases.py'),actualRunner=sha(ROOT/'native_probe_maintenance.py'),
    formalNamed=7,formalSamples=2000,formalSteps=100,formalSeed=20461010,sourceTests=21,actualNoGUIImportPreflight=True,inheritedProductionFormalNamed=8,inheritedModeNamed=6,inheritedActualLuaTests=24,inheritedProductionSourceTests=26,
    inheritedPrivate185ReportSHA256='fd4c8678b208f5ff56ce0e6e35f403a6e40e6a3329947b9792336fae9816d2b4',
    nativeAccepted=False,productionAccepted=False,mainChanged=False,readerStarted=False,nativeLaunched=False,command=manifest['command'])
(ROOT/'proof-stage-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
