import hashlib,os,stat,tempfile,unittest
from pathlib import Path
from runtime_inputs import mapping_authority,exact_files_instance
class RuntimeInputs(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.runtime=self.base/'runtime';self.cache=self.runtime/'cache';self.cache.mkdir(parents=True)
  self.disk=self.base/'frozen.so';self.disk.write_bytes(b'fixture');self.disk.chmod(0o600)
  self.expected={str(self.disk):{'sha256':hashlib.sha256(b'fixture').hexdigest(),'mode':0o600}}
 def tearDown(self):self.tmp.cleanup()
 def raw(self,p,permissions='r-xp',suffix='',inode=None):return f'1-2 {permissions} 0000 00:00 {p.stat().st_ino if inode is None else inode} {p}{suffix}\n'
 def call(self,p,**kw):return mapping_authority(self.raw(p,**kw),self.expected,self.runtime,[self.cache])
 def test_exact_frozen_disk(self):self.assertEqual(len(self.call(self.disk)['frozenFiles']),1)
 def test_changed_bytes(self):
  self.disk.write_bytes(b'changed')
  with self.assertRaisesRegex(RuntimeError,'bytes/mode'):self.call(self.disk)
 def test_changed_mode(self):
  self.disk.chmod(0o700)
  with self.assertRaisesRegex(RuntimeError,'bytes/mode'):self.call(self.disk)
 def test_unfrozen_disk(self):
  p=self.base/'unknown.so';p.write_bytes(b'unknown')
  with self.assertRaisesRegex(RuntimeError,'absent'):self.call(p)
 def test_cache_nonexec(self):
  p=self.cache/'data';p.write_bytes(b'cache');self.assertEqual(len(self.call(p,permissions='rw-p')['ownedMutableMaps']),1)
 def test_cache_exec(self):
  p=self.cache/'injected.so';p.write_bytes(b'ELF')
  with self.assertRaisesRegex(RuntimeError,'Unapproved'):self.call(p)
 def test_runtime_other_data(self):
  p=self.runtime/'unknown';p.write_bytes(b'cache')
  with self.assertRaisesRegex(RuntimeError,'Unapproved'):self.call(p,permissions='r--p')
 def test_symlink_escape(self):
  p=self.cache/'escape';p.symlink_to(self.base/'other');(self.base/'other').write_bytes(b'other')
  with self.assertRaisesRegex(RuntimeError,'absent'):self.call(p,permissions='r--p')
 def test_deleted_disk(self):
  with self.assertRaisesRegex(RuntimeError,'Deleted'):self.call(self.disk,suffix=' (deleted)')
 def test_inode_changed(self):
  with self.assertRaisesRegex(RuntimeError,'inode'):self.call(self.disk,inode=self.disk.stat().st_ino+1)
 def test_anonymous_memfd_not_disk(self):
  result=mapping_authority('1-2 rwxp 0000 00:01 123 /memfd:jit (deleted)',{},self.runtime,[self.cache]);self.assertEqual(len(result['anonymousMaps']),1)
 def test_cache_allowance_escaped_runtime(self):
  with self.assertRaisesRegex(RuntimeError,'outside'):mapping_authority('',{},self.runtime,[self.base])
 def test_exact_instance(self):
  rows=[{'id':'exact','pid':123,'config_path':str(self.base/'shell.qml')}];self.assertEqual(exact_files_instance(rows,123,self.base)['id'],'exact')
 def test_same_path_different_pid_refused(self):
  with self.assertRaisesRegex(RuntimeError,'exact'):exact_files_instance([{'id':'other','pid':124,'config_path':str(self.base/'shell.qml')}],123,self.base)
 def test_same_pid_other_config_refused(self):
  with self.assertRaisesRegex(RuntimeError,'exact'):exact_files_instance([{'id':'other','pid':123,'config_path':str(self.base/'other.qml')}],123,self.base)
 def test_duplicate_refused(self):
  row={'id':'exact','pid':123,'config_path':str(self.base/'shell.qml')}
  with self.assertRaisesRegex(RuntimeError,'exact'):exact_files_instance([row,row],123,self.base)
if __name__=='__main__':unittest.main(verbosity=2)
