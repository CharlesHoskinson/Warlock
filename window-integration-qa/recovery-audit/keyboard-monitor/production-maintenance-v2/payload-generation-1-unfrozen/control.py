"""Exact-instance production maintenance. Import has no session or load effects."""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import argparse,fcntl,hashlib,json,os,re,socket,stat,subprocess

class Refused(RuntimeError): pass

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def start_time(pid): return int(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19])
def run(command,env):
    result=subprocess.run(command,env=env,capture_output=True,timeout=4)
    if len(result.stdout)>1048576 or len(result.stderr)>16384: raise Refused('bounded IPC reply exceeded')
    if result.returncode: raise Refused('IPC failed: '+result.stderr[-4096:].decode(errors='replace'))
    return result.stdout.decode('utf-8').strip()

def select(rows,explicit=None,environment=None):
    # An invalid supplied target cannot fall through to another instance.
    preferred=explicit if explicit is not None else environment
    chosen=[row for row in rows if row['instance']==preferred] if preferred is not None else rows
    if len(chosen)!=1: raise Refused('exact compositor unavailable or ambiguous')
    row=chosen[0]
    if not re.fullmatch(r'[a-f0-9]{40}_[0-9]+_[0-9]+',row['instance']): raise Refused('invalid compositor signature')
    return row

def artifact(manifest,base,approved=True):
    if approved and not all(manifest.get(k) is True for k in ('nativeAccepted','productionAccepted','privateProbeAbsent')):
        raise Refused('production native acceptance/review missing')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',manifest.get('packageID','')): raise Refused('invalid package ID')
    relative=Path(manifest['library'])
    if relative.is_absolute() or '..' in relative.parts: raise Refused('artifact must be an owned package-relative path')
    path=base/relative
    if path.is_symlink() or path.resolve()!=path.absolute(): raise Refused('symlink artifact refused')
    row=path.stat()
    if not stat.S_ISREG(row.st_mode) or row.st_uid!=os.getuid() or row.st_mode&0o022: raise Refused('unsafe artifact ownership/mode')
    if not re.fullmatch(r'[a-f0-9]{64}',manifest.get('sha256','')) or sha(path)!=manifest['sha256']: raise Refused('immutable artifact hash mismatch')
    return path,row

@dataclass(frozen=True)
class Identity:
    signature:str
    pid:int
    start:int
    device:int
    inode:int

class Control:
    def __init__(self,manifest_path,explicit=None,env=None,transport=run,approved=True):
        self.manifest_path=Path(manifest_path).absolute();self.base=self.manifest_path.parent
        self.manifest=json.loads(self.manifest_path.read_text());self.manifest_hash=sha(self.manifest_path)
        self.env=dict(os.environ if env is None else env);self.transport=transport;self.approved=approved
        self.library,_=artifact(self.manifest,self.base,approved)
        self.runtime=Path(self.env.get('XDG_RUNTIME_DIR',''))
        canonical=Path(f'/run/user/{os.getuid()}')
        if self.runtime!=canonical:
            # QA proof is explicit; production never redirects itself to a fixture.
            if self.env.get('HYPR_A11Y_BRIDGE_PRIVATE')!='1':raise Refused('noncanonical runtime refused')
            import importlib.util
            helper=Path('/home/hoskinson/window-integration-qa/qa_launch.py')
            module=importlib.util.module_from_spec(spec:=importlib.util.spec_from_file_location('maintenance_qa_launch',helper));spec.loader.exec_module(module)
            module.require_qa_scope();module.verify_runtime(self.runtime)
        elif 'HYPR_A11Y_BRIDGE_PRIVATE' in self.env:raise Refused('private flag cannot select main session')
        self._directory(self.runtime)
        expected='unix:path='+str(self.runtime/'bus');address=self.env.get('DBUS_SESSION_BUS_ADDRESS','')
        if address!=expected and not re.fullmatch(re.escape(expected)+r',guid=[a-f0-9]{32}',address): raise Refused('wrong session bus')
        bus=(self.runtime/'bus').lstat()
        if not stat.S_ISSOCK(bus.st_mode) or bus.st_uid!=os.getuid():raise Refused('unsafe session bus socket')
        self.bus_identity=(bus.st_dev,bus.st_ino)
        rows=json.loads(self.transport(['hyprctl','instances','-j'],self.env))
        row=select(rows,explicit,self.env.get('HYPRLAND_INSTANCE_SIGNATURE'))
        self.env['HYPRLAND_INSTANCE_SIGNATURE']=row['instance']
        self.socket=self.runtime/'hypr'/row['instance']/'.socket.sock'
        sock=self.socket.lstat();self.identity=Identity(row['instance'],int(row['pid']),start_time(int(row['pid'])),sock.st_dev,sock.st_ino)
        self._guard()
    @staticmethod
    def _directory(path):
        row=path.lstat()
        if not stat.S_ISDIR(row.st_mode) or row.st_uid!=os.getuid() or stat.S_IMODE(row.st_mode)!=0o700:raise Refused('unsafe runtime directory')
    def _guard(self):
        if sha(self.manifest_path)!=self.manifest_hash:raise Refused('manifest changed during operation')
        artifact(self.manifest,self.base,self.approved);self._directory(self.runtime)
        bus=(self.runtime/'bus').lstat()
        if (bus.st_dev,bus.st_ino)!=self.bus_identity or not stat.S_ISSOCK(bus.st_mode) or bus.st_uid!=os.getuid():raise Refused('session bus changed')
        i=self.identity
        if Path(f'/proc/{i.pid}').stat().st_uid!=os.getuid() or start_time(i.pid)!=i.start:raise Refused('compositor process changed')
        row=self.socket.lstat()
        if not stat.S_ISSOCK(row.st_mode) or row.st_uid!=os.getuid() or (row.st_dev,row.st_ino)!=(i.device,i.inode):raise Refused('IPC socket changed')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as endpoint:
            endpoint.settimeout(2);endpoint.connect(str(self.socket))
            import struct
            pid,uid,_=struct.unpack('3i',endpoint.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            if (pid,uid)!=(i.pid,os.getuid()):raise Refused('IPC peer mismatch')
            endpoint.sendall(b'j/version');chunks=bytearray()
            while True:
                block=endpoint.recv(8192)
                if not block:break
                chunks.extend(block)
                if len(chunks)>65536:raise Refused('version reply exceeded bound')
            version=json.loads(chunks)
        after=self.socket.lstat()
        if (after.st_dev,after.st_ino)!=(i.device,i.inode) or version.get('commit')!=self.manifest['hyprlandCommit']:raise Refused('IPC ABI/socket changed')
    def ipc(self,*args):
        self._guard();value=self.transport(['hyprctl','-i',self.identity.signature,*args],self.env);self._guard();return value
    def plugin_rows(self):return json.loads(self.ipc('-j','plugin','list'))
    def _mapped(self):
        path,row=artifact(self.manifest,self.base,self.approved);matches=[]
        for line in Path(f'/proc/{self.identity.pid}/maps').read_text().splitlines():
            parts=line.split(maxsplit=5)
            if len(parts)==6 and parts[5]==str(path):matches.append(parts)
        if not matches:raise Refused('exact loaded artifact mapping missing')
        for parts in matches:
            major,minor=(int(v,16) for v in parts[3].split(':'))
            if int(parts[4])!=row.st_ino or os.makedev(major,minor)!=row.st_dev:raise Refused('loaded mapping identity differs')
        rows=[r for r in self.plugin_rows() if r.get('name')==self.manifest['pluginName']]
        if len(rows)!=1 or rows[0].get('version')!=self.manifest['pluginVersion']:raise Refused('unique loaded plugin identity mismatch')
    def lua(self,method,*tokens):
        if method not in ('identity','prepare_unload','capability_status'):raise Refused('unknown maintenance method')
        code='return hl.plugin.omarchy_a11y.'+method+'('+','.join(json.dumps(v,ensure_ascii=True) for v in tokens)+')'
        return json.loads(self.ipc('repl',code))
    def native_identity(self):
        self._mapped();value=self.lua('identity')
        if value.get('instance')!=self.identity.signature or value.get('packageID')!=self.manifest['packageID'] or not re.fullmatch(r'[a-f0-9]{64}',value.get('incarnation','')):raise Refused('native per-load identity differs')
        return value
    def capability_status(self,client):
        first=self.native_identity();value=self.lua('capability_status',first['instance'],first['packageID'],first['incarnation'],client)
        if any(value.get(k)!=first[k] for k in ('instance','packageID','incarnation','managerOwner')) or self.native_identity()!=first:raise Refused('capability epoch changed')
        return value
    def load(self):
        if any(row.get('name')==self.manifest['pluginName'] for row in self.plugin_rows()):raise Refused('existing bridge refused; use normal unload')
        if self.ipc('plugin','load',str(self.library))!='ok':raise Refused('normal load failed')
        return self.native_identity()
    def unload(self):
        first=self.native_identity()
        value=self.lua('prepare_unload',first['instance'],first['packageID'],first['incarnation'])
        if value.get('ready') is not True or any(value.get(k)!=first[k] for k in ('instance','packageID','incarnation','managerOwner')):raise Refused('normal retirement refused; no raw unload')
        if self.native_identity()!=first:raise Refused('plugin replaced after retirement')
        if self.ipc('plugin','unload',str(self.library))!='ok':raise Refused('unload failed; retired bridge retained')
        if any(r.get('name')==self.manifest['pluginName'] for r in self.plugin_rows()):raise Refused('plugin still loaded')
        return value
    @contextmanager
    def locked(self):
        path=self.runtime/'omarchy-a11y-maintenance.lock'
        fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            row=os.fstat(fd)
            if not stat.S_ISREG(row.st_mode) or row.st_uid!=os.getuid() or stat.S_IMODE(row.st_mode)!=0o600:raise Refused('unsafe maintenance lock')
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Refused('another managed operation is active')
            yield
        finally:os.close(fd)

def reader_intent(env):
    # Property read only. No property Set or Orca construction occurs here.
    import gi
    from gi.repository import Gio,GLib
    connection=Gio.DBusConnection.new_for_address_sync(env['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
    try:
        result=connection.call_sync('org.a11y.Bus','/org/a11y/bus','org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',('org.a11y.Status','ScreenReaderEnabled')),GLib.VariantType.new('(v)'),Gio.DBusCallFlags.NONE,2000,None)
        return result.unpack()[0]
    finally:connection.close_sync(None)

def main():
    parser=argparse.ArgumentParser(description='Normal exact-instance accessibility bridge maintenance; never starts the reader')
    parser.add_argument('action',choices=('status','load','unload','reload'));parser.add_argument('--manifest',required=True);parser.add_argument('--instance')
    args=parser.parse_args();control=Control(args.manifest,args.instance)
    with control.locked():
        before=reader_intent(control.env)
        if args.action=='status':value=control.native_identity()
        elif args.action=='reload':old=control.unload();value={'previous':old,'current':control.load()}
        else:value=getattr(control,args.action)()
        after=reader_intent(control.env)
        if before!=after:raise Refused('reader enabled intent changed externally during operation')
        print(json.dumps({'result':value,'readerEnabledBefore':before,'readerEnabledAfter':after}))
if __name__=='__main__':main()
