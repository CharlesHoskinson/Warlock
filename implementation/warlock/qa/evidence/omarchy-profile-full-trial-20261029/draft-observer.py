"""Bound an owned GTK draft to a private native window; no process starts on import.

The caller supplies its already-reviewed six-second wait and physical input and
owns launch/cleanup. This does not itself establish visible pixels or AT.
"""
import hashlib, json, os, signal
from pathlib import Path

TITLE='Warlock recovery owned draft'
FIXTURE=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/omarchy-recovery-trial-v1/draft-fixture-terra-1/owned-draft.py')
FIXTURE_SHA='48f93ea51b6d1c75c8c7538c322d09381b9dcf1620331e91756fedc7fb549240'
GTK_PROVIDERS={
 '/usr/lib/libgtk-3.so.0.2420.32':'1bf8b70cc6779ab9e8e3a558ad58e63e8aed4f30216619ff25d0cdb010f8975a',
 '/usr/lib/libgdk-3.so.0.2420.32':'7db98bfcc2f0f7e278c4f82391fbc3bf47b011c91c587c8cc168ef097d7f2940',
}
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def start(pid):return Path('/proc',str(pid),'stat').read_text().rpartition(') ')[2].split()[19]
def mapped(pid):
    paths={}
    for line in Path('/proc',str(pid),'maps').read_text().splitlines():
        parts=line.split(None,5)
        if len(parts)==6 and parts[5].startswith('/') and not parts[5].endswith(' (deleted)'):
            dev=parts[3].split(':'); identity=(int(dev[0],16),int(dev[1],16),int(parts[4]))
            if parts[5] in paths and paths[parts[5]]!=identity:raise RuntimeError('Ambiguous mapped provider')
            paths[parts[5]]=identity
    return paths
def live_mapping(path, identity):
    st=os.stat(path)
    if (os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)!=identity:raise RuntimeError('Mapped object no longer matches path: '+path)
    return {'sha256':digest(path),'device':[identity[0],identity[1]],'inode':identity[2]}
class Draft:
    def __init__(self,session,client,wait,env,log,python_sha):
        if digest(FIXTURE)!=FIXTURE_SHA:raise RuntimeError('Draft fixture changed')
        self.s,self.client,self.wait,self.log=session,client,wait,Path(log)
        draft_env=dict(env,GDK_BACKEND='wayland')
        self.proc=session.host.launch('recovery-owned-draft',['/usr/bin/python3','-B',str(FIXTURE)],env=draft_env)
        self.pid=self.proc.pid;self.start=start(self.pid);self.pidfd=os.pidfd_open(self.pid,0)
        self.live()
        def identify():
            self.live()
            clients=[r for r in self.s.data('clients') if r.get('title')==TITLE and r.get('pid')==self.pid]
            roots=[r for r in self.client.snapshot('720')['windows'] if r.get('label')==TITLE]
            if len(clients)==len(roots)==1:return clients[0],roots[0]
            return None
        surface,root=wait(identify)
        self.address=surface['address'];self.incarnation=root['incarnation']
        if Path('/proc',str(self.pid),'exe').resolve()!=Path('/usr/bin/python3').resolve() or digest(Path('/proc',str(self.pid),'exe'))!=python_sha:raise RuntimeError('Draft Python executable mismatch')
        paths=mapped(self.pid)
        gi=[p for p in paths if '/gi/' in p and Path(p).name.startswith('_gi.') and p.endswith('.so')]
        if len(gi)!=1:raise RuntimeError('Actual Python GI provider mapping not unique')
        for path,expected in GTK_PROVIDERS.items():
            if path not in paths or live_mapping(path,paths[path])['sha256']!=expected:raise RuntimeError('GTK provider absent or changed: '+path)
        typelibs=sorted(p for p in paths if p.endswith('.typelib') and ('Gtk-3.0' in p or 'Gdk-3.0' in p))
        if len(typelibs)!=2:raise RuntimeError('Actual GTK/GDK typelib mappings not both observed')
        self.providers={p:live_mapping(p,paths[p]) for p in sorted(set(GTK_PROVIDERS)|set(typelibs)|set(gi))}
        self.checkpoints=[]
    def live(self):
        if self.proc.poll() is not None or start(self.pid)!=self.start:raise RuntimeError('Draft process incarnation changed')
    def identity(self):
        self.live()
        clients=[r for r in self.s.data('clients') if r.get('title')==TITLE and r.get('pid')==self.pid]
        roots=[r for r in self.client.snapshot('721')['windows'] if r.get('label')==TITLE]
        if len(clients)!=1 or len(roots)!=1 or clients[0].get('address')!=self.address or roots[0].get('incarnation')!=self.incarnation:raise RuntimeError('Draft native window incarnation changed')
    def send_signal(self,signum):
        self.identity()
        signal.pidfd_send_signal(self.pidfd,signum,None,0)
    def close_pidfd(self):
        if self.pidfd is not None:
            os.close(self.pidfd);self.pidfd=None
    def records(self):
        if not self.log.exists():return []
        raw=self.log.read_text();complete=raw[:raw.rfind('\n')+1]
        return [json.loads(line) for line in complete.splitlines() if line.startswith('{')]
    def type_and_verify(self,physical,commands,expected):
        # Caller targets the actual native surface using the reviewed physical input path.
        self.identity()
        active=self.s.data('activewindow')
        if active.get('pid')!=self.pid or active.get('address')!=self.address:raise RuntimeError('Draft does not have native focus before typing')
        rows=self.records();previous=max((r['sequence'] for r in rows),default=0)
        physical(commands)
        def changed():
            self.identity()
            active=self.s.data('activewindow')
            if active.get('pid')!=self.pid or active.get('address')!=self.address:raise RuntimeError('Draft lost native focus during typing')
            found=[r for r in self.records() if r.get('kind')=='changed' and r.get('sequence',0)>previous and r.get('pid')==self.pid and str(r.get('processStart'))==self.start and r.get('focused') is True and r.get('text')==expected]
            return found[-1] if found else None
        return self.wait(changed)
    def snapshot(self,label,expected):
        self.identity();rows=self.records();previous=max((r['sequence'] for r in rows),default=0)
        self.send_signal(signal.SIGUSR1)
        def receipt():
            self.identity()
            found=[r for r in self.records() if r.get('kind')=='snapshot' and r.get('sequence',0)>previous and r.get('pid')==self.pid and str(r.get('processStart'))==self.start]
            return found[0] if found else None
        row=self.wait(receipt)
        if row.get('text')!=expected:raise RuntimeError('Draft buffer differs at '+label)
        self.checkpoints.append({'label':label,'record':row,'address':self.address,'incarnation':self.incarnation})
        return row
