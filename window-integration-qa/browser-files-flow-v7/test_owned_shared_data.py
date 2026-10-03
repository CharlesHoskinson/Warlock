import array,base64,hashlib,json,mmap,os,socket,stat,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import owned_shared_data as sd
from runtime_inputs import mapping_authority

CHILD=r'''
import os,socket,array,sys,uuid
p='/dev/shm/'+str(uuid.uuid4());rw=os.open(p,os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600);os.ftruncate(rw,4096);ro=os.open(p,os.O_RDONLY);os.close(rw);os.unlink(p)
s=socket.socket(socket.AF_UNIX);s.bind(sys.argv[1]);s.listen();print('ready',flush=True)
while True:
 c,_=s.accept();v=c.recv(1)
 if v==b'f':c.sendmsg([b'f'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[ro]))])
 elif v==b'd':dup=os.dup(ro);c.send(b'ok')
 elif v==b'm':os.fchmod(ro,0o4600);c.send(b'ok')
 elif v==b'r':os.close(ro);ro=os.open('/dev/null',os.O_RDONLY);c.send(b'ok')
 elif v==b'q':c.send(b'ok');c.close();break
 c.close()
os.close(ro);s.close()
'''
class KernelFixture:
 def __init__(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'peer';self.child=subprocess.Popen([sys.executable,'-IS','-c',CHILD,str(self.path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  assert self.child.stdout.readline().strip()=='ready'
  with self.connection() as c:
   c.send(b'f');_,anc,_,_=c.recvmsg(1,socket.CMSG_SPACE(4));self.fd=array.array('i',anc[0][2])[0]
  self.mapping=mmap.mmap(self.fd,4096,flags=mmap.MAP_PRIVATE,prot=mmap.PROT_READ);os.close(self.fd)
  self.producer=self.ident(self.child.pid);self.consumer=self.ident(os.getpid());exe=str(Path('/proc/self/exe').resolve());st=Path(exe).stat();self.frozen={exe:{'sha256':sd.digest(Path(exe).read_bytes()),'mode':stat.S_IMODE(st.st_mode)}}
 def connection(self):
  c=socket.socket(socket.AF_UNIX);c.settimeout(2);c.connect(str(self.path));return c
 def command(self,value):
  with self.connection() as c:c.send(value);return c.recv(2)
 def peer(self):
  before=self.path.stat()
  with self.connection() as c:pid,uid,gid=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  after=self.path.stat();assert (before.st_dev,before.st_ino)==(after.st_dev,after.st_ino)
  return {'path':str(self.path),'device':before.st_dev,'inode':before.st_ino,'pid':pid,'uid':uid,'gid':gid}
 def ident(self,pid):return {'pid':pid,'start':Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]}
 def batch(self):return {'processes':[{'identity':i,'maps':Path(f'/proc/{i["pid"]}/maps').read_text()} for i in (self.consumer,self.producer)]}
 def observe(self,proof=None,**kw):
  proof={} if proof is None else proof;sd.observe(proof,self.batch(),self.consumer,self.producer,self.frozen,lambda:None,self.peer,**kw);return proof
 def close(self):
  self.mapping.close();self.command(b'q');self.child.wait(timeout=3);assert self.child.returncode==0;assert not self.child.stderr.read();self.child.stdout.close();self.child.stderr.close();self.tmp.cleanup()

class OwnedSharedDataTest(unittest.TestCase):
 def setUp(self):self.fixture=KernelFixture()
 def tearDown(self):self.fixture.close()
 def test_actual_two_process_kernel_fd_peer_metadata(self):
  p=self.fixture.observe();self.assertTrue(p['accepted']);self.assertEqual(len(p['mappings']),1);r=next(iter(p['mappings'].values()));self.assertEqual(r['producerFDBefore'],r['producerFDAfter']);self.assertEqual(r['matchingProducerFDs'],r['matchingProducerFDsAfter']);self.assertEqual(r['producerFDBefore']['fdinfo']['flags']&os.O_ACCMODE,os.O_RDONLY)
 def test_exact_shared_data_runtime_classification(self):
  p=self.fixture.observe();raw=self.fixture.batch()['processes'][0]['maps'];line=next(iter(p['mappings']));selected={**p,'consumerRawMapsSHA256':sd.digest(line.encode())}
  authority=mapping_authority(line,{},Path(self.fixture.tmp.name)/'runtime',[],shared_data=selected);self.assertEqual(len(authority['ownedMutableMaps']),1);self.assertFalse(authority['frozenFiles'])
 def test_no_proof_deleted_refused(self):
  p=self.fixture.observe();line=next(iter(p['mappings']))
  with self.assertRaisesRegex(RuntimeError,'Deleted'):mapping_authority(line,{},Path(self.fixture.tmp.name)/'runtime',[])
 def test_raw_hash_change_refused(self):
  p=self.fixture.observe();line=next(iter(p['mappings']))
  with self.assertRaisesRegex(RuntimeError,'Deleted'):mapping_authority(line,{},Path(self.fixture.tmp.name)/'runtime',[],shared_data=p)
 def test_forged_executable_line_refused_even_with_proof(self):
  p=self.fixture.observe();line=next(iter(p['mappings'])).replace('r--p','r-xp');p.update(consumerRawMapsSHA256=sd.digest(line.encode()),mappings={line:{'accepted':True,'mapping':{'line':line}}})
  with self.assertRaisesRegex(RuntimeError,'Deleted'):mapping_authority(line,{},Path(self.fixture.tmp.name)/'runtime',[],shared_data=p)
 def test_unrelated_deleted_code_name_refused(self):
  p=self.fixture.observe();line=next(iter(p['mappings']));line=line.replace(line.split(maxsplit=5)[5],'/usr/lib/code.so (deleted)');p.update(consumerRawMapsSHA256=sd.digest(line.encode()),mappings={line:{'accepted':True,'mapping':{'line':line}}})
  with self.assertRaisesRegex(RuntimeError,'Deleted'):mapping_authority(line,{},Path(self.fixture.tmp.name)/'runtime',[],shared_data=p)
 def test_duplicate_producer_fd_refused(self):
  self.fixture.command(b'd')
  with self.assertRaisesRegex(RuntimeError,'Exactly one'):self.fixture.observe()
 def test_special_mode_bits_refused(self):
  self.fixture.command(b'm')
  with self.assertRaisesRegex(RuntimeError,'full mode'):self.fixture.observe()
 def test_fd_replacement_between_snapshots_refused(self):
  calls=0;proof={}
  def read(pid):
   nonlocal calls;calls+=1
   if calls==3:self.fixture.command(b'r')
   return Path(f'/proc/{pid}/maps').read_bytes()
  with self.assertRaises(RuntimeError):self.fixture.observe(proof,read_maps=read)
  self.assertFalse(proof['accepted']);self.assertTrue(proof['observations'])
 def test_consumer_vma_change_between_snapshots_refused(self):
  calls=0
  def read(pid):
   nonlocal calls;calls+=1;raw=Path(f'/proc/{pid}/maps').read_bytes()
   if calls==3:raw=b'\n'.join(x for x in raw.splitlines() if b'/dev/shm/' not in x)
   return raw
  with self.assertRaisesRegex(RuntimeError,'VMA changed after'):self.fixture.observe(read_maps=read)
 def test_executable_producer_alias_refused(self):
  def read(pid):
   raw=Path(f'/proc/{pid}/maps').read_bytes()
   if pid==self.fixture.producer['pid']:
    line=next(r for r in sd.maps(Path('/proc/self/maps').read_bytes()) if sd.NAME.fullmatch(r['path']))['line'];raw+=b'\n'+line.replace('r--p','r-xp').encode()+b'\n'
   return raw
  with self.assertRaisesRegex(RuntimeError,'Executable alias'):self.fixture.observe(read_maps=read)
 def test_writable_consumer_vma_refused(self):
  real=self.fixture.batch
  def batch():
   value=real();line=next(r for r in sd.maps(value['processes'][0]['maps'].encode()) if sd.NAME.fullmatch(r['path']))['line'];value['processes'][0]['maps']=value['processes'][0]['maps'].replace(line,line.replace('r--p','rw-p'));return value
  self.fixture.batch=batch
  with self.assertRaises(RuntimeError):self.fixture.observe()
 def test_stale_producer_identity_refused(self):
  self.fixture.producer['start']='0'
  with self.assertRaisesRegex(RuntimeError,'lifetime'):self.fixture.observe()
 def test_wrong_kernel_peer_refused(self):
  self.fixture.peer=lambda:{'pid':1,'uid':os.getuid()}
  with self.assertRaisesRegex(RuntimeError,'kernel peer'):self.fixture.observe()
 def test_fdinfo_write_access_refused(self):
  with self.assertRaisesRegex(RuntimeError,'not read-only'):sd.fdinfo(b'flags:\t02\nmnt_id:\t1\nino:\t1\n')
 def test_duplicate_fdinfo_refused(self):
  with self.assertRaisesRegex(RuntimeError,'Duplicate'):sd.fdinfo(b'flags: 00\nflags: 00\nmnt_id: 1\nino: 1\n')
 def test_offset_beyond_file_size_refused(self):
  p=self.fixture.observe();r=next(iter(p['mappings'].values()));mapping={**r['mapping'],'offset':4096}
  with self.assertRaisesRegex(RuntimeError,'offset/range'):sd.metadata(self.fixture.producer['pid'],r['producerFDBefore']['fd'],mapping,p['mountBefore'])
 def test_ambiguous_tmpfs_mount_refused(self):
  original=sd.bounded
  def read(path,limit=sd.MAX_MAP_BYTES):
   raw=original(path,limit)
   if str(path).endswith('/mountinfo'):
    line=next(x for x in raw.splitlines() if b' /dev/shm ' in x);raw+=b'\n'+line+b'\n'
   return raw
  with patch.object(sd,'bounded',read):
   with self.assertRaisesRegex(RuntimeError,'ambiguous'):self.fixture.observe()
 def test_missing_producer_descriptor_refused(self):
  self.fixture.command(b'r')
  with self.assertRaisesRegex(RuntimeError,'Exactly one'):self.fixture.observe()
 def test_producer_peer_replacement_after_capture_refused(self):
  original=self.fixture.peer;calls=0
  def peer():
   nonlocal calls;calls+=1;value=original()
   if calls==2:value['inode']+=1
   return value
  self.fixture.peer=peer
  with self.assertRaisesRegex(RuntimeError,'peer/mount changed'):self.fixture.observe()
 def test_final_guard_failure_never_accepts(self):
  proof={};calls=0
  def guard():
   nonlocal calls;calls+=1
   if calls==3:raise RuntimeError('final peer changed')
  with self.assertRaisesRegex(RuntimeError,'final peer'):sd.observe(proof,self.fixture.batch(),self.fixture.consumer,self.fixture.producer,self.fixture.frozen,guard,self.fixture.peer)
  self.assertFalse(proof['accepted'])
 def test_full_vma_bounds_exceed_size_refused(self):
  p=self.fixture.observe();r=next(iter(p['mappings'].values()));mapping={**r['mapping'],'end':r['mapping']['end']+4096}
  with self.assertRaisesRegex(RuntimeError,'offset/range'):sd.metadata(self.fixture.producer['pid'],r['producerFDBefore']['fd'],mapping,p['mountBefore'])
 def test_fresh_confirmation_after_disk_validation(self):
  batch=self.fixture.batch();p={};sd.observe(p,batch,self.fixture.consumer,self.fixture.producer,self.fixture.frozen,lambda:None,self.fixture.peer);sd.confirm(p,batch,self.fixture.consumer,self.fixture.producer,self.fixture.frozen,lambda:None,self.fixture.peer);self.assertTrue(p['accepted'] and p['confirmedAfterDiskValidation'])
 def test_replaced_fd_during_disk_validation_invalidates(self):
  batch=self.fixture.batch();p={};sd.observe(p,batch,self.fixture.consumer,self.fixture.producer,self.fixture.frozen,lambda:None,self.fixture.peer);self.fixture.command(b'r')
  with self.assertRaises(RuntimeError):sd.confirm(p,batch,self.fixture.consumer,self.fixture.producer,self.fixture.frozen,lambda:None,self.fixture.peer)
  self.assertFalse(p['accepted'])

if __name__=='__main__':unittest.main()
