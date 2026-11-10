"""Fixed source/installed-ABI controls; no GTK, compositor or target-module imports."""
import argparse,hashlib,re,unittest,xml.etree.ElementTree as ET
from pathlib import Path

TYPE='type ContextMenuCallback = Ptr MvpObject -> Ptr MvpObject -> Ptr MvpObject -> Ptr () -> IO CInt\n'
WRAPPER='foreign import ccall "wrapper"\n  wrapContextMenu :: ContextMenuCallback -> IO (FunPtr ContextMenuCallback)\n\n'
HANDLER='''      -- WebKit's stock browser menu is not shell policy. The borrowed menu and
      -- hit-test objects are valid only during emission; neither is retained.
      -- TRUE suppresses the stock popover, including on a context fault.
      mapM_ (\\visibleView -> acquireSignal visibleView "context-menu"
        (wrapContextMenu $ \\_ _ _ _ -> callback 1 (pure 1))) [bView, pView]

'''
NS={'g':'http://www.gtk.org/introspection/core/1.0','glib':'http://www.gtk.org/introspection/glib/1.0','c':'http://www.gtk.org/introspection/c/1.0'}

def signal(gir):
 tree=ET.parse(gir);matches=tree.findall(".//g:class[@name='WebView']/glib:signal[@name='context-menu']",NS)
 if len(matches)!=1:raise ValueError('exact WebKit6 context-menu signal required')
 return matches[0]

def callback_contract(source):
 return source.count(TYPE)==1 and source.count(WRAPPER)==1 and source.count(HANDLER)==1

class Controls(unittest.TestCase):
 def test_installed_gtk4_signal_has_two_borrowed_parameters(self):
  s=signal(args.gir);params=s.findall('g:parameters/g:parameter',NS)
  self.assertEqual([p.attrib['name']for p in params],['context_menu','hit_test_result'])
  self.assertEqual([p.attrib['transfer-ownership']for p in params],['none','none'])
  self.assertEqual(s.find('g:return-value/g:type',NS).attrib['name'],'gboolean')
  self.assertEqual(s.attrib['when'],'last')
 def test_header_virtual_method_confirms_no_gtk3_event_argument(self):
  header=Path(args.header).read_text();match=re.search(r'gboolean\s+\(\*\s*context_menu\)\s*\((.*?)\);',header,re.S)
  self.assertIsNotNone(match)
  self.assertEqual(re.findall(r'(\w+)\s*\*',match.group(1)),['WebKitWebView','WebKitContextMenu','WebKitHitTestResult'])
  self.assertNotIn('GdkEvent',match.group(1))
 def test_return_true_suppresses_borrowed_default_menu_by_installed_contract(self):
  doc=signal(args.gir).find('g:doc',NS).text
  self.assertIn('return %TRUE so that the proposed menu will not be shown',doc)
  self.assertIn('only valid\nduring the signal emission',doc)
  self.assertTrue(callback_contract(Path(args.module).read_text()))
 def test_visible_roles_registered_before_present_via_owned_masked_path(self):
  source=Path(args.module).read_text();start=source.index('attachMvpWindow contextOwner views = mask');end=source.index('      gtkWindowPresent window',start)
  self.assertIn(HANDLER,source[start:end]);self.assertNotIn('[cView',HANDLER)
  self.assertIn('disconnect <- connectOwnedMvpSignal contextOwner obj sigName mkCb',source)
  self.assertIn("modifyIORef' sigReleases ((checkContext >> disconnect) :)",source)
 def test_all_prior_source_bytes_and_retirement_are_preserved(self):
  source=Path(args.module).read_text();old=Path(args.baseline).read_text()
  self.assertTrue(callback_contract(source))
  self.assertEqual(source.replace(TYPE,'',1).replace(WRAPPER,'',1).replace(HANDLER,'',1),old)
  self.assertIn('MVP signal callback retained until owner process exit:',source)
  self.assertNotIn('freeHaskellFunPtr',source)
 def test_fault_fallback_suppresses_without_new_effect_or_borrow_escape(self):
  source=Path(args.module).read_text();self.assertIn('callback 1 (pure 1)',HANDLER)
  for forbidden in ('writeIORef','Focus','emit','gObjectRef','peek','poke','free','get_event'):
   self.assertNotIn(forbidden,HANDLER)
  self.assertIn("atomicModifyIORef' contextFault (\\_ -> (True, ()))",source)
 def test_elm_key_default_and_native_escape_are_unchanged(self):
  source=Path(args.renderer).read_text()
  self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),args.renderer_sha256)
  self.assertIn('preventDefaultOn "keydown" (keyboardContextDecoder (send contextWire))',source)
  self.assertIn('D.succeed (contextMessage,True)',source)
  module=Path(args.module).read_text();baseline=Path(args.baseline).read_text()
  begin='      -- Capture-phase key observation';end='      -- gtk_widget_add_controller'
  self.assertEqual(module[module.index(begin):module.index(end)],baseline[baseline.index(begin):baseline.index(end)])
 def test_bounded_wrong_abi_role_return_and_registration_mutations_refuse(self):
  source=Path(args.module).read_text();self.assertTrue(callback_contract(source))
  for seed in range(32):
   changes=[(TYPE,TYPE.replace(' -> Ptr ()',' -> Ptr MvpObject -> Ptr ()')),(TYPE,TYPE.replace('IO CInt','IO ()')),(HANDLER,HANDLER.replace('callback 1 (pure 1)','callback 0 (pure 0)')),(HANDLER,HANDLER.replace('[bView, pView]','[cView]')),(HANDLER,HANDLER.replace('acquireSignal visibleView','connectProcessSignal contextOwner visibleView')),(HANDLER,HANDLER.replace('context-menu','context-menu-dismissed')),(WRAPPER,''),(HANDLER,'')]
   before,after=changes[seed%len(changes)]
   self.assertFalse(callback_contract(source.replace(before,after,1)),seed)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--module',required=True);p.add_argument('--baseline',required=True);p.add_argument('--gir',required=True);p.add_argument('--header',required=True);p.add_argument('--renderer',required=True);p.add_argument('--renderer-sha256',required=True);args,rest=p.parse_known_args();unittest.main(argv=[__file__,*rest])
