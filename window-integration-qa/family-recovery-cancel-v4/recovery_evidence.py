"""Bounded original baseline gate for separate recovery fault attempts."""
MAIN_CHECKS=frozenset(('allStableClientFields','originalFocus','originalCursor','originalLayers','typedClipboardAndPrimary','a11ySocketFlagsAndReaderEnabled','outputs','plugins','keyboardStates','fourCatalogNaturalBytes','dashboardBytes','originalFilesProcess','originalFilesPublicState','originalFilesFullUi','originalFilesVisibility'))
NORMAL_CLIENTS=frozenset(('family-service','qt-fixture','taskbar-shell'))

def validate_baseline(row,manifest_sha):
    if row.get('result')!='pass' or row.get('sourceManifestSHA256')!=manifest_sha:raise ValueError('original same-source baseline required')
    checks=row.get('checks')
    if not isinstance(checks,list) or len(checks)!=38 or any(c.get('passed') is not True for c in checks):raise ValueError('original complete38 acceptance gates required')
    main=row.get('mainPreservation',{})
    if set(main)!=MAIN_CHECKS or any(v is not True for v in main.values()):raise ValueError('all original15 main preservation gates required')
    cleanup=row.get('clientCleanup',{})
    if set(cleanup)!=NORMAL_CLIENTS or any(type(c.get('exitCode')) is not int or c['exitCode']!=0 or c.get('gone') is not True or c.get('error') or c.get('forcedTermination') or c.get('forcedKill') for c in cleanup.values()):raise ValueError('all original fixtures must terminate normally')
    if row.get('normalNativeUnload') is not True or row.get('allFrozenInputsExact') is not True or row.get('mainGUIWrites') is not False or row.get('mainRestorationWrites') is not False:raise ValueError('strict baseline unload/source/main gates required')
    return True


def runtime_peer_witness(root,session,identity,old_owner,root_identity,lock_identity,destination):
    """Actual private kernel lease/socket witness; state query grants no intent."""
    import fcntl,json,os,re,socket,stat,struct
    from pathlib import Path
    root=Path(root);record={'root':str(root),'expectedService':identity,'nativeAuthority':False};descriptor=lock=None
    def require(value,message):
        if not value:raise ValueError(message)
    def projection(info):return [info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)]
    def owner_read():
        fd=os.open('owner.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=descriptor)
        try:
            info=os.fstat(fd);data=os.read(fd,1048577);after=os.fstat(fd);named=os.stat('owner.json',dir_fd=descriptor,follow_symlinks=False)
            require(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600 and len(data)==info.st_size and len(data)<=1048576 and projection(info)==projection(after)==projection(named),'exact bounded current owner metadata required')
            return json.loads(data),projection(info)
        finally:os.close(fd)
    try:
        descriptor=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);r=os.fstat(descriptor);record['rootBefore']=projection(r)
        require([r.st_dev,r.st_ino]==root_identity and r.st_uid==os.getuid() and stat.S_IMODE(r.st_mode)==0o700,'actual anchored current private root required')
        lock=os.open('runtime.lock',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=descriptor);li=os.fstat(lock);record['lockBefore']=projection(li)
        require([li.st_dev,li.st_ino]==lock_identity and stat.S_ISREG(li.st_mode) and li.st_uid==os.getuid() and stat.S_IMODE(li.st_mode)==0o600,'actual anchored current lock required')
        blocked=False
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:blocked=True
        else:fcntl.flock(lock,fcntl.LOCK_UN)
        record['exclusiveLeaseBlocked']=blocked;require(blocked,'current normal exclusive runtime lease missing')
        before,before_inode=owner_read();record['ownerBefore']=before;record['ownerInodeBefore']=before_inode
        require(set(before)=={'pid','start','nonce','session','socket'} and all(type(before[k]) is int and before[k]>0 for k in ('pid','start')) and before['pid']==identity['pid'] and before['start']==int(identity['start']) and before['session']==session and type(before['nonce']) is str and re.fullmatch('[0-9a-f]{32}',before['nonce']) and before['nonce']!=old_owner['nonce'],'exact typed fresh owner/lifetime/session required')
        api=os.stat('api.sock',dir_fd=descriptor,follow_symlinks=False);record['socketBefore']=projection(api)
        require(stat.S_ISSOCK(api.st_mode) and api.st_uid==os.getuid() and stat.S_IMODE(api.st_mode)==0o600 and before['socket']==[api.st_dev,api.st_ino],'exact private bound listener required')
        raw=Path(f"/proc/{before['pid']}/stat").read_text();head,tail=raw.rsplit(') ',1);fields=tail.split();record['publicLifetimeBefore']={'pid':int(head.split(' ',1)[0]),'start':int(fields[19]),'state':fields[0]}
        require(record['publicLifetimeBefore']['pid']==before['pid'] and record['publicLifetimeBefore']['start']==before['start'] and fields[0] in ('R','S','D','T','t','K','W','P','I'),'exact current public owner execution lifetime required')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
            connection.settimeout(2);connection.connect(f'/proc/self/fd/{descriptor}/api.sock')
            pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));record['peer']={'pid':pid,'uid':uid,'gid':gid}
            require(pid==before['pid'] and uid==os.getuid(),'actual API peer changed')
            connection.sendall(b'{"command":"state"}\n');data=b''
            while b'\n' not in data:
                part=connection.recv(8193-len(data));require(bool(part) and len(data)+len(part)<=8192,'bounded actual state response required');data+=part
            reply=json.loads(data.split(b'\n',1)[0]);record['stateReply']=reply
            require(reply.get('ok') is True and reply.get('actors')==[] and reply.get('pendingReceipts')==[],'actual recovered API still has live/pending actor authority')
        after,after_inode=owner_read();record['ownerAfter']=after;record['ownerInodeAfter']=after_inode;record['rootAfter']=projection(root.lstat());record['lockAfter']=projection(os.stat('runtime.lock',dir_fd=descriptor,follow_symlinks=False));record['socketAfter']=projection(os.stat('api.sock',dir_fd=descriptor,follow_symlinks=False))
        require(before==after and before_inode==after_inode and record['rootBefore']==record['rootAfter'] and record['lockBefore']==record['lockAfter'] and record['socketBefore']==record['socketAfter'],'current runtime/socket/owner witness changed')
        raw=Path(f"/proc/{pid}/stat").read_text();head,tail=raw.rsplit(') ',1);fields=tail.split();record['publicLifetimeAfter']={'pid':int(head.split(' ',1)[0]),'start':int(fields[19]),'state':fields[0]}
        require(record['publicLifetimeAfter']['pid']==before['pid'] and record['publicLifetimeAfter']['start']==before['start'] and fields[0] in ('R','S','D','T','t','K','W','P','I'),'actual API peer lifetime changed')
        record['confirmed']=True;return record
    except BaseException as error:record['error']=repr(error);raise
    finally:
        if lock is not None:os.close(lock)
        if descriptor is not None:os.close(descriptor)
        fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        with os.fdopen(fd,'w') as output:json.dump(record,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
