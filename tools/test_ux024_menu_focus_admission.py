#!/usr/bin/env python3
"""Root-only mocked fixed admission controls. No compiler or runtime effect."""
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
MODULE,REPO=map(Path,sys.argv[1:3]);sys.argv=[sys.argv[0],*sys.argv[3:]]
sys.path.insert(0,str(REPO/'window-integration-qa'))
spec=importlib.util.spec_from_file_location('fixed_admission_under_test',MODULE);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
class Admission(unittest.TestCase):
 def packet(self,root):
  hs=root/'implementation/warlock/haskell';hs.mkdir(parents=True);(hs/'one.hs').write_text('module One where')
  tree={'one.hs':'a'*64};sources={n:'a'*64 for n in q.MENU_FOCUS_BUILD_SUPPORT};sources.update({'implementation/warlock/haskell/'+n:h for n,h in tree.items()})
  return {'schema':1,'kind':'ux024-fixed-menu-focus-build','recordPath':q.MENU_FOCUS_BUILD_RECORD,'recordIdentitySha256':q.MENU_FOCUS_BUILD_IDENTITY,'selectionGeneration':99,'authorizationExpiresUTC':'2026-11-10T14:40:00Z','coreSha256':'a'*64,'targets':list(q.MENU_FOCUS_BUILD_TARGETS),'behaviorSuites':['ui-webkit-controls'],'sourceHashes':sources,'haskellFiles':tree,'toolchainManifest':{'path':str(root/'tools/arm64-toolchain.json'),'sha256':'a'*64},'cacheCorrespondence':{'path':str(root/'.warlock-contributor/evidence/cache-proof.json'),'sha256':'b'*64}}
 def write(self,root,value):
  p=root/q.MENU_FOCUS_BUILD_PACKET;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value));return p
 def test_exact_hash_argument_and_literal_runner_only(self):
  with patch.object(q,'REPO',REPO):
   runner=REPO/'tools/run_ux024_menu_focus_build.py';self.assertTrue(q.menu_focus_build_mode(runner,['--sha256','a'*64],'a'*64))
   for args in [[],['--sha256','b'*64],['--sha256','a'*64,'--inside-private','/tmp/x'],['--packet','/tmp/x']]:self.assertFalse(q.menu_focus_build_mode(runner,args,'a'*64))
   self.assertFalse(q.menu_focus_build_mode(REPO/'tools/other.py',['--sha256','a'*64],'a'*64))
 def test_complete_fixed_closure_and_metadata(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);packet=self.packet(root);p=self.write(root,packet);value=q.menu_focus_build_spec(root)
   self.assertEqual(value['packetSha256'],q.digest(p));self.assertEqual(value['inputs'],set(packet['sourceHashes'])|{q.MENU_FOCUS_BUILD_PACKET,'tools/arm64-toolchain.json','.warlock-contributor/evidence/cache-proof.json'})
 def test_scope_targets_unknown_fields_and_actor_record_refuse(self):
  for mutation in ['target','suite','record','identity','selection','extra']:
   with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);p=self.packet(root)
    if mutation=='target':p['targets'].append('warlock-runtime:exe:ux003-native-observer')
    if mutation=='suite':p['behaviorSuites']=['warlock-ui-owner']
    if mutation=='record':p['recordPath']='.warlock-contributor/other.json'
    if mutation=='identity':p['recordIdentitySha256']='b'*64
    if mutation=='selection':p['selectionGeneration']=True
    if mutation=='extra':p['arbitraryCommand']=['sh']
    self.write(root,p)
    with self.assertRaises(RuntimeError):q.menu_focus_build_spec(root)
 def test_incomplete_extra_haskell_or_support_hashes_refuse(self):
  for mutation in ['missing','extra','badsha','mismatch']:
   with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);p=self.packet(root)
    if mutation=='missing':p['sourceHashes'].pop('tools/qa_cpu.py')
    if mutation=='extra':p['haskellFiles']['invented.hs']='a'*64
    if mutation=='badsha':p['sourceHashes']['tools/qa_cpu.py']=None
    if mutation=='mismatch':p['sourceHashes']['implementation/warlock/haskell/one.hs']='b'*64
    self.write(root,p)
    with self.assertRaises(RuntimeError):q.menu_focus_build_spec(root)
 def test_reference_escape_symlink_and_oversize_refuse(self):
  for mutation in ['outside','symlink','oversize']:
   with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);p=self.packet(root);path=self.write(root,p)
    if mutation=='outside':p['cacheCorrespondence']['path']='/etc/passwd';self.write(root,p)
    if mutation=='symlink':path.unlink();path.symlink_to(root/'missing')
    if mutation=='oversize':path.write_bytes(b' '*(4*1024*1024+1))
    with self.assertRaises((RuntimeError,OSError)):q.menu_focus_build_spec(root)
 def test_old_elm_mode_unchanged(self):
  with patch.object(q,'REPO',REPO):
   self.assertTrue(q.menu_tab_dom_mode(REPO/'tools/check_elm_cpu.py',['--menu-tab-dom','--arm64']))
   self.assertFalse(q.menu_tab_dom_mode(REPO/'tools/run_ux024_menu_focus_build.py',['--menu-tab-dom','--arm64']))
if __name__=='__main__':unittest.main()
