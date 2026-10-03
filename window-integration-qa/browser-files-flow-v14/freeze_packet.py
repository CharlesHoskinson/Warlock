#!/usr/bin/env python3
"""Freeze reviewed browser/Files/host/candidate transitive inputs; never launches GUI."""
from pathlib import Path
import hashlib,json,os,stat,sys
B=Path(__file__).resolve().parent;Q=B.parent
files={};links={};provenance={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(p,expected=None):
 p=Path(p)
 if p.is_symlink():
  links[str(p)]=os.readlink(p);add(p.resolve(),expected)
 actual=sha(p)
 if expected is not None and actual!=expected:raise RuntimeError('Source mismatch '+str(p))
 row={'path':str(p),'sha256':actual,'mode':stat.S_IMODE(p.stat().st_mode)}
 if str(p) in files and files[str(p)]!=row:raise RuntimeError('Conflicting input '+str(p))
 files[str(p)]=row
 if p.resolve()!=p:add(p.resolve(),expected)
def include_manifest(p):
 add(p);packet=json.loads(Path(p).read_text());rows=packet.get('files',packet.get('inputs',{}))
 for path,value in (rows.items() if isinstance(rows,dict) else [(r['path'],r['sha256']) for r in rows]):add(path,value)
 source_links=packet.get('symlinks',{})
 for path,target in (source_links.items() if isinstance(source_links,dict) else [(r['path'],r['target']) for r in source_links]):
  if not Path(path).is_symlink() or os.readlink(path)!=target:raise RuntimeError('Link changed '+path)
  links[path]=target
 provenance[str(p)]=sha(p)
# Accepted immutable host, probe, compiler and loader inputs, with prior failures retained.
for name in ['qt-modal-private-v9','toolkit-interruption-v5','private-weston-aq-host-v4','aquamarine-nested-lifecycle-v1']:
 include_manifest(Q/name/'frozen-inputs.json')
add(Q/'toolkit-v4-root-source-review.json')
add(Q/'toolkit-v5-root-source-review.json')
add(Q/'browser-files-flow-v1/frozen-inputs.json')
add(Q/'browser-files-flow-v2/frozen-inputs.json')
add(Q/'browser-files-flow-v3/frozen-inputs.json')
add(Q/'browser-files-flow-v4/frozen-inputs.json')
add(Q/'browser-files-flow-v5/frozen-inputs.json')
add(Q/'browser-files-flow-v6/frozen-inputs.json')
add(Q/'browser-files-flow-v7/frozen-inputs.json')
add(Q/'browser-files-flow-v8/frozen-inputs.json')
add(Q/'browser-files-flow-v9/frozen-inputs.json')
add(Q/'browser-files-flow-v10/frozen-inputs.json')
include_manifest(Q/'browser-files-flow-v11/frozen-inputs.json')
include_manifest(Q/'browser-files-flow-v12/frozen-inputs.json')
include_manifest(Q/'browser-files-flow-v13/frozen-inputs.json')
add(Q/'browser-v13-root-source-review.json')
add('/usr/include/wayland-util.h')
for p in [*(Q/'browser-v12-independent-review').rglob('*'),*(Q/'browser-v13-independent-review').rglob('*')]:
 if p.is_file() and '__pycache__' not in p.parts:add(p)
add('/usr/bin/objdump')
add('/usr/bin/pacman')
add('/usr/share/man/man1/dbus-daemon.1.gz')
add('/usr/share/dbus-1/session.conf')
loader=B/'loader-closure.json';add(loader);packet=json.loads(loader.read_text())
for p,v in packet['files'].items():add(p,v)
for p,v in packet['symlinks'].items():
 if not Path(p).is_symlink() or os.readlink(p)!=v:raise RuntimeError('Loader symlink changed '+p)
 links[p]=v
# Python imports and original main product observations are actual executed source inputs.
for name in ['qa_run.py','qa_launch.py']:add(Q/name)
for row in json.loads((B/'files-copy-provenance.json').read_text())['source']:add(row['live'],row['liveSHA256'])
for folder in ['/usr/lib/python3.14','/usr/share/icons','/usr/share/mime']:
 for p in Path(folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'site-packages' not in p.parts:add(p)
for name in ['/usr/bin/wl-paste','/usr/bin/gsettings','/usr/bin/gdbus','/usr/lib/locale/locale-archive','/etc/ld.so.cache','/etc/localtime','/etc/fonts/fonts.conf','/usr/share/glvnd/egl_vendor.d/50_mesa.json']:
 if Path(name).is_file():add(name)
for p in B.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and not any(x.startswith('attempt-') for x in p.parts) and p.name not in ['frozen-inputs.json','preflight-report.json','freeze-verification.json']:add(p)
packet={'scope':'Private original Brave local draft/copy-real-Files callback and focus continuity, genuine release/private config reload; no main input/network/mail/deployment','files':list(files[p] for p in sorted(files)),'symlinks':[{'path':p,'target':v} for p,v in sorted(links.items())],'command':[sys.executable,str(Q/'qa_run.py'),'--',sys.executable,str(B/'run_native.py'),'--attempt',str(B/'attempt-1')],'preflightCommand':[sys.executable,str(B/'run_native.py'),'--preflight'],'candidateSHA256':'bdd8bab3b3cea6f2dd2e49b317f133691cc920700f9743d21438c0e3338a0dc7','sourceProvenance':provenance,'featureGates':15,'hostGates':10,'mainPreservationGates':18,'byteModeLinkClosure':True,'liveOwnedMappingsMustMatch':True,'descendantMappingsUnreadableFails':True,'rawOwnedProcessEvidenceBeforeRoleFilter':True,'rawOwnedMappingEvidenceBeforeValidation':True,'configuredAndInstalledNssClosure':True,'allStableV6MappingsAndElfDependenciesPinned':True,'sharedDataRequiredFullMode':0,'sharedDataPolicy':'Only exact copied Files read-only UUID tmpfs data with owned compositor read-only FD/device/inode/exact full mode0000/UID/unlink/access/mount/bounds and before/after lifetime/kernel-peer/VMA/FD confirmation; no executable or ordinary deleted disk code allowance','sharedDataObservationScope':'All captured owned maps plus fresh before/after Files/compositor maps; not global or continuous inspection','browserMetricsDataPolicy':'Only exact PID/start/UID/scope/frozen-executable root runtime-profile anchors and stable present exact directory0700 OR absent exact descriptor-relative ENOENT canonical BrowserMetrics parent state, canonical PID target, one O_RDWR non-O_PATH FD/full mode0600/regular/nlink0/4MiB/device/inode/tmpfs mount and fullsize rw-s offset0 VMA; before/after stable projection plus fresh confirmation after strict disk validation; captured exact root rawmaps hash and line only; no exec alias in complete observed batch and fresh root/compositor maps; contents/timestamps/position mutable, no histogram/sourcebranch claim', 'browserMetricsTemporalModel':'runtime_metrics.qnt exact root/runtime/profile/present-parent tokens OR stable absentENOENT parent state and epoch invalidation; original model/source/failure proofs retained', 'browserMetricsDetachedParentPolicy':'Read-only O_DIRECTORY|O_NOFOLLOW profile FD fstat and named identity before/after must match exact prelaunch profile anchor; follow_symlinksFalse lookup of BrowserMetrics singlecomponent, exact actual ENOENT filename and full requestedpath; parent state stable through before/after/postdisk and later mapping phases; no historical absent parent inode/mode/unlink actor/sourcebranch claim', 'browserMetricsInputRequiresConfirmedWitness':True,'actualFullMappingCoverageProved':False,'privateSessionBusZeroActivationDirectories':True,'appSessionAndSystemBusExplicitlyPrivate':True,'runtimeMappingPolicy':'Only non-executable owned profile/tmp/cache/quickshell data; disk code always frozen','anonymousRuntimeCode':'Anonymous memfd/JIT maps recorded separately; not disk-input freeze proof','diagnosticKernelInitialEnvironmentRange':True,'selectorAuthorityProperty':'Observed actual PID-bound private session-bus connection plus exact final pre-exec selectors; no direct currentgetenv/GIO claim','nativeExecution':False,'mainGUIWrites':False,'mainRestorationWrites':False,'physicalHardwareProved':False,'productionDeployment':False,'requiredReview':'Root exclusive native grant for exact one command/attempt; retain all failures'}
packet.update(browserCoordinatePolicy='Two serial genuine trusted primary button-free pointermove observations, exact same page timeOrigin/session/lifetime/layout/output; native float cursor and exact browser hit/pointer owner stable before-after; installed24.8 wire representation and two exactly equal native-wire minus CSS client translations; all four observed viewport insets contained, no guessed offset/epsilon; integer strictly interior point and full two-token integer grammar before every actual move; original15 feature oracles unchanged',browserCoordinateTemporalModels=['viewport_geometry.qnt','coordinate_representation.qnt','pointer_syntax.qnt'],browserCoordinateCalibrationIsOriginalFeatureAcceptance=False)
p=B/'frozen-inputs.json';assert not p.exists();p.write_text(json.dumps(packet,indent=2)+'\n');p.chmod(0o600)
print(json.dumps({'files':len(files),'links':len(links),'manifestSHA256':sha(p),'diagnosticKernelInitialEnvironmentRange':True,'selectorAuthorityProperty':'Observed actual PID-bound private session-bus connection plus exact final pre-exec selectors; no direct currentgetenv/GIO claim','nativeExecution':False}))
