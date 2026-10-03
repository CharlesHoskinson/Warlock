"""CPU-only feasibility and replacement witness; no product authority or native API."""
from pathlib import Path
import errno,fcntl,hashlib,json,os,stat

REQUIRED=fcntl.F_SEAL_SEAL|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_GROW|fcntl.F_SEAL_WRITE|32

def metadata(fd):
    st=os.fstat(fd)
    return {'fd':fd,'target':os.readlink(f'/proc/self/fd/{fd}'),'device':st.st_dev,'inode':st.st_ino,
            'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid,'links':st.st_nlink,'size':st.st_size,
            'fullFlags':fcntl.fcntl(fd,fcntl.F_GETFL),'accessMode':fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE,
            'fdFlags':fcntl.fcntl(fd,fcntl.F_GETFD),'seals':fcntl.fcntl(fd,fcntl.F_GET_SEALS),
            'sha256':hashlib.sha256(os.pread(fd,st.st_size,0)).hexdigest()}

def individually_valid(m):
    return (m['mode']==0o600 and m['uid']==os.getuid() and m['links']==0 and m['accessMode']==os.O_RDWR and
            not(m['fullFlags']&os.O_PATH) and m['fdFlags']==fcntl.FD_CLOEXEC and m['seals']==REQUIRED)

def main():
    fds=[]
    try:
        for n in (1,2):
            fd=os.memfd_create(f'readonly-v22-design-only-{n}',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING|8);fds.append(fd)
            os.fchmod(fd,0o600);os.write(fd,b'V22 design-only; identical bytes do not grant replacement authority\n')
            fcntl.fcntl(fd,fcntl.F_ADD_SEALS,REQUIRED)
        before=metadata(fds[0]);replacement=metadata(fds[1]);attempts=[]
        for name,fn in [('write',lambda:os.pwrite(fds[0],b'x',0)),('truncate',lambda:os.ftruncate(fds[0],1)),('chmodExecute',lambda:os.fchmod(fds[0],0o700))]:
            try:fn();attempts.append({'operation':name,'refused':False})
            except OSError as e:attempts.append({'operation':name,'refused':True,'errno':e.errno})
        after=metadata(fds[0])
        result={'version':2,'designOnly':True,'runtimeCopied':False,'nativeLaunch':False,'before':before,'after':after,
                'replacement':replacement,'individuallyValidBoth':individually_valid(before) and individually_valid(replacement),
                'sameBytes':before['sha256']==replacement['sha256'],'exactReplacementAccepted':before==replacement,
                'sameBeforeAfter':before==after,'attempts':attempts,'doesNotClaimPROTEXECPrevention':True,
                'headerSHA256':{n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in ['/usr/include/linux/memfd.h','/usr/include/linux/fcntl.h']}}
        Path(__file__).with_name('kernel-anchor-feasibility-v2.json').write_text(json.dumps(result,indent=2)+'\n')
        assert result['individuallyValidBoth'] and result['sameBytes'] and not(result['exactReplacementAccepted'])
        assert result['sameBeforeAfter'] and all(x['refused'] and x['errno']==errno.EPERM for x in attempts)
        print('PASS actual sealed-FD replacement and before/after refusal witness; no product authority')
    finally:
        for fd in fds:os.close(fd)

if __name__=='__main__':main()
