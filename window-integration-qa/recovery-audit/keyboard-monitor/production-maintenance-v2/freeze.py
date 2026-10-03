"""Freeze review inputs; excluded earlier failed/unreviewed generations retained."""
from pathlib import Path
import hashlib,json,re,shlex
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
excluded={'__pycache__','payload-build-failed-keyring-1','payload-generation-1-unfrozen'}
local={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and not any(part in excluded for part in p.relative_to(HERE).parts) and p.name not in ('stage-manifest.json','stage-report.json')}
external={};links={}
def record(path):
    path=Path(path).absolute()
    if not path.exists():raise RuntimeError('missing freeze input '+str(path))
    if path.is_symlink():links[str(path)]=str(path.readlink())
    resolved=path.resolve()
    if not resolved.is_relative_to(HERE):external[str(resolved)]=sha(resolved)
text=(HERE/'native/plugin-production.d').read_text().replace('\\\n',' ')
for item in shlex.split(text.split(':',1)[1]):record(Path(item) if item.startswith('/') else HERE/'native'/item)
for row in (HERE/'native/ldd.txt').read_text().splitlines():
    for path in re.findall(r'(/[^\s]+)',row):record(path)
for path in ('/usr/bin/g++','/usr/bin/pkg-config','/usr/bin/python3','/usr/bin/hyprctl','/usr/bin/gpgv','/usr/share/pacman/keyrings/archlinux.gpg','/home/hoskinson/window-integration-qa/qa_launch.py'):
    record(path)
manifest={'local':local,'external':external,'links':links,'exclusions':sorted(excluded),'scope':'offline production candidate; no install/load/start/native proof'}
(HERE/'stage-manifest.json').write_text(json.dumps(manifest,indent=2))
report=dict(stage='production-maintenance-v2',manifestSHA256=sha(HERE/'stage-manifest.json'),localInputs=len(local),externalInputs=len(external),symlinks=len(links),
 formalNamed=8,formalSamples=2000,formalMaxSteps=100,formalSeed=20461009,actualLuaNonceRuntimeScenarios=24,pythonSourceAndFilesystemTests=19,
 signedArchivesVerified=7,payloadFiles=len(json.loads((HERE/'payload/payload-manifest.json').read_text())),
 SO_SHA256=sha(HERE/'native/libomarchy-a11y-prod-v2.so'),packageSHA256=sha(HERE/'payload/package.json'),payloadManifestSHA256=sha(HERE/'payload/payload-manifest.json'),
 inheritedPrivateAcceptance=185,inheritedPrivatePreservation=19,nativeAccepted=False,productionAccepted=False,mainChanged=False,readerStarted=False,readerIntentChanged=False,
 nativeContract='NATIVE_CONTRACT.md',installPlan='reviewed-install-plan.json',retainedV5ReportSHA256='fd4c8678b208f5ff56ce0e6e35f403a6e3329947b9792336fae9816d2b4')
# Correct authoritative original report token; no source evidence rewriting.
report['retainedV5ReportSHA256']='fd4c8678b208f5ff56ce0e6e35f403a6e40e6a3329947b9792336fae9816d2b4'
(HERE/'stage-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
