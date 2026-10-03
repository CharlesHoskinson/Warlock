"""Source-only inverse of B19 host additions; never native/runtime routing."""
from pathlib import Path
import json,runpy,sys
from unittest.mock import patch
B=Path(__file__).resolve().parent
CHANGE=json.loads((B/'startup-source-insertion.json').read_text())
def project(path,text):
 if Path(path).parent!=B:return text
 row=CHANGE.get(Path(path).name)
 if not row:return text
 if Path(path).name=='run_native.py':
  assert text.count(row['add'])==1;return text.replace(row['add'],'',1)
 assert text.count(row['new'])==1 and text.count(row['importNew'])==1
 return text.replace(row['new'],row['old'],1).replace(row['importNew'],row['importOld'],1)
def main():
 name=sys.argv[1];assert name.startswith('test_')and name.endswith('.py')and name!='test_output_readiness.py'
 original_text=Path.read_text;original_bytes=Path.read_bytes
 def text(path,*args,**kwargs):return project(path,original_text(path,*args,**kwargs))
 def raw(path):
  value=original_bytes(path);return project(path,value.decode()).encode()if path.parent==B and path.name in CHANGE else value
 with patch.object(Path,'read_text',text),patch.object(Path,'read_bytes',raw):
  if name in {'test_geometry_source.py','test_focus_setup.py','test_press_receipt.py','test_continuation_evidence.py'}:
   sys.argv=[str(B/'keyboard_preservation_projection.py'),name];runpy.run_path(str(B/'keyboard_preservation_projection.py'),run_name='__main__')
  else:sys.argv=[str(B/name)];runpy.run_path(str(B/name),run_name='__main__')
if __name__=='__main__':main()
