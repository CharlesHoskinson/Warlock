"""Offline package construction from frozen accepted sources and signed archives."""
from pathlib import Path
import hashlib,json,shutil,stat,subprocess
HERE=Path(__file__).resolve().parent
QA=Path('/home/hoskinson/window-integration-qa')
READER=QA/'orca-reader'
SIGNED=HERE.parent/'mouse-review-signed-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source,target):target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
def construct():
    payload=HERE/'payload'
    if payload.exists():raise RuntimeError('fresh payload required; do not overwrite reviewed package')
    payload.mkdir(mode=0o700)
    for name in ('control.py','mapping_artifact.py','reader_bootstrap.py','launch_reader.py','capability_adapter.py','reader_reconnect_v7.py','legacy_keygrab_compat.py','CONTRACT.md'):
        copy(HERE/name,payload/name)
    copy(HERE/'native/libomarchy-a11y-prod-v2.so',payload/'native/libomarchy-a11y-prod-v2.so')
    shutil.copytree(READER/'prefix',payload/'reader-prefix',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(SIGNED/'orca-compat',payload/'orca-compat',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    # Archives/signatures and PKGINFO are kept alongside exact copied payload,
    # so package identity and source/licensing do not depend on mutable URLs.
    provenance=[]
    keyring=HERE/'archlinux-keys.gpg'
    if not keyring.exists():
        keyring.write_bytes(subprocess.check_output(['gpg','--dearmor'],input=Path('/usr/share/pacman/keyrings/archlinux.gpg').read_bytes()))
    for row in json.loads((READER/'packages.json').read_text()):
        name=row['url'].rsplit('/',1)[1];package=READER/'packages'/name;signature=Path(str(package)+'.sig')
        if sha(package)!=row['sha256']:raise RuntimeError('signed archive hash changed: '+name)
        result=subprocess.run(['gpgv','--keyring',str(keyring),str(signature),str(package)],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        copy(package,payload/'provenance/packages'/name);copy(signature,payload/'provenance/packages'/(name+'.sig'))
        info=subprocess.check_output(['bsdtar','-xOf',str(package),'.PKGINFO']).decode()
        metadata=payload/'provenance'/('pkginfo-'+row['name']+'.txt');metadata.write_text(info)
        licences=[line.split(' = ',1)[1] for line in info.splitlines() if line.startswith('license = ')]
        for licence in licences:
            standard=Path('/usr/share/licenses/spdx')/(licence+'.txt')
            if standard.exists():copy(standard,payload/'licenses'/standard.name)
        provenance.append(dict(row,signatureSHA256=sha(signature),signatureCheck=result.stderr,licenses=licences))
    # LGPL v2.1 is the original Orca source header's governing license, with
    # later versions selectable; include both GPL and LGPL references.
    for name in ('LGPL-2.1-only','LGPL-2.1-or-later','LGPL-3.0-only','GPL-2.0-only','GPL-3.0-only'):
        source=Path('/usr/share/licenses/spdx')/(name+'.txt')
        if source.exists():copy(source,payload/'licenses'/source.name)
    copy(SIGNED/'orca-compat-provenance.json',payload/'provenance/orca-compat-provenance.json')
    copy(SIGNED/'v2-to-signed-v3.diff',payload/'provenance/signed-coordinate-change.diff')
    (payload/'provenance/packages.json').write_text(json.dumps(provenance,indent=2))
    sources=payload/'source/native';sources.mkdir(parents=True)
    for source in (HERE/'native').iterdir():
        if source.suffix in ('.hpp','.cpp','.diff'):copy(source,sources/source.name)
    copy(HERE/'maintenance.qnt',payload/'source/maintenance.qnt')
    copy(HERE/'package_modes.qnt',payload/'source/package_modes.qnt')
    copy(HERE/'mapping_identity.qnt',payload/'source/mapping_identity.qnt')
    copy(HERE/'native/ldd.txt',payload/'provenance/native-ldd.txt')
    copy(HERE/'README.md',payload/'README.md')
    copy(HERE/'NATIVE_CONTRACT.md',payload/'NATIVE_CONTRACT.md')
    copy(HERE/'install.py',payload/'source/install.py')
    copy(HERE/'build_package.py',payload/'source/build_package.py')
    copy(HERE/'native/build.sh',payload/'source/native/build.sh')
    package=dict(schema=2,packageID='omarchy-a11y-prod-v2',identity='Omarchy native monitor + Omarchy Orca compat signed-v3',
        library='native/libomarchy-a11y-prod-v2.so',sha256=sha(payload/'native/libomarchy-a11y-prod-v2.so'),
        hyprlandABI='efb50993780079460b0cbed1363e2166a2de1d9f_aq_0.15_hu_0.14_hg_0.5_hc_0.1_hlg_0.6',pluginName='omarchy-a11y-monitor',pluginVersion='0.8-production-v2',hyprlandCommit='efb50993780079460b0cbed1363e2166a2de1d9f',
        nativeAccepted=False,inheritedPolicyNativeAccepted=True,productionAccepted=False,privateProbeAbsent=True,
        acceptanceScope='Accepted185 applies to inherited policy/private service; production init/Lua/transport/bootstrap/real speech remain unproved.',
        privateCampaignReportSHA256='fd4c8678b208f5ff56ce0e6e35f403a6e40e6a3329947b9792336fae9816d2b4',readerDefault='disabled; existing org.a11y.Status.ScreenReaderEnabled required',
        originalReaderSigned=True,modifiedModules=['mouse_review.py'],systemLibrariesModified=False)
    (payload/'package.json').write_text(json.dumps(package,indent=2))
    closure={str(p.relative_to(payload)):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(payload.rglob('*')) if p.is_file()}
    if any(row['mode'] not in (0o644,0o755) for row in closure.values()):raise RuntimeError('unsafe or unexpected payload source mode')
    (payload/'payload-manifest.json').write_text(json.dumps(closure,indent=2))
    print(json.dumps(dict(payload=str(payload),files=len(closure),packageSHA256=sha(payload/'package.json'),payloadManifestSHA256=sha(payload/'payload-manifest.json'),productionAccepted=False)))
if __name__=='__main__':construct()
