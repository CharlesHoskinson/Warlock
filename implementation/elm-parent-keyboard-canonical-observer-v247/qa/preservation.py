#!/usr/bin/python3
import hashlib,json,pathlib,re,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def function(text,name):
 m=re.search(r'^(?:static [^\n]*|WL_EXPORT int|int)\b[^\n]*\b'+name+r'\([^\n]*\)\s*\{',text,re.M);assert m,name;depth=1;end=m.end()
 while depth:
  if text[end]=='{':depth+=1
  if text[end]=='}':depth-=1
  end+=1
 return text[m.start():end]
def main():
 out=ROOT/'qa'/f'preservation-{time.time_ns()}';out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
 def check(name,value):report['checks'].append({'name':name,'passed':value});assert value,name
 try:
  for name in ['parent-input-module.c','parent-input-client.c']:
   old=(ROOT/'original239'/name).read_text();new=(ROOT/'native'/name).read_text()
   for f in re.findall(r'^static [^\n]*?\b(\w+)\([^\n]*\)\s*\{',old,re.M):
    if f!='private_socket':check(name+':'+f,function(old,f)==function(new,f))
   if name=='parent-input-module.c':check('module-entry-guard-only',function(old,'wet_module_init').replace('if (!gate || strcmp(gate, "1")) return -1;','if (!gate || strcmp(gate, "1") || !canonical_private_runtime(getenv("XDG_RUNTIME_DIR"))) return -1;')==function(new,'wet_module_init'))
   else:check('client-main-exact',function(old,'main')==function(new,'main'))
  for name in ['parent-input.xml','surface-observer.h']:check('239-exact:'+name,sha(ROOT/'native'/name)==sha(ROOT/'original239'/name))
  check('225-actual-header-exact',sha(ROOT/'native/surface-observer.h')==sha(ROOT.parent/'elm-parent-surface-observer-v225/native/surface-observer.h'))
  report.update(passed=True,inputs={str(p.relative_to(ROOT)):sha(p) for name in ['original239','native'] for p in (ROOT/name).iterdir() if p.is_file()})
 except Exception as e:report['error']=repr(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
