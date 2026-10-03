"""Explicit descriptor keeper owner; no launch on import.

Only CPU helper tests instantiate this source-stage primitive. Product wiring
must record this snapshot through the service journal before any launch gate.
"""
from copy import deepcopy
from contextlib import nullcontext
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import uuid
from helper_keeper import send,receive
from keeper_actor_ledger import digest,checked_intent
from recovery_resources import SEALS,material_fd,material_path,process_start


def keeper_source():
    ledger=Path(__file__).with_name('keeper_actor_ledger.py').read_bytes()
    keeper=Path(__file__).with_name('helper_keeper.py').read_bytes()
    keeper=keeper.replace(b'from keeper_actor_ledger import ActorLedger,observe_registration,verify_freeze,verify_native_return,MAX_LEDGER_BYTES,ENV_NAMES,material\n',b'')
    return ledger+b'\n'+keeper+b'''\nif __name__=='__main__':\n import sys\n options=json.loads(sys.argv[2]);fd=int(sys.argv[1])\n options['keeper_start']=int(Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19])\n serve(socket.socket(fileno=fd),**options)\n'''

class Keeper:
    def __init__(self,root,env,record,reservation_lock=None,*,actor_record=None):
        self.root=Path(root);info=self.root.lstat()
        if self.root.resolve()!=self.root.absolute() or not self.root.is_dir() or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('exact private keeper root required')
        self.reservation_lock=reservation_lock or nullcontext()
        self.env=dict(env);self.record=record;self.actor_record=actor_record;self.actor_jobs={};self.actor_freezes={};self.actor_revisions={};self.actor_fault=False;self.lock=threading.RLock();self.jobs={};self.children={};self.closed=False
        self.nonce=uuid.uuid4().hex;self.identity=[info.st_dev,info.st_ino]
        parent,child=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        parent.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1);parent.settimeout(5)
        child.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.connection=parent;self.process=None;self.ownership=None
        script=os.memfd_create('motion-owned-descriptor-keeper',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
        try:
            code=keeper_source()
            os.write(script,code);os.fchmod(script,0o400);fcntl.fcntl(script,fcntl.F_ADD_SEALS,SEALS)
            options={'service_pid':os.getpid(),'service_start':process_start(os.getpid()),'nonce':self.nonce,'root':str(self.root),'root_identity':self.identity}
            launcher=str(Path(sys.executable).resolve())
            argv=[launcher,f'/proc/self/fd/{script}',str(child.fileno()),json.dumps(options,sort_keys=True,separators=(',',':'))]
            self.process=subprocess.Popen(argv,env=self.env,pass_fds=(child.fileno(),script),start_new_session=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            child.close();start=process_start(self.process.pid)
            self.ownership={'pid':self.process.pid,'start':start,'uid':os.getuid(),'launcher':material_path(launcher),'script':material_fd(script,sealed=True),'scriptFD':script,'argv':argv,
                'environment':{k:self.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')},
                'nonce':self.nonce,'root':str(self.root),'rootIdentity':self.identity,'servicePID':os.getpid(),'serviceStart':options['service_start'],'phase':'live'}
            ready,fd=receive(parent,self.process.pid,os.getuid())
            if fd is not None:os.close(fd);raise ValueError('keeper ready cannot transfer descriptor')
            if ready!={'event':'keeperReady','pid':self.process.pid,'start':start,'nonce':self.nonce}:raise ValueError('exact keeper ready identity required')
            self.verify();self.publish()
        except BaseException:
            parent.close();child.close()
            if self.process is not None:
                try:self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=2)
                self.process.stderr.close()
            raise
        finally:os.close(script)
    def snapshot(self):return {'keeper':deepcopy(self.ownership),'jobs':deepcopy(list(self.jobs.values()))}
    def publish(self):self.record(self.snapshot())
    def verify(self):
        row=self.ownership;pid=row['pid']
        if process_start(pid)!=row['start']:raise ValueError('exact keeper lifetime unavailable')
        if material_path(f'/proc/{pid}/exe')!=row['launcher']:raise ValueError('keeper launcher material changed')
        if material_path(f"/proc/{pid}/fd/{row['scriptFD']}",sealed=True)!=row['script']:raise ValueError('keeper sealed script changed')
        if Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]!=[v.encode() for v in row['argv']]:raise ValueError('keeper exact argv changed')
        if process_start(pid)!=row['start']:raise ValueError('keeper lifetime changed during verification')
    def exchange(self,packet,fd=None):
        self.verify();send(self.connection,packet,fd)
        reply,received=receive(self.connection,self.process.pid,os.getuid())
        if received is not None:os.close(received);raise ValueError('unexpected keeper response descriptor')
        if reply is None or reply.get('ok') is not True:raise ValueError('keeper refused ownership command')
        return reply
    def register(self,ownership,*,kind,actor=None,process=None):
        with self.reservation_lock,self.lock:
            if self.closed:raise RuntimeError('keeper is closed')
            if self.actor_fault:raise ValueError('actor ledger durability failed; new launch refused')
            job=uuid.uuid4().hex;pid=ownership['pid'];start=ownership['start']
            fd=os.pidfd_open(pid,0)
            try:
                if process_start(pid)!=start:raise ValueError('helper lifetime changed before descriptor registration')
                reply=self.exchange({'command':'register','job':job,'pid':pid,'start':start,'kind':kind,'actor':actor,'ownership':deepcopy(ownership)},fd)
                if reply!={'ok':True,'job':job}:raise ValueError('keeper registered different job')
            finally:os.close(fd)
            if process is not None:
                if process.pid!=pid:raise ValueError('exact direct Popen identity required')
                self.children[job]=process
            self.jobs[job]={'job':job,'kind':kind,'actor':actor,'phase':'gated','ownership':deepcopy(ownership)}
            self.actor_jobs[job]={'job':job,'kind':kind,'actor':actor,'pid':pid,'start':start,'sourceSHA256':digest(ownership),'phase':'gated','returned':None,'uncertain':False}
            self.actor_changed(actor)
            if self.actor_record is not None:self.actor_publish()
            self.publish() # May throw. Caller keeps the launch gate closed.
            return job
    def released(self,job):
        with self.reservation_lock,self.lock:
            if self.actor_fault:raise ValueError('actor ledger durability failed; release refused')
            if self.exchange({'command':'released','job':job})!={'ok':True,'job':job}:raise ValueError('different released ledger job')
            self.jobs[job]['phase']='released';self.actor_jobs[job]['phase']='released';self.actor_changed(self.actor_jobs[job]['actor'])
            if self.actor_record is not None:self.actor_publish()
            self.publish()
    def complete(self,job):
        with self.reservation_lock,self.lock:
            reply=self.exchange({'command':'complete','job':job})
            if reply!={'ok':True,'job':job}:raise ValueError('keeper completed different job')
            self.actor_jobs[job]['phase']='closed';self.actor_changed(self.actor_jobs[job]['actor'])
            if self.actor_record is not None:self.actor_publish()
            if self.jobs[job]['kind'] in ('native-effect','native-export') and self.actor_jobs[job]['returned'] is None:
                # Physical closure is separate from the durable semantic reply.
                # Keep the ordinary registry's unresolved released phase so even
                # inherited restart guards cannot treat this result gap as closed.
                self.jobs[job]['groupEmpty']=True;self.children.pop(job,None);self.publish()
                return
            self.jobs[job]['phase']='closed';self.jobs[job]['groupEmpty']=True;self.publish()
            del self.jobs[job];self.children.pop(job,None);self.publish()
    def actor_changed(self,actor):
        if actor is not None:self.actor_revisions[str(actor)]=self.actor_revisions.get(str(actor),0)+1
    def actor_snapshot(self):
        return {'jobs':deepcopy(self.actor_jobs),'freezes':deepcopy(self.actor_freezes),'revisions':deepcopy(self.actor_revisions),'fault':self.actor_fault}
    def actor_publish(self):
        if self.actor_record is None:raise ValueError('durable actor ledger service binding is required')
        try:self.actor_record(self.actor_snapshot())
        except BaseException:self.actor_fault=True;raise
    def actor_rows(self,actor):return [deepcopy(self.actor_jobs[k]) for k in sorted(self.actor_jobs) if self.actor_jobs[k]['actor']==actor]
    def checked_actor_witness(self,actor,witness):
        row=self.ownership
        expected={'keeperPID':row['pid'],'keeperStart':row['start'],'nonce':row['nonce'],'root':row['root'],'rootIdentity':row['rootIdentity'],
            'servicePID':row['servicePID'],'serviceStart':row['serviceStart'],'environment':row['environment'],'sourceSHA256':row['script']['sha256']}
        wanted={'issuer':expected,'intent':self.actor_freezes.get(str(actor)),'revision':self.actor_revisions.get(str(actor),0),
            'jobCount':len(self.actor_rows(actor)),'ledgerSHA256':digest(self.actor_rows(actor))}
        if self.actor_fault or digest(witness)!=digest(wanted):raise ValueError('authenticated actor witness differs from complete owned inventory')
        return deepcopy(witness)
    def freeze_actor(self,intent):
        with self.reservation_lock,self.lock:
            if self.actor_record is None or self.actor_fault:raise ValueError('durable current actor ledger binding missing/failed')
            intent=checked_intent(intent);actor=intent['actor'];old=self.actor_freezes.get(str(actor))
            reply=self.exchange({'command':'actor-freeze','intent':intent})
            if set(reply)!={'ok','witness'}:raise ValueError('complete authenticated freeze witness required')
            if old is None:self.actor_freezes[str(actor)]=deepcopy(intent);self.actor_changed(actor)
            elif old!=intent:raise ValueError('conflicting actor freeze')
            proof=self.checked_actor_witness(actor,reply['witness']);self.actor_publish();return proof
    def actor_witness(self,actor):
        with self.reservation_lock,self.lock:
            reply=self.exchange({'command':'actor-witness','actor':actor,'expected':None})
            if set(reply)!={'ok','witness'}:raise ValueError('complete authenticated actor witness required')
            return self.checked_actor_witness(actor,reply['witness'])
    def attest_actor(self,actor,expected):
        with self.reservation_lock,self.lock:
            self.checked_actor_witness(actor,expected)
            reply=self.exchange({'command':'actor-attest','actor':actor,'expected':expected})
            if set(reply)!={'ok','witness'}:raise ValueError('complete authenticated actor terminal witness required')
            proof=self.checked_actor_witness(actor,reply['witness']);self.actor_publish();return proof
    def native_returned(self,job,proof):
        with self.reservation_lock,self.lock:
            if self.exchange({'command':'native-returned','job':job,'proof':proof})!={'ok':True,'job':job}:raise ValueError('exact durable native result missing')
            self.actor_jobs[job]['returned']=deepcopy(proof);self.actor_changed(self.actor_jobs[job]['actor']);self.actor_publish()
            if job in self.jobs and self.actor_jobs[job]['phase']=='closed':
                self.jobs[job]['phase']='closed';self.jobs[job]['groupEmpty']=True;self.publish()
                del self.jobs[job];self.children.pop(job,None);self.publish()
    def native_uncertain(self,job):
        with self.reservation_lock,self.lock:
            if self.exchange({'command':'native-uncertain','job':job})!={'ok':True,'job':job}:raise ValueError('exact native uncertainty ledger missing')
            self.actor_jobs[job]['uncertain']=True;self.actor_changed(self.actor_jobs[job]['actor']);self.actor_publish()
    def stop(self):
        with self.reservation_lock,self.lock:
            if self.closed:return
            if self.jobs:raise ValueError('normal keeper stop refuses outstanding jobs')
            self.exchange({'command':'stop'});self.connection.close();self.process.wait(timeout=5)
            if self.process.returncode!=0:raise RuntimeError('keeper failed normal closure: '+self.process.stderr.read(8193))
            self.process.stderr.close();terminal=self.read_terminal()
            if terminal['normalStop'] is not True:raise ValueError('keeper normal stop proof missing')
            self.ownership['phase']='closed';self.ownership['terminal']=terminal;self.closed=True;self.publish()
    def abort(self):
        # Exact retained groups are closed by the keeper. Reap only this owner's
        # direct Popen children so exited leaders cannot impede group-empty proof.
        with self.reservation_lock,self.lock:
            self.connection.close()
            for child in self.children.values():child.wait(timeout=5)
            self.process.wait(timeout=5)
            if self.process.returncode!=0:raise RuntimeError('keeper failed exact crash cleanup: '+self.process.stderr.read(8193).decode())
            self.process.stderr.close();terminal=self.read_terminal()
            self.ownership['phase']='closed';self.ownership['terminal']=terminal;self.closed=True;self.publish()
            return terminal
    def read_terminal(self):
        return read_terminal(self.ownership)
    def detach(self):
        # Crash simulation/real service exit: keeper retains its own descriptors.
        self.connection.close()

def read_terminal(ownership):
    root=Path(ownership['root']);info=root.lstat()
    if [info.st_dev,info.st_ino]!=ownership['rootIdentity'] or info.st_uid!=os.getuid() or info.st_mode&0o077 or root.resolve()!=root.absolute():raise ValueError('keeper terminal root changed')
    path=root/('keeper-'+ownership['nonce']+'.json')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        if before.st_uid!=os.getuid() or before.st_mode&0o077 or before.st_size>1048576:raise ValueError('private bounded keeper terminal required')
        data=os.read(fd,1048577);after=os.fstat(fd)
        if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('keeper terminal changed while reading')
    finally:os.close(fd)
    body=json.loads(data)
    expected={'keeperPID':ownership['pid'],'keeperStart':ownership['start'],'nonce':ownership['nonce'],'rootIdentity':ownership['rootIdentity'],'servicePID':ownership['servicePID'],'serviceStart':ownership['serviceStart'],'allGroupsEmpty':True}
    if any(type(body.get(k)) is not type(v) or body.get(k)!=v for k,v in expected.items()):raise ValueError('terminal belongs to another keeper/service/root or incomplete groups')
    return body

def checked_keeper(row,*,root,environment):
    from recovery_intent import positive
    from recovery_resources import checked_material
    import re
    expected={'pid','start','uid','launcher','script','scriptFD','argv','environment','nonce','root','rootIdentity','servicePID','serviceStart','phase'}
    if not isinstance(row,dict) or set(row)-{'terminal'}!=expected:raise ValueError('complete typed keeper ownership required')
    for field in ('pid','start','servicePID','serviceStart'):positive(row[field])
    if type(row['uid']) is not int or row['uid']!=os.getuid():raise ValueError('keeper exact UID differs')
    if type(row['scriptFD']) is not int or row['scriptFD']<0:raise ValueError('keeper inherited script descriptor invalid')
    if not isinstance(row['nonce'],str) or re.fullmatch('[0-9a-f]{32}',row['nonce']) is None:raise ValueError('keeper nonce invalid')
    if row['root']!=str(root) or row['environment']!=environment or row['phase'] not in ('live','closed'):raise ValueError('keeper belongs to another runtime/environment')
    inode=row['rootIdentity']
    if not isinstance(inode,list) or len(inode)!=2 or any(type(v) is not int or v<0 for v in inode) or inode[1]<1:raise ValueError('typed keeper root identity required')
    checked_material(row['script'],sealed=True);checked_material(row['launcher'],sealed=False)
    if row['script']['sha256']!=hashlib.sha256(keeper_source()).hexdigest():raise ValueError('keeper executable script is not this reviewed implementation')
    argv=row['argv']
    if not isinstance(argv,list) or len(argv)!=4 or any(type(v) is not str for v in argv) or argv[1]!=f"/proc/self/fd/{row['scriptFD']}" or not argv[2].isdigit():raise ValueError('keeper exact argv binding required')
    options=json.loads(argv[3]);expected_options={'service_pid':row['servicePID'],'service_start':row['serviceStart'],'nonce':row['nonce'],'root':row['root'],'root_identity':inode}
    if options!=expected_options or any(type(options.get(k)) is not type(v) for k,v in expected_options.items()):raise ValueError('keeper invocation differs from durable runtime ownership')
    return row

def verify_keeper(row):
    pid=row['pid']
    if process_start(pid)!=row['start']:raise ValueError('keeper exact lifetime unavailable')
    if material_path(f'/proc/{pid}/exe')!=row['launcher'] or material_path(f"/proc/{pid}/fd/{row['scriptFD']}",sealed=True)!=row['script']:raise ValueError('keeper actual launcher/script differs')
    if Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]!=[v.encode() for v in row['argv']]:raise ValueError('keeper exact argv differs')
    raw=Path(f'/proc/{pid}/environ').read_bytes();env=dict(part.split(b'=',1) for part in raw.split(b'\0') if b'=' in part)
    if any(env.get(k.encode())!=v.encode() for k,v in row['environment'].items()):raise ValueError('keeper actual selected environment differs')
    if process_start(pid)!=row['start']:raise ValueError('keeper lifetime changed during material observation')

def await_terminal(ownership,*,timeout=5):
    import select
    # Retained pidfd binds this wait to the archived lifetime, even if its numeric
    # PID becomes another process while waiting. Never signal this keeper.
    if process_start(ownership['pid'])==ownership['start']:
        try:fd=os.pidfd_open(ownership['pid'],0)
        except ProcessLookupError:fd=None
        if fd is not None:
            try:
                poll=select.poll();poll.register(fd,select.POLLIN)
                if process_start(ownership['pid'])==ownership['start'] and not poll.poll(0):
                    verify_keeper(ownership)
                    if not poll.poll(int(timeout*1000)):raise RuntimeError('old descriptor keeper still alive; restart remains quarantined')
            finally:os.close(fd)
    terminal=read_terminal(ownership)
    if type(terminal.get('normalStop')) is not bool or type(terminal.get('registrations')) is not int or terminal['registrations']<0 or type(terminal.get('closedNs')) is not int or terminal['closedNs']<1:raise ValueError('typed complete keeper terminal required')
    jobs=terminal.get('jobs')
    if not isinstance(jobs,list) or len(jobs)>512:raise ValueError('bounded complete keeper terminal jobs required')
    seen={}
    from recovery_intent import positive
    import re
    for job in jobs:
        if not isinstance(job,dict) or not isinstance(job.get('job'),str) or not re.fullmatch('[0-9a-f]{32}',job['job']) or job['job'] in seen:raise ValueError('typed distinct terminal jobs required')
        positive(job.get('pid'));positive(job.get('start'))
        if job.get('groupEmpty') is not True or type(job.get('normalCompletion')) is not bool:raise ValueError('exact job group closure not proven')
        seen[job['job']]=job
    return terminal,seen
