"""Explicit inverse of B17 diagnostic additions for inherited source comparisons.
No native/feature execution is projected. This runner changes only the two source
reads in unchanged predecessor preservation tests; focused tests verify exact
V16 byte reconstruction and every original oracle AST separately.
"""
from pathlib import Path
import runpy,sys
from unittest.mock import patch
B=Path(__file__).resolve().parent
PATCHES={'private_session.py': [('from continuation_evidence import ContinuationEvidence\n', ''), (' continuation_trace=None\n', ''), ("  record=continuation_trace.begin_dom() if continuation_trace is not None else None\n  try:value=cdp.dom(session_id)\n  except Exception as error:\n   if record is not None:continuation_trace.dom_error(record,error)\n   raise\n  if record is not None:continuation_trace.end_dom(record,value)\n  assert value['url']==(B/'compose.html').as_uri() and value['title']=='Private local draft QA';return value\n", "  value=cdp.dom(session_id);assert value['url']==(B/'compose.html').as_uri() and value['title']=='Private local draft QA';return value\n"), ("  if continuation_trace is None:\n   result=subprocess.run(['/usr/bin/wtype','-d','20','--',text],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)\n  else:\n   result=continuation_trace.run_wtype(['/usr/bin/wtype','-d','20','--',text],env)\n", "  result=subprocess.run(['/usr/bin/wtype','-d','20','--',text],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)\n"), ("   more='-continued'+str(iteration)\n   diagnostic_expected=prior['value'][:prior['selection'][0]]+more+prior['value'][prior['selection'][1]:]\n   evidence_path=out/('continuation-'+str(iteration)+'.json')\n   continuation_trace=ContinuationEvidence(evidence_path,obs,native,browser.pid,owned_roots['browser']['start'],identities['browser'],session_id)\n   report.setdefault('continuationEvidencePaths',[]).append(str(evidence_path))\n   continuation_trace.prepare(returned,diagnostic_expected,more,env)\n   old_inputs=len([r for r in returned['events'] if r['type']=='input' and r['trusted']]);type_text(more)\n", "   more='-continued'+str(iteration);old_inputs=len([r for r in returned['events'] if r['type']=='input' and r['trusted']]);type_text(more)\n"), ('   continuation_trace=None\n', '')], 'run_native.py': [("PROBE=B/'native-keyboard-probe/libqt-modal-probe.so'\n", "PROBE=QA/'qt-modal-private-v9/native-probe/libqt-modal-probe.so'\n")]}
def project(path,text):
 if Path(path).parent==B and Path(path).name in PATCHES:
  for added,old in PATCHES[Path(path).name]:
   if not added or text.count('\n'+added)!=1:raise AssertionError('Exact B17 diagnostic projection shape changed:'+str(path))
   text=text.replace('\n'+added,'\n'+old,1)
 return text

def main():
 name=sys.argv[1];assert name in {'test_geometry_source.py','test_focus_setup.py','test_press_receipt.py'}
 read_text=Path.read_text;read_bytes=Path.read_bytes
 def text_read(path,*args,**kwargs):return project(path,read_text(path,*args,**kwargs))
 def bytes_read(path):
  value=read_bytes(path)
  return project(path,value.decode()).encode() if path.parent==B and path.name in PATCHES else value
 sys.argv=[str(B/name)]
 with patch.object(Path,'read_text',text_read),patch.object(Path,'read_bytes',bytes_read):runpy.run_path(str(B/name),run_name='__main__')
if __name__=='__main__':main()
