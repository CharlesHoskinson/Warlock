#!/usr/bin/env python3
"""Offline real PNG composition/cache tests; no compositor or user windows."""
import os,copy,importlib.machinery,importlib.util,json,subprocess,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
HELPERS=Path(os.getenv('MOTION_HELPER_DIR',str(HERE)))
loader=importlib.machinery.SourceFileLoader('whole',str(HELPERS/'hypr-window-motion'))
spec=importlib.util.spec_from_loader(loader.name,loader);whole=importlib.util.module_from_spec(spec);loader.exec_module(whole)

class Snapshot(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.root_patch=patch.object(whole,'ROOT',self.root);self.root_patch.start()
  self.runtime_patch=patch.object(whole,'RUNTIME',self.root/'runtime');self.runtime_patch.start()
  self.window={'address':'0x10','stableId':'abc','pid':100,'at':[100,200],'size':[2,2],'workspace':{'name':'2'}}
  self.native_calls=0
  self.metadata={'ok':True,'whole':True,'stableId':'abc','pid':100,'rect':{'x':99,'y':197,'width':4,'height':6},'insets':{'left':1,'top':3,'right':1,'bottom':1},'pixels':[4,6]}
  self.original_output=subprocess.check_output
  def snapshot(argv,**kwargs):
   if argv[0]!='hyprctl':return self.original_output(argv,**kwargs)
   self.native_calls+=1
   import re
   path=Path(json.loads(re.search(r',("[^"]+\.png")\)\)',argv[2]).group(1)))
   subprocess.run(['magick','-size','4x6','xc:gold','-fill','red','-draw','rectangle 1,3 2,4',str(path)],check=True)
   return json.dumps(self.metadata)
  self.snapshot_patch=patch.object(whole.subprocess,'check_output',side_effect=snapshot);self.snapshot_patch.start()
  def client(adapter,window,token):
   path=self.root/(token+'.png')
   subprocess.run(['magick','-size','2x2','xc:lime',str(path)],check=True);return str(path)
  self.client_patch=patch.object(whole.BasicDesktop,'capture',client);self.client_patch.start()
  self.desktop=whole.Desktop()
  self.clients_patch=patch.object(self.desktop,'clients',side_effect=lambda:[copy.deepcopy(self.window)]);self.clients_patch.start()
 def tearDown(self):
  self.clients_patch.stop();self.client_patch.stop();self.snapshot_patch.stop();self.root_patch.stop();self.runtime_patch.stop();self.temp.cleanup()
 def pixels(self,path):return self.original_output(['magick',path,'-depth','8','rgba:-'])
 def test_server_caption_retained_with_latest_client(self):
  result=self.desktop.capture(self.window,'first')
  self.assertEqual(result['rect'],{'x':99,'y':197,'width':4,'height':6});self.assertTrue(result['whole'])
  rgba=self.pixels(result['image'])
  self.assertEqual(list(rgba[:4]),[255,215,0,255])
  client_offset=(3*4+1)*4;self.assertEqual(list(rgba[client_offset:client_offset+4]),[255,0,0,255])
  self.assertEqual(self.pixels(str(self.root/'runtime/hypr-window-previews/0x10-0.png'))[:4],bytes([255,0,0,255]))
  self.assertEqual(self.window['at']+self.window['size'],[100,200,2,2])
 def test_minimized_restore_uses_identity_cache_and_current_rect(self):
  self.desktop.capture(self.window,'first')
  restored=copy.deepcopy(self.window);restored['workspace']['name']='special:win-minimized';restored['at']=[300,400]
  self.window=restored;result=self.desktop.capture(restored,'second')
  self.assertEqual(self.native_calls,1);self.assertEqual(result['rect']['x'],299);self.assertEqual(result['rect']['y'],397)
  rgba=self.pixels(result['image']);self.assertEqual(list(rgba[:4]),[255,215,0,255]);self.assertEqual(list(rgba[(3*4+1)*4:(3*4+1)*4+4]),[0,255,0,255])
 def test_reused_pid_cannot_read_old_frame(self):
  self.desktop.capture(self.window,'first');stale=copy.deepcopy(self.window);stale['workspace']['name']='special:win-minimized';stale['pid']=101
  with self.assertRaises(OSError):self.desktop.capture(stale,'reuse')
  self.assertFalse((self.root/'reuse.png').exists())
 def test_changed_native_client_size_rejects_cache(self):
  self.desktop.capture(self.window,'first');stale=copy.deepcopy(self.window);stale['workspace']['name']='special:win-minimized';stale['size']=[3,2]
  with self.assertRaisesRegex(ValueError,'matching'):self.desktop.capture(stale,'resize')
 def test_invalid_native_metadata_rejected_before_cache(self):
  for field,value in [('insets',{'left':float('nan')}),('pixels',[0,6])]:
   with self.subTest(field=field):
    metadata=copy.deepcopy(self.metadata);metadata[field]=value
    with patch.object(self,'metadata',metadata),self.assertRaises(ValueError):self.desktop.capture(self.window,'invalid-'+field)
    self.assertFalse((self.root/'full-abc-100.json').exists())
 def test_native_missing_server_frame_never_uses_client_only_route(self):
  with patch.object(self,'metadata',{'ok':False,'reason':'unsupported'}),self.assertRaises(ValueError):self.desktop.capture(self.window,'missing')
  self.assertFalse((self.root/'missing.png').exists())

 def test_visible_minimize_does_not_capture_client_again(self):
  with patch.object(whole.BasicDesktop,'capture',side_effect=AssertionError('second grim capture')):
   self.assertTrue(self.desktop.capture(self.window,'visible')['whole'])
 def test_native_metadata_geometry_drift_is_rejected(self):
  metadata=copy.deepcopy(self.metadata);metadata['rect']['x']+=1
  with patch.object(self,'metadata',metadata),self.assertRaisesRegex(ValueError,'drifted'):
   self.desktop.capture(self.window,'drift')
  self.assertFalse((self.root/'full-abc-100.json').exists());self.assertFalse((self.root/'frame-drift.png').exists())
 def test_live_geometry_drift_is_rejected(self):
  current=copy.deepcopy(self.window);current['size'][0]+=1
  with patch.object(self.desktop,'clients',return_value=[current]),self.assertRaisesRegex(ValueError,'geometry changed'):
   self.desktop.capture(self.window,'live-drift')
  self.assertFalse((self.root/'full-abc-100.json').exists())
 def test_concurrent_captures_produce_consistent_cache_pair(self):
  with ThreadPoolExecutor(max_workers=2) as pool:
   results=list(pool.map(lambda token:self.desktop.capture(copy.deepcopy(self.window),token),['concurrent-a','concurrent-b']))
  self.assertTrue(all(Path(result['image']).is_file() for result in results))
  self.assertEqual(self.pixels(results[0]['image']),self.pixels(results[1]['image']))
  metadata=json.loads((self.root/'full-abc-100.json').read_text());self.assertEqual(metadata['identity'],['0x10','abc',100])
  self.assertFalse(list(self.root.glob('*.tmp')))
 def test_janitor_retains_minimized_live_cache_and_removes_closed_reused(self):
  self.desktop.capture(self.window,'cached');self.window['workspace']['name']='special:win-minimized'
  self.desktop.janitor();self.assertTrue((self.root/'full-abc-100.png').exists())
  self.window['pid']=101;self.desktop.janitor()
  self.assertFalse((self.root/'full-abc-100.png').exists());self.assertFalse((self.root/'full-abc-100.json').exists())
 def test_janitor_only_removes_owned_abandoned_files(self):
  owned=['frame-abcdefabcdef-1.png','composed-abcdefabcdef-2.png','full-abc-100-abcdefabcdef-3.png.tmp','full-abc-100-abcdefabcdef-3.json.tmp']
  unrelated=['unrelated.png','pending.json','abcdefabcdef-1.png','frame-user.png']
  for name in owned+unrelated:(self.root/name).write_bytes(b'test')
  self.desktop.janitor()
  self.assertTrue(all(not (self.root/name).exists() for name in owned));self.assertTrue(all((self.root/name).exists() for name in unrelated))
 def test_watchdog_janitor_runs_without_pending_and_is_bounded(self):
  controller=whole.Controller(self.desktop,self.root)
  with patch.object(self.desktop,'janitor') as janitor,patch.object(whole.time,'monotonic',return_value=10):
   controller.watchdog();controller.watchdog();self.assertEqual(janitor.call_count,1)
   with patch.object(whole.time,'monotonic',return_value=11):controller.watchdog()
   self.assertEqual(janitor.call_count,2)

if __name__=='__main__':unittest.main()
