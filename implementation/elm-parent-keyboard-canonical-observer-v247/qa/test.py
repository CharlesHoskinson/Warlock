import hashlib,json,resource,re,shutil,subprocess,time,xml.etree.ElementTree as E
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('client-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual source preservation and compiled client correlation with explicit request/dispatch stubs; no socket or GUI','inputs':{},'checks':[],'commands':[]}
def check(name,v):r['checks'].append({'name':name,'passed':bool(v)});assert v,name
def run(name,cmd,expected=0):
 p=subprocess.run(cmd,capture_output=True,timeout=30);(out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'argv':cmd,'exitCode':p.returncode});assert p.returncode==expected,(name,p.stderr[-2000:]);return p
try:
 for p in [Path(__file__),ROOT/'qa/client-test.c',*sorted((ROOT/'native').glob('*')),*sorted((ROOT/'original151').glob('*')),*sorted((ROOT/'original225').glob('*'))]:r['inputs'][str(p)]=sha(p)
 def function(text,name):
  m=re.search(r'^static [^\n]*\b'+name+r'\([^\n]*\)\s*\{',text,re.M);assert m,name
  depth=1;end=m.end()
  while depth:
   if text[end]=='{':depth+=1
   if text[end]=='}':depth-=1
   end+=1
  return text[m.start():end]
 for file,exceptions in [('parent-input-module.c',{'compositor_destroyed'}),('parent-input-client.c',{'global','removed','private_socket'})]:
  old=(ROOT/'original151'/file).read_text();new=(ROOT/'native'/file).read_text()
  for name in re.findall(r'^static [^\n]*?\b(\w+)\([^\n]*\)\s*\{',old,re.M):
   if name not in exceptions:check('legacy-byteexact:'+name,function(old,name)==function(new,name))
 check('intentional-private-socket-guard-change',function((ROOT/'original239/parent-input-client.c').read_text(),'private_socket')!=function((ROOT/'native/parent-input-client.c').read_text(),'private_socket'))
 a=E.parse(ROOT/'original151/parent-input.xml').getroot().find('interface');b=E.parse(ROOT/'native/parent-input.xml').getroot().find('interface');a.tail=b.tail=None;check('legacy-XML-v7-exact',E.tostring(a)==E.tostring(b))
 a=E.parse(ROOT/'original225/parent-input.xml').getroot().findall('interface')[1];b=E.parse(ROOT/'native/parent-input.xml').getroot().findall('interface')[1];a.tail=b.tail=None;check('observer-XML-v1-exact',E.tostring(a)==E.tostring(b))
 observer=ROOT.parent/'elm-parent-surface-observer-v225/native/surface-observer.h';check('actual225header-exact',sha(observer)==sha(ROOT/'native/surface-observer.h'))
 g=out/'generated';g.mkdir();src=out/'inputs';src.mkdir()
 for p in (ROOT/'native').glob('*'):shutil.copy2(p,src/p.name)
 shutil.copy2(ROOT/'qa/client-test.c',src/'client-test.c')
 for mode,name in [('client-header','parent-input-client.h'),('private-code','parent-input-protocol.c')]:run('scanner-'+mode,['/usr/bin/wayland-scanner',mode,str(src/'parent-input.xml'),str(g/name)])
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client']).decode().split()
 original=(src/'parent-input-client.c').read_text()
 def compile_case(name):
  b=out/name;run(name+'-compile',['/usr/bin/cc','-D_GNU_SOURCE','-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(g),'-I'+str(src),str(src/'client-test.c'),str(g/'parent-input-protocol.c'),*flags,'-o',str(b)]);return b
 result=run('actual-client',[str(compile_case('actual-client'))]);lines=result.stdout.decode().splitlines();r['actualCallbackChecks']=int(lines[-1].split('=')[1]);check('actual-callbacks-positive',r['actualCallbackChecks']==26)
 for name,before,after in [('wrong-allocation','client->waiting = ++client->sequence; client->received = false;','client->waiting = client->sequence; client->received = false;'),('missing-sequence-bound','!client->observer || client->sequence==UINT32_MAX ||','!client->observer ||'),('wrong-receipt-key','sequence != client->waiting || accepted > 1','accepted > 1')]:
  assert before in original;(src/'parent-input-client.c').write_text(original.replace(function(original,'send_key'),function(original,'send_key').replace(before,after,1),1) if name=='wrong-allocation' else original.replace(before,after,1));binary=compile_case(name);p=subprocess.run([str(binary)],capture_output=True,timeout=10);(out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr);check('unsafe-rejected:'+name,p.returncode!=0)
 (src/'parent-input-client.c').write_text(original)
 for p,d in r['inputs'].items():assert sha(Path(p))==d,p
 r['passed']=True
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(not r['passed'])
