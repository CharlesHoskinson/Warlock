"""QA-only one-shot lost release; import and run the exact built real daemon.

No authority request, proof, read or effect is synthesized by this wrapper.
"""
import hashlib,importlib.util,json,os,pathlib,stat,sys

def unique(pairs):
    result={}
    for name,value in pairs:
        if name in result:raise ValueError('Duplicate QA fault field')
        result[name]=value
    return result

def private(fd,directory=False):
    value=os.fstat(fd)
    if value.st_uid!=os.getuid() or stat.S_IMODE(value.st_mode)!=(0o700 if directory else 0o600) or not (stat.S_ISDIR(value.st_mode) if directory else stat.S_ISREG(value.st_mode) and value.st_nlink==1):raise ValueError('Unsafe QA fault storage')

def raw_at(directory,name,limit):
    try:fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
    except FileNotFoundError:return None
    try:
        private(fd)
        data=bytearray()
        while len(data)<=limit:
            part=os.read(fd,min(65536,limit+1-len(data)))
            if not part:break
            data.extend(part)
        if len(data)>limit:raise ValueError('QA fault byte limit')
        return json.loads(data,object_pairs_hook=unique)
    finally:os.close(fd)

class OneShotReleaseFault:
    def __init__(self,config):
        if set(config)!=set(['schema','campaignId','daemonPath','daemonSHA256','markerDirectory','runtime','instance']) or type(config['schema']) is not int or config['schema']!=1:raise ValueError('QA fault configuration')
        for name in ['daemonPath','markerDirectory','runtime']:
            p=pathlib.Path(config[name])
            if not p.is_absolute() or p.resolve()!=p:raise ValueError('QA fault canonical path')
        if not isinstance(config['campaignId'],str) or len(config['campaignId'])!=32 or any(c not in '0123456789abcdef' for c in config['campaignId']):raise ValueError('QA campaign identity')
        if not isinstance(config['instance'],str) or not config['instance'] or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in config['instance']):raise ValueError('QA instance')
        if hashlib.sha256(pathlib.Path(config['daemonPath']).read_bytes()).hexdigest()!=config['daemonSHA256']:raise ValueError('Built daemon changed')
        self.config=dict(config);self.poisoned=False

    def intercept(self,frame,forward,error_type):
        if self.poisoned:raise ValueError('QA fault requires correction')
        if not isinstance(frame,dict) or frame.get('kind')!='host-reservation-released':return forward(frame)
        c=self.config;directory=None;fd=None
        try:
            directory=os.open(c['markerDirectory'],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);private(directory,True)
            used=raw_at(directory,'lost-release.json',1048576)
            if used is not None:
                if set(used)!=set(['schema','kind','campaignId','daemonSHA256','record','certificate','originalRelease']) or type(used['schema']) is not int or used['schema']!=1 or used['kind']!='qa-release-output-lost' or used['campaignId']!=c['campaignId'] or used['daemonSHA256']!=c['daemonSHA256']:raise ValueError('QA fault marker mismatch')
                return forward(frame)
            if set(frame)!=set(['protocolVersion','kind','binding','record','release']) or type(frame['protocolVersion']) is not int or frame['protocolVersion']!=3 or set(frame['release'])!=set(['id','proof','observation']):raise ValueError('Actual release frame shape')
            # Read through the actual built helper's private-file validation,
            # without acquiring its lifetime writer lock or altering either file.
            from recovery_journal import Journal
            from retirement_ledger import release_payload
            bound=frame['binding'];record=frame['record'];release=frame['release']
            payload=release_payload(record,release['proof'],release['observation'])
            if bound!=release['proof']['binding']:raise ValueError('Current release binding')
            namespace=Journal.namespace_path(c['runtime'],c['instance'],bound['lifetime'])
            store=os.open(namespace,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:
                private(store,True)
                sidecar=raw_at(store,'release-deliveries-v1.json',1048576);parent=raw_at(store,'ledger-v6.json',1048576)
            finally:os.close(store)
            cert=next((v for v in sidecar['certificates'] if v['record']==record and {k:v[k] for k in ['id','proof','observation']}==release),None)
            if cert is None:raise ValueError('Release has no durable current certificate')
            payload['anchorId']=cert['anchorId']
            if cert['id']!=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest():raise ValueError('Certificate digest')
            original=next((v for v in parent['releases'] if v['id']==cert['anchorId'] and v['record']==record and v['phase']=='Released'),None)
            if original is None:raise ValueError('Release original archive anchor')
            marker={'schema':1,'kind':'qa-release-output-lost','campaignId':c['campaignId'],'daemonSHA256':c['daemonSHA256'],'record':record,'certificate':cert,'originalRelease':original}
            data=json.dumps(marker,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
            fd=os.open('lost-release.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory);offset=0
            while offset<len(data):
                try:n=os.write(fd,data[offset:])
                except InterruptedError:continue
                if n<=0:raise OSError('QA marker no write progress')
                offset+=n
            os.fsync(fd);closing=fd;fd=None;os.close(closing);os.fsync(directory)
        except BaseException:self.poisoned=True;raise
        finally:
            if fd is not None:os.close(fd)
            if directory is not None:os.close(directory)
        # Mark the real writer closed so run() cannot emit a followup frame on
        # this intentionally failed lane. Main exits; a user reconnect is needed.
        raise error_type('QA lost real release before wire publication')

def main():
    fault_path=os.environ['ELM_QA_RELEASE_FAULT_CONFIG']
    path=pathlib.Path(fault_path);directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:private(directory,True);config=raw_at(directory,path.name,4096)
    finally:os.close(directory)
    fault=OneShotReleaseFault(config);daemon_path=pathlib.Path(config['daemonPath']);sys.path.insert(0,str(daemon_path.parent))
    spec=importlib.util.spec_from_file_location('qa_exact_built_daemon',daemon_path);daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)
    forward=daemon.send
    def send(frame):
        try:return fault.intercept(frame,forward,daemon.OutputFailure)
        except daemon.OutputFailure:daemon.output_writer.poisoned=True;raise
    daemon.send=send
    sys.argv=[str(daemon_path),sys.argv[1]]
    return daemon.run()
if __name__=='__main__':raise SystemExit(main())
