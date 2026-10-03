"""Actual CPU-only kernel tmpfs/VMA/FD faults; never starts a GUI client."""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import owned_metrics_data as md
from mapping_evidence import capture, validate
from runtime_inputs import mapping_authority

CHILD = r'''
import fcntl,json,mmap,os,sys
parent=sys.argv[1];name=parent+'/BrowserMetrics-ABC-'+format(os.getpid(),'X')+'.pma'
fd=os.open(name,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.ftruncate(fd,4194304)
view=mmap.mmap(fd,4194304,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE,trackfd=False)
os.unlink(name);aliases=[];extras=[];print('ready',flush=True)
for raw in sys.stdin:
 cmd=json.loads(raw)
 if cmd[0]=='quit':print('ok',flush=True);break
 if cmd[0]=='dup':extras.append(os.dup(fd))
 if cmd[0]=='mode':os.fchmod(fd,cmd[1])
 if cmd[0]=='size':os.ftruncate(fd,cmd[1])
 if cmd[0]=='flags':fcntl.fcntl(fd,fcntl.F_SETFL,fcntl.fcntl(fd,fcntl.F_GETFL)^os.O_NONBLOCK)
 if cmd[0]=='mutate':os.write(fd,b'writable-data');os.utime('/proc/self/fd/'+str(fd),ns=(1,2))
 if cmd[0]=='exec':aliases.append(mmap.mmap(fd,4194304,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_EXEC,trackfd=False))
 if cmd[0]=='replace':
  os.close(fd);n=os.open(name,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.ftruncate(n,4194304);os.unlink(name)
  if n!=fd:os.dup2(n,fd);os.close(n)
 if cmd[0]=='readonly':
  n=os.open('/proc/self/fd/'+str(fd),os.O_RDONLY);os.dup2(n,fd);os.close(n)
 if cmd[0]=='path':
  n=os.open('/proc/self/fd/'+str(fd),os.O_PATH);os.dup2(n,fd);os.close(n)
 if cmd[0]=='vma':
  view.close();view=mmap.mmap(fd,cmd[1],flags=cmd[2],prot=cmd[3],offset=cmd[4],trackfd=False)
 if cmd[0]=='close':os.close(fd);fd=-1
 print('ok',flush=True)
for m in aliases:m.close()
view.close()
for n in extras:os.close(n)
if fd>=0:os.close(fd)
'''

def ident(pid):
    return {'pid': pid, 'start': Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]}


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(dir=f'/run/user/{os.getuid()}')
        self.runtime = Path(self.temp.name)
        self.profile = self.runtime / 'browser-profile'; self.profile.mkdir(mode=0o700)
        self.parent = self.profile / 'BrowserMetrics'; self.parent.mkdir(mode=0o700)
        self.anchors = md.anchors(self.runtime, self.profile)
        self.child = subprocess.Popen([sys.executable, '-IS', '-c', CHILD, str(self.parent)],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True)
        assert self.child.stdout.readline().strip() == 'ready'
        self.browser = ident(self.child.pid); self.compositor = ident(os.getpid())
        exe = Path('/proc/self/exe').resolve()
        self.frozen = {str(exe): {'sha256': md.digest(exe.read_bytes()), 'mode': stat.S_IMODE(exe.stat().st_mode)}}
    def command(self, *args):
        self.child.stdin.write(json.dumps(args) + '\n'); self.child.stdin.flush()
        assert self.child.stdout.readline().strip() == 'ok'
    def batch(self):
        return capture([self.browser, self.compositor], lambda i: ident(i['pid']) == i,
                       lambda pid: Path(f'/proc/{pid}/maps').read_bytes(), 'CPU fixture')
    def observe(self, proof=None, batch=None, **extras):
        proof = {} if proof is None else proof
        md.observe(proof, batch or self.batch(), self.browser, self.compositor,
                   self.runtime, self.profile, self.anchors, self.frozen, lambda: None, **extras)
        return proof
    def confirm(self, proof, batch, **extras):
        md.confirm(proof, batch, self.browser, self.compositor, self.runtime,
                   self.profile, self.anchors, self.frozen, lambda: None, **extras)
    def close(self):
        self.command('quit'); self.child.wait(timeout=3)
        assert self.child.returncode == 0, self.child.stderr.read()
        self.child.stdin.close(); self.child.stdout.close(); self.child.stderr.close(); self.temp.cleanup()


class MetricsDataTest(unittest.TestCase):
    def setUp(self): self.f = Fixture()
    def tearDown(self): self.f.close()
    def test_actual_one_fd_fullsize_owned_kernel_witness_and_confirmation(self):
        b = self.f.batch(); p = self.f.observe(batch=b); self.assertTrue(p['accepted']); self.assertFalse(p['usableForInput'])
        row = p['observations'][0]; self.assertEqual(len(row['before']['matchingFDs']), 1)
        self.assertEqual(row['stableBefore'], row['stableAfter']); self.assertEqual(row['stableBefore']['fdinfo']['flags'] & os.O_ACCMODE, os.O_RDWR)
        self.f.confirm(p, b); self.assertTrue(p['usableForInput']); self.assertTrue(p['confirmedAfterDiskValidation'])
    def test_classifier_exact_root_row_only(self):
        b = self.f.batch(); p = self.f.observe(batch=b); raw = b['processes'][0]['maps']; line = p['observations'][0]['mapping']['line']
        value = md.classification(p, raw, line, self.f.browser, self.f.runtime); self.assertIsNotNone(value)
        self.assertIsNone(md.classification(p, raw, line, self.f.compositor, self.f.runtime))
        self.assertIsNone(md.classification(p, raw+'\n', line, self.f.browser, self.f.runtime))
        self.assertIsNone(md.classification(p, raw, line, self.f.browser, self.f.runtime/'other'))
    def test_exact_mapping_authority_extras(self):
        b = self.f.batch(); p = self.f.observe(batch=b)
        # Use real complete raw root snapshot to preserve exact captured binding.
        raw = b['processes'][0]['maps']; frozen = dict(self.f.frozen)
        for mapping in md.maps(raw.encode()):
            if mapping['path'].startswith('/') and not mapping['path'].endswith(' (deleted)'):
                path = Path(mapping['path']); frozen[str(path.resolve())] = {'sha256': md.digest(path.read_bytes()), 'mode': stat.S_IMODE(path.stat().st_mode)}
        value = mapping_authority(raw, frozen, self.f.runtime, [self.f.profile], owned_metrics=p, observed_identity=self.f.browser)
        self.assertEqual(len(value['ownedMutableMaps']), 1)
        with self.assertRaisesRegex(RuntimeError, 'Deleted'):
            mapping_authority(raw, frozen, self.f.runtime, [self.f.profile], owned_metrics=p, observed_identity=self.f.compositor)
    def test_missing_and_partial_proof_refused(self):
        b = self.f.batch(); p = self.f.observe(batch=b); line = p['observations'][0]['mapping']['line']
        for partial in (None, {'accepted': True}, {**p, 'accepted': False}):
            self.assertIsNone(md.classification(partial, b['processes'][0]['maps'], line, self.f.browser, self.f.runtime))
        md.revoke(p)
        with self.assertRaisesRegex(RuntimeError, 'partial or invalidated'): self.f.confirm(p, b)
        self.assertFalse(p['accepted']); self.assertFalse(p['usableForInput'])
    def test_actual_mutable_contents_timestamps_position_allowed(self):
        b = self.f.batch(); p = self.f.observe(batch=b); before = p['observations'][0]['before']['matchingFDs'][0]
        self.f.command('mutate'); self.f.confirm(p, b)
        after = p['afterDiskValidation']['observations'][0]['before']['matchingFDs'][0]
        self.assertNotEqual(before['stat']['st_mtime_ns'], after['stat']['st_mtime_ns'])
        self.assertNotEqual(before['rawFdinfo'], after['rawFdinfo']); self.assertTrue(p['usableForInput'])
    def test_duplicate_actual_fd_refused(self):
        self.f.command('dup'); p = {}
        with self.assertRaisesRegex(RuntimeError, 'Exactly one'): self.f.observe(p)
        self.assertEqual(len(p['observations'][0]['before']['matchingFDs']), 2); self.assertTrue(p['observations'][0]['after']); self.assertFalse(p['accepted'])
    def test_metadata_faults_retain_both_raw_samples(self):
        for mode in (0o400, 0o640, 0o4600, 0o2600, 0o1600):
            self.f.command('mode', mode); p = {}
            with self.assertRaisesRegex(RuntimeError, 'fullmode'): self.f.observe(p)
            row = p['observations'][0]
            for phase in ('before','after'):
                fd = row[phase]['matchingFDs'][0]; self.assertEqual(stat.S_IMODE(fd['stat']['st_mode']), mode)
                self.assertTrue(fd['rawFdinfo']); self.assertTrue(row[phase]['rawMountinfo']); self.assertTrue(fd['target'])
            self.assertFalse(p['accepted'])
    def test_wrong_actual_size_refused(self):
        self.f.command('size', md.SIZE-1)
        with self.assertRaisesRegex(RuntimeError, 'size'): self.f.observe()
    def test_actual_readonly_and_path_fd_refused(self):
        for cmd in ('readonly','path'):
            self.f.command(cmd); p = {}
            with self.assertRaisesRegex(RuntimeError, 'O_RDWR'): self.f.observe(p)
            self.assertFalse(p['accepted']); self.assertTrue(p['observations'][0]['after']['matchingFDs'])
    def test_actual_executable_alias_refused(self):
        self.f.command('exec'); p = {}
        with self.assertRaises(RuntimeError): self.f.observe(p)
        self.assertFalse(p['accepted'])
    def test_actual_fd_replacement_during_disk_validation_revokes(self):
        b = self.f.batch(); p = self.f.observe(batch=b); self.f.command('replace')
        with self.assertRaises(RuntimeError): self.f.confirm(p,b)
        self.assertFalse(p['accepted']); self.assertFalse(p['usableForInput']); self.assertFalse(p['observations'][0]['accepted'])
    def test_actual_full_flags_change_during_disk_validation_revokes(self):
        b = self.f.batch(); p = self.f.observe(batch=b); self.f.command('flags')
        with self.assertRaisesRegex(RuntimeError, 'during strict disk'): self.f.confirm(p,b)
        self.assertFalse(p['accepted'])
    def test_between_samples_flags_change_refused(self):
        calls=0
        def read(pid):
            nonlocal calls
            if pid==self.f.browser['pid']:
                calls+=1
                if calls==2:self.f.command('flags')
            return Path(f'/proc/{pid}/maps').read_bytes()
        p={}
        with self.assertRaisesRegex(RuntimeError,'between snapshots'):self.f.observe(p,read_maps=read)
        self.assertTrue(p['observations'][0]['before']);self.assertTrue(p['observations'][0]['after']);self.assertFalse(p['accepted'])
    def test_changed_parent_and_profile_directory_identity_refused(self):
        b=self.f.batch();p=self.f.observe(batch=b);old=self.f.parent.with_name('old-parent');self.f.parent.rename(old);self.f.parent.mkdir(mode=0o700)
        with self.assertRaises(RuntimeError):self.f.confirm(p,b)
        self.assertFalse(p['usableForInput'])
    def test_frozen_executable_and_root_lifetime_refused(self):
        old=self.f.browser['start'];self.f.browser['start']='0';p={}
        with self.assertRaises(RuntimeError):self.f.observe(p)
        self.f.browser['start']=old;next(iter(self.f.frozen.values()))['sha256']='0'*64
        with self.assertRaisesRegex(RuntimeError,'observation unavailable'):self.f.observe(p)
        self.assertFalse(p['accepted'])
    def test_stale_capture_and_mapping_token_refused(self):
        b=self.f.batch();b['processes'][0]['rawMapsSHA256']='0'*64
        with self.assertRaisesRegex(RuntimeError,'snapshot binding'):self.f.observe(batch=b)
    def test_fresh_unrelated_mapping_change_allowed(self):
        b=self.f.batch();p=self.f.observe(batch=b)
        def read(pid):return Path(f'/proc/{pid}/maps').read_bytes()+b'\n00100000-00101000 rw-p 00000000 00:00 0\n'
        self.f.confirm(p,b,read_maps=read);self.assertTrue(p['usableForInput'])
    def test_missing_or_changed_vma_in_fresh_root_refused(self):
        def read(pid):
            raw=Path(f'/proc/{pid}/maps').read_bytes()
            if pid==self.f.browser['pid']:raw=b'\n'.join(x for x in raw.splitlines() if b'BrowserMetrics-' not in x)
            return raw
        with self.assertRaisesRegex(RuntimeError,'VMA changed'):self.f.observe(read_maps=read)
    def test_fdinfo_read_error_retains_other_observations(self):
        real=md.bounded;p={}
        def read(path,limit=4*1024*1024):
            if '/fdinfo/' in str(path):raise PermissionError(13,'CPU denied fdinfo')
            return real(path,limit)
        with patch.object(md,'bounded',read):
            with self.assertRaisesRegex(RuntimeError,'metadata unavailable'):self.f.observe(p)
        for phase in ('before','after'):
            fd=p['observations'][0][phase]['matchingFDs'][0];self.assertTrue(fd['stat']);self.assertTrue(fd['target']);self.assertEqual(fd['errors']['rawFdinfo']['errno'],13)
    def test_fdinfo_duplicate_parse_refused(self):
        with self.assertRaisesRegex(RuntimeError,'Duplicate'):md.parse_fdinfo(b'flags: 02\nflags: 02\nmnt_id: 1\nino: 1\n')
    def test_ambiguous_mount_refused_with_raw_evidence(self):
        real=md.bounded;p={}
        def read(path,limit=4*1024*1024):
            raw=real(path,limit)
            if str(path).endswith('/mountinfo'):
                selected=md.parse_mount(raw,self.f.runtime);raw+=selected['line'].encode()+b'\n'
            return raw
        with patch.object(md,'bounded',read):
            with self.assertRaisesRegex(RuntimeError,'observation unavailable'):self.f.observe(p)
        self.assertTrue(p['observations'][0]['after']['rawMountinfo'])
    def test_complete_batch_unreadable_alias_refused(self):
        b=self.f.batch();b['processes'][1]['readError']={'errno':13}
        with self.assertRaisesRegex(RuntimeError,'alias observation unavailable'):self.f.observe(batch=b)
    def test_wrong_kernel_vma_permissions_and_ranges_refused(self):
        import mmap
        for length, flags, prot, offset in (
            (4096,mmap.MAP_SHARED,mmap.PROT_READ|mmap.PROT_WRITE,0),
            (md.SIZE,mmap.MAP_PRIVATE,mmap.PROT_READ|mmap.PROT_WRITE,0),
            (md.SIZE,mmap.MAP_SHARED,mmap.PROT_READ,0),
            (md.SIZE-4096,mmap.MAP_SHARED,mmap.PROT_READ|mmap.PROT_WRITE,4096)):
            self.f.command('vma',length,flags,prot,offset);p={}
            with self.assertRaisesRegex(RuntimeError,'VMA must be'):self.f.observe(p)
            self.assertTrue(p['observations'][0]['before']['matchingFDs']);self.assertTrue(p['observations'][0]['after']['matchingFDs'])
    def test_canonical_wrong_pid_filename_refused(self):
        b=self.f.batch();row=b['processes'][0];raw=base64.b64decode(row['rawMapsBase64']);raw=raw.replace(('-'+format(self.f.browser['pid'],'X')+'.pma').encode(),b'-0.pma')
        row.update(maps=raw.decode(),rawMapsBase64=base64.b64encode(raw).decode(),rawMapsSHA256=md.digest(raw),rawMapsBytes=len(raw));p={}
        with self.assertRaisesRegex(RuntimeError,'canonical PID filename'):self.f.observe(p,batch=b)
        self.assertTrue(p['observations'][0]['after']);self.assertFalse(p['accepted'])
    def test_fresh_compositor_executable_alias_refused(self):
        candidate=next(r for r in md.maps(Path(f'/proc/{self.f.browser["pid"]}/maps').read_bytes()) if 'BrowserMetrics-' in r['path'])
        def read(pid):
            raw=Path(f'/proc/{pid}/maps').read_bytes()
            if pid==self.f.compositor['pid']:raw+=b'\n'+candidate['line'].replace('rw-s','r-xs').encode()+b'\n'
            return raw
        with self.assertRaisesRegex(RuntimeError,'Executable alias'):self.f.observe(read_maps=read)
    def test_other_owned_batch_executable_alias_refused(self):
        b=self.f.batch();candidate=next(r for r in md.maps(b['processes'][0]['maps'].encode()) if 'BrowserMetrics-' in r['path']);raw=b['processes'][1]['maps'].encode()+b'\n'+candidate['line'].replace('rw-s','r-xs').encode()+b'\n';row=b['processes'][1]
        row.update(maps=raw.decode(),rawMapsBase64=base64.b64encode(raw).decode(),rawMapsSHA256=md.digest(raw),rawMapsBytes=len(raw))
        with self.assertRaisesRegex(RuntimeError,'Executable alias'):self.f.observe(batch=b)
    def test_symlink_parent_refused_and_raw_errors_retained(self):
        b=self.f.batch();old=self.f.parent.with_name('symlink-target');self.f.parent.rename(old);self.f.parent.symlink_to(old,target_is_directory=True);p={}
        with self.assertRaisesRegex(RuntimeError,'observation unavailable'):self.f.observe(p,batch=b)
        self.assertIn('directory:parent',p['observations'][0]['before']['errors']);self.assertTrue(p['observations'][0]['after']['rootMaps'])
        self.f.parent.unlink();old.rename(self.f.parent)
    def test_previous_parent_anchor_replacement_refused(self):
        b=self.f.batch();p=self.f.observe(batch=b);self.f.confirm(p,b);self.assertIn('parent',self.f.anchors)
        self.f.anchors['parent']={**self.f.anchors['parent'],'inode':self.f.anchors['parent']['inode']+1}
        with self.assertRaisesRegex(RuntimeError,'parent anchor changed'):self.f.observe()
    def test_absence_snapshot_cannot_hide_new_mapping(self):
        b=self.f.batch();row=b['processes'][0];raw=b'\n'.join(line for line in row['maps'].encode().splitlines() if b'BrowserMetrics-' not in line)
        row.update(maps=raw.decode(),rawMapsBase64=base64.b64encode(raw).decode(),rawMapsSHA256=md.digest(raw),rawMapsBytes=len(raw));p={}
        with self.assertRaisesRegex(RuntimeError,'New metrics mapping'):self.f.observe(p,batch=b)
        self.assertFalse(p['accepted']);self.assertEqual(len(p['absenceSamples']),2)
    def test_classifier_executable_line_and_unrelated_deleted_code_refused(self):
        b=self.f.batch();p=self.f.observe(batch=b);raw=b['processes'][0]['maps'];line=p['observations'][0]['mapping']['line']
        self.assertIsNone(md.classification(p,raw,line.replace('rw-s','rwxp'),self.f.browser,self.f.runtime))
        other=line.replace(line.split(maxsplit=5)[5],'/usr/lib/changed-code.so (deleted)')
        with self.assertRaisesRegex(RuntimeError,'Deleted'):mapping_authority(other,{},self.f.runtime,[self.f.profile],owned_metrics=p,observed_identity=self.f.browser)
    def test_validated_extra_is_exact_row_identity(self):
        b=self.f.batch();seen=[]
        validate(b,lambda i:True,lambda raw,observed_identity:seen.append(observed_identity) or {},extras=lambda r:{'observed_identity':r['identity']})
        self.assertEqual(seen,[self.f.browser,self.f.compositor])

if __name__=='__main__':unittest.main()
