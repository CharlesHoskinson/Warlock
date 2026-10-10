"""UI-016 native backing/custody checks; physical GUI acceptance is separate."""
import hashlib,json,pathlib,re,subprocess,time,sys,shlex,shutil
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
initial=sys.argv[1:]==['--initialization'];assert initial or not sys.argv[1:]
out=root/'qa/runs'/('picker-storage-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['picker-storage.qnt']+([] if initial else ['picker-storage_test.qnt'])
report={'passed':False,'protectedScope':scope,'initializationOnly':initial,'commands':[],'inputs':{str(root/'qa'/n):sha(root/'qa'/n) for n in names},'scope':'Two unique sealed native backings under original slot/byte bounds, descriptor alias without another backing, exact consumer close/export release/producer retirement and no foreign/repeated offer. No native pixels, AT or hardware memory claim.','nativeAcceptance':False,'fullReleaseAccepted':False}
for n in names:(out/n).write_bytes((root/'qa'/n).read_bytes())
commands=[('typecheck','picker-storage.qnt',['typecheck'])]
if initial:commands.append(('initialization','picker-storage.qnt',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=82810']))
else:commands += [('tests-typecheck','picker-storage_test.qnt',['typecheck']),('named','picker-storage_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=82811']),('witness-safety','picker-storage.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','twoFamiliesWitness','retainedAfterReleaseWitness','capacityRefusalWitness','--max-samples=1000','--max-steps=25','--seed=82812'])]
try:
 for name,path,args in commands:
  cmd=['quint',args[0],str(root/'qa'/path),*args[1:]];r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(r.stdout);(out/(name+'.stderr')).write_text(r.stderr);report['commands'].append({'name':name,'command':cmd,'exitCode':r.returncode});assert r.returncode==0,r.stdout+r.stderr
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',r.stdout)};assert len(counts)==3 and all(counts.values());report['witnesses']=counts
 if not initial:
  original=root/'qa/picker-storage-test.cpp';test=out/'picker-storage-test.cpp';shutil.copyfile(original,test)
  report['inputs'][str(original)]=sha(original)
  flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0'],text=True))
  command=['/usr/bin/g++','-std=c++20','-Wall','-Wextra','-Werror','-MMD','-MF',str(out/'storage.d'),'-I'+str(root/'native'),str(test),'-o',str(out/'picker-storage-test'),*flags]
  report['compilerSHA256']=sha(pathlib.Path(command[0]).resolve())
  for name,args in [('storage-compile',command),('storage-behavior',[str(out/'picker-storage-test')])]:
   result=subprocess.run(args,capture_output=True,text=True,timeout=180)
   (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
   report['commands'].append({'name':name,'command':args,'exitCode':result.returncode});assert result.returncode==0,result.stdout+result.stderr
   if name=='storage-behavior':report['storage']=__import__('json').loads(result.stdout);assert report['storage']['passed']
  dependencies=shlex.split((out/'storage.d').read_text().replace('\\\n',' ').split(':',1)[1])
  report['dependencies']={str(pathlib.Path(path).resolve()):sha(pathlib.Path(path)) for path in dependencies}
  assert sha(original)==report['inputs'][str(original)]
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
