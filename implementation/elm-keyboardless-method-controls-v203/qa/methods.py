"""Compile verbatim actual SeatManager methods with synthetic lifecycle controls."""
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('methods-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'candidate/src/managers/SeatManager.cpp';code=source.read_text();template=(ROOT/'qa/methods.cpp').read_text()
def extract(name):
 start=code.index('void CSeatManager::'+name+'(');brace=code.index('{',start);depth=1;i=brace+1
 while depth:
  if code[i]=='{':depth+=1
  elif code[i]=='}':depth-=1
  i+=1
 return code[start:i]
methods='\n\n'.join(extract(n) for n in ['setKeyboard','updateActiveKeyboardData','setKeyboardFocus'])
controls=[
 ('discards-absent-focus','    if (!m_keyboard) {','    if (!m_keyboard) return;\n    if (!m_keyboard) {'),
 ('missing-first-enter','    if (RESTORED_FOCUS && m_state.keyboardFocus == RESTORED_FOCUS && m_keyboard == KEEB) {','    if (false) {'),
 ('enters-stale-focus','RESTORED_FOCUS && m_state.keyboardFocus == RESTORED_FOCUS && m_keyboard == KEEB','RESTORED_FOCUS && m_keyboard == KEEB'),
 ('enters-old-keyboard','RESTORED_FOCUS && m_state.keyboardFocus == RESTORED_FOCUS && m_keyboard == KEEB','RESTORED_FOCUS && m_state.keyboardFocus == RESTORED_FOCUS'),
 ('drops-destroy-listener','        if (surf)\n            m_listeners.keyboardSurfaceDestroy = surf->m_events.destroy.listen([this] { setKeyboardFocus(nullptr); });','        (void)surf;'),
 ('enters-foreign-resource','if (r->resource->client() != client)','if (false && r->resource->client() != client)'),
 ('reenters-on-additional-device','!m_keyboard && KEEB ? m_state.keyboardFocus.lock()','KEEB ? m_state.keyboardFocus.lock()'),
]
report={'passed':False,'nativeAcceptance':False,'scope':'Verbatim actual C++ setter/resource methods with synthetic devices/client/surface/callback fixtures, not GTK/native/seat-policy admission evidence','source':str(source),'sourceSHA256':sha(source),'controls':[]}
try:
 (OUT/'production-methods.cpp').write_text(methods);(OUT/'template.cpp').write_text(template)
 for name,old,new in [('baseline',None,None),*controls]:
  changed=methods
  if old is not None:assert methods.count(old)==1,(name,methods.count(old));changed=methods.replace(old,new)
  p=OUT/(name+'.cpp');p.write_text(template.replace('// PRODUCTION_METHODS',changed));binary=OUT/name
  cmd=['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(binary)]
  result=subprocess.run(cmd,capture_output=True,timeout=180);(OUT/(name+'-compile.stdout')).write_bytes(result.stdout);(OUT/(name+'-compile.stderr')).write_bytes(result.stderr);assert result.returncode==0,result.stderr.decode(errors='replace')
  result=subprocess.run([str(binary)],capture_output=True,timeout=15);(OUT/(name+'.stdout')).write_bytes(result.stdout);(OUT/(name+'.stderr')).write_bytes(result.stderr)
  accepted=(result.returncode==0) if old is None else (result.returncode==1 and b'failed ' in result.stderr)
  assert accepted,(name,result.returncode,result.stderr.decode(errors='replace'))
  report['controls'].append({'name':name,'accepted':accepted,'exitCode':result.returncode,'binarySHA256':sha(binary)});print(name,accepted,flush=True)
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
