"""Static installed Qt plugin dependency closure. No toolkit/display initialization."""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess
B=Path(__file__).resolve().parent

def collect():
    files={};modes={};links={};logs={}
    def add(path):
        path=Path(os.path.normpath(str(path)))
        while path.is_symlink():
            target=os.readlink(path);links[str(path)]=target
            path=Path(os.path.normpath(target if target.startswith('/') else str(path.parent/target)))
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            before=os.fstat(fd);digest=hashlib.sha256();size=0
            if not stat.S_ISREG(before.st_mode) or before.st_size>2147483648:raise RuntimeError('Bounded regular loader file required')
            def witness(s):return s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns,s.st_ctime_ns
            while data:=os.read(fd,1048576):size+=len(data);digest.update(data)
            if size!=before.st_size or witness(before)!=witness(os.fstat(fd)) or witness(before)!=witness(path.lstat()):raise RuntimeError('Loader source changed during full EOF read')
            files[str(path)]=digest.hexdigest();modes[str(path)]=stat.S_IMODE(before.st_mode)
        finally:os.close(fd)
    plugins=Path('/usr/lib/qt6/plugins')
    roots=[plugins/'platforms/libqwayland.so',plugins/'platforms/libqxcb.so']
    for directory in ('wayland-shell-integration','wayland-graphics-integration-client','wayland-decoration-client','xcbglintegrations'):
        roots+=sorted((plugins/directory).glob('*.so'))
    for root in roots:
        add(root)
        result=subprocess.run(['/usr/bin/ldd',str(root)],env={'PATH':'/usr/bin','LC_ALL':'C'},capture_output=True,text=True,timeout=10)
        if result.returncode or 'not found' in result.stdout+result.stderr:raise RuntimeError('Installed Qt loader dependency unresolved: '+str(root))
        logs[str(root)]=dict(argv=['/usr/bin/ldd',str(root)],stdout=result.stdout,stderr=result.stderr,returncode=result.returncode)
        for line in result.stdout.splitlines():
            for name in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',line):add(name)
    add('/usr/bin/ldd');add('/usr/bin/bash');add('/usr/bin/env')
    report=dict(inputs=files,inputModes=modes,symlinks=links,roots=list(map(str,roots)),ldd=logs,GUIInitialized=False,nativeLaunch=False,actualMapsRequired=True)
    path=B/'qt-loader-inputs.json';fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(inputs=len(files),modes=len(modes),links=len(links),nativeLaunch=False)))
if __name__=='__main__':collect()
