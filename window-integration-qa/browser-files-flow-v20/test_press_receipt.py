"""CPU-only actual Qt JavaScript/Connections tests and exact source preservation."""
import ast,json,subprocess
from pathlib import Path
import unittest
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v15')
CASES=['qtSignalOrder','keyboardCannotProducePointerReceipt','qtCancellation','noPress','invisible',
 'disabled','disabled2','emptyName','emptyIdentity','badPressButton','badPressModifiers','booleanPressMetadata',
 'fractionalPressMetadata','boundedGeneration','badOwnerToken','immutable','cancel','destroy','newPress',
 'replacedItem','replacedArea','changedOwnerToken','changedGeneration','badClickButton','badClickModifiers',
 'booleanClickMetadata','reactiveMutation','duplicateClick']
class QtReceipt(unittest.TestCase):pass
def case(name):
 def test(self):
  p=subprocess.run([str(B/'receipt-cpu'),str(B/'receipt-fixture.qml'),name],capture_output=True,text=True,timeout=8)
  self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertTrue(json.loads(p.stdout)['ok'])
 return test
for name in CASES:setattr(QtReceipt,'test_'+name,case(name))

class Preserve(unittest.TestCase):
 def test_original_private_flow_all_byte_exact(self):self.assertEqual((B/'private_session.py').read_bytes(),(OLD/'private_session.py').read_bytes())
 def test_original15_oracle_asts_exact(self):
  def calls(path):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(path.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(calls(B/'private_session.py'),calls(OLD/'private_session.py'))
 def test_real_product_qml_and_scripts_exact(self):
  for p in (OLD/'files-app').rglob('*'):
   if p.is_file()and p.name!='shell.qml':self.assertEqual((B/p.relative_to(OLD)).read_bytes(),p.read_bytes(),str(p.relative_to(OLD)))
 def test_all_old_runtime_python_and_models_exact(self):
  for p in [*OLD.glob('*.py'),*OLD.glob('*.qnt')]:
   if p.name not in {'metrics_offline.py','freeze_packet.py'}:self.assertEqual((B/p.name).read_bytes(),p.read_bytes(),p.name)
 def test_shell_exact_outside_qa_additions(self):
  old=(OLD/'files-app/shell.qml').read_text();new=(B/'files-app/shell.qml').read_text()
  new=new.replace('import "PressReceipt.js" as PressReceipt\n','',1)
  start=new.index('  property var qaPointerObservers: []');end=new.index('  function qaCollect()',start)
  new=new[:start]+new[end:]
  start=new.index('          var area=qaMouseArea(o)');end=new.index('\n        }\n',start)+1
  oldstart=old.index('          o.clicked.connect(');oldend=old.index('\n        }\n',oldstart)+1
  new=new[:start]+old[oldstart:oldend]+new[end:]
  self.assertEqual(new,old)
 def test_exact_copied_callback_bodies_in_cpu_qt_fixture(self):
  btn=(B/'files-app/Ui/Btn.qml').read_text();ex=(B/'files-app/explorer/Explorer.qml').read_text();fixture=(B/'receipt-fixture.qml').read_text()
  for line in ('onPressed: root.forceActiveFocus()','onClicked: (m) => { if (root.enabled2) root.clicked(m) }'):
   self.assertIn(line,btn);self.assertIn(line,fixture)
  for code in ('win.viewMode = win.viewMode === "list" ? "grid" : "list"','win.viewMode === "list" ? "Show grid" : "Show list"'):
   self.assertIn(code,ex);self.assertIn(code,fixture)
  shell=(B/'files-app/shell.qml').read_text()
  begin=shell.index('    Connections {');end=shell.index('\n  function qaMouseArea',begin)
  block=shell[begin:end].rsplit('\n  }',1)[0]
  self.assertIn(block,fixture)
 def test_no_gui_application_in_cpu_runner(self):
  text=(B/'receipt_cpu.cpp').read_text();self.assertIn('QCoreApplication app',text);self.assertNotIn('QGuiApplication',text);self.assertNotIn('QQuickWindow',text)
 def test_source_only_connections_no_original_handler_replacement(self):
  text=(B/'files-app/shell.qml').read_text();self.assertIn('target: mouseArea',text)
  self.assertIn('function onPressed(mouse)',text);self.assertIn('function onCanceled()',text)
  self.assertIn('function onClicked(mouse)',text);self.assertNotIn('function onPressedChanged',text)
  self.assertNotIn('o.clicked.connect',text);self.assertNotIn('forceActiveFocus',text)

if __name__=='__main__':unittest.main()
