"""Offline source/package/dependency freeze; never starts a compositor or probe."""
from pathlib import Path
import hashlib,json,re,subprocess
STAGE=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 target=STAGE/'host-stage-report.json'
 if target.exists():raise RuntimeError('Preserve frozen stage; use a fresh revision')
 files={};links={}
 for p in sorted(STAGE.rglob('*')):
  name=str(p.relative_to(STAGE))
  if '__pycache__' in p.parts or 'gpg' in p.relative_to(STAGE).parts:continue
  if p.is_symlink():links[name]=p.readlink().as_posix()
  elif p.is_file():files[name]=digest(p)
 dependencies=set()
 mapping=json.loads((STAGE/'dependency-map.json').read_text())
 for rows in mapping.values():dependencies.update(row['path'] for row in rows if not Path(row['path']).is_relative_to(STAGE))
 for name in ('dependencies-probe.log','dependencies-hyprland.log'):
  text=(STAGE/name).read_text();assert 'not found' not in text
  dependencies.update(re.findall(r'(?:=>\s+|^\s*)(/\S+)\s+\(',text,re.M))
 dependencies.update(['/usr/bin/Hyprland','/usr/bin/hyprctl','/usr/bin/dbus-daemon','/usr/bin/systemd-run','/usr/bin/prlimit','/usr/bin/python3','/usr/bin/wayland-scanner','/usr/bin/gpgv','/usr/share/pacman/keyrings/archlinux.gpg','/usr/share/wayland-protocols/stable/linux-dmabuf/linux-dmabuf-v1.xml','/usr/share/glvnd/egl_vendor.d/50_mesa.json','/usr/lib/libEGL_mesa.so.0','/usr/lib/libgbm.so.1','/usr/lib/dri/iris_dri.so',str(STAGE.parent/'qa_launch.py'),str(STAGE.parent/'qa_run.py'),'/home/hoskinson/Documents/crash-noise/HANDOFF-codex-window-qa.md'])
 dependencies.update(str(p) for p in Path('/usr/lib').glob('libgallium*.so'))
 external={name:digest(name) for name in sorted(dependencies)}
 signature=(STAGE/'downloads/weston-signature-verified.log').read_text()
 fingerprint='83BC8889351B5DEBBB68416EB8AC08600F108CDF'
 assert '[GNUPG:] VALIDSIG '+fingerprint in signature
 build=(STAGE/'prefix/.BUILDINFO').read_text()
 assert 'pkgbuild_sha256sum = '+digest(STAGE/'primary/Arch-PKGBUILD') in build
 assert digest(STAGE/'downloads/weston-15.0.1-release.tar.xz')=='551d039bfb0c837ba5a4d027cdb8ee16bded0eedb789821f8025d8a64b791f6d'
 assert digest(STAGE/'downloads/weston-neatvnc1.patch')=='753d04e7f7acf2e4dfc7956ac2f8c75b8f592316fdc15971393d339d58bb077a'
 for name in ('weston','headless','gl','kiosk'):assert 'not found' not in (STAGE/('dependencies-'+name+'.log')).read_text()
 tests=(STAGE/'offline-tests.stdout').read_text();assert 'Ran 15 tests' in tests and tests.rstrip().endswith('OK')
 report=dict(stage='signed-private-weston-host-v1',nativeHostAccepted=False,compositorLaunchOccurred=False,package='weston15.0.1-3',packageSHA256=digest(STAGE/'downloads/weston-15.0.1-3-x86_64.pkg.tar.zst'),signatureVerified=True,signatureFingerprint=fingerprint,requiredELFMissingDependencies=0,offlineNamedTests=15,probeCompiledWerror=True,sourceReleaseHashesVerified=True,crashHandoffApplied=True,scopeWrapperCorrection='systemd261 scopes reject LimitCORE; dedicated user scope then prlimit --core=1:1 before complete runner',runtimeScheme='/run/user/$UID/wqa/qa-*',defaultXwayland=False,mainWrites=False,files=files,symlinks=links,externalDependencies=external,licenseFiles=[name for name in files if name.startswith('prefix/usr/share/licenses/')],sourceProvenance=json.loads((STAGE/'downloads/source-provenance.json').read_text()))
 target.write_text(json.dumps(report,indent=2)+'\n');target.chmod(0o600)
 print(json.dumps(dict(manifestSHA256=digest(target),localFiles=len(files),symlinks=len(links),externalDependencies=len(external),nativeHostAccepted=False)))
if __name__=='__main__':main()
