"""Generate/verify new native tuple façade and current runtime link closure, CPU only."""
import hashlib,importlib.util,json,os,pathlib,re,resource,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));from tuple import assemble,entry,sha,require

def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope;require_qa_scope();require(resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'protected core limit')
 out=ROOT/'qa'/('preflight-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'nativeReadiness':False}
 def run(name,args,env):
  p=subprocess.run(args,capture_output=True,text=True,env=env,timeout=20);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);require(p.returncode==0,name+' failed');return p.stdout
 try:
  descriptor,packets,inventory,aq=assemble();core,authority,observer=packets
  env=dict(os.environ);env['LD_LIBRARY_PATH']=str(pathlib.Path(aq['library']).parent);env.pop('LD_PRELOAD',None)
  libraries={};maps={}
  for name,packet in zip(('core307','authority319','observer315'),packets):
   output=run(name+'-ldd',['/usr/bin/ldd',packet['binary']],env);require('not found' not in output,'runtime library missing')
   selected={}
   for line in output.splitlines():
    for word in line.split():
     if word.startswith('/') and pathlib.Path(word).is_file():
      p=pathlib.Path(word).resolve();selected[str(p)]=sha(p);libraries[str(p)]=sha(p)
   maps[name]=selected
  aq_selected={p:d for p,d in maps['core307'].items() if pathlib.Path(p).name.startswith('libaquamarine.so')};require(aq_selected=={str(pathlib.Path(aq['library']).resolve()):aq['librarySHA256']},'actual AQ155 resolution')
  exports=set()
  for index,path in enumerate([core['binary'],*sorted(libraries)]):
   for line in run('exports-'+str(index),['/usr/bin/nm','-D','--defined-only',path],env).splitlines():
    fields=line.split()
    if len(fields)>=3:exports.add(fields[-1].replace('@@','@'));exports.add(fields[-1].split('@')[0])
  strong={};missing={}
  for name,packet in zip(('authority319','observer315'),(authority,observer)):
   requested=[]
   for line in run(name+'-undefined',['/usr/bin/nm','-D','--undefined-only',packet['binary']],env).splitlines():
    fields=line.split()
    if len(fields)==2 and fields[0]=='U':requested.append(fields[1])
   strong[name]=requested;missing[name]=sorted(set(requested)-exports);require(not missing[name],'strong runtime symbols missing')
  for path,digest in libraries.items():entry(path,digest,inventory)
  for tool in ('/usr/bin/ldd','/usr/bin/nm','/usr/bin/python3'):entry(pathlib.Path(tool).resolve(),sha(pathlib.Path(tool).resolve()),inventory)
  entry('/etc/ld.so.cache',sha('/etc/ld.so.cache'),inventory)
  (out/'observed-ld.so.cache').write_bytes(pathlib.Path('/etc/ld.so.cache').read_bytes())
  # Reuse exact source-closed host and source-only cleanup acquisition; import never enters or launches.
  spec=importlib.util.spec_from_file_location('own_popup_tuple_host321',ROOT/'runtime/candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);host.verify_inputs();host.aq_tuple()
  sys.path.insert(0,str(ROOT/'qa/helpers'));import owned_bus_host,private_bus,activation_import,cleanup,credentials,outcomes
  require(callable(owned_bus_host.derivative),'cleanup acquisition interface')
  closure={'passed':True,'nativeAcceptance':False,'scope':'Current AQ155 LD_LIBRARY_PATH library lookup/strong-symbol closure; no process mapping or pluginload.','libraries':libraries,'resolvedByArtifact':maps,'strongUndefined':strong,'missingSymbols':missing,'owningHeaderTreeSHA256':descriptor['owningHeaderTreeSHA256'],'currentLinkerCache':inventory['/etc/ld.so.cache'],'tools':{str(pathlib.Path(t).resolve()):inventory[str(pathlib.Path(t).resolve())] for t in ('/usr/bin/ldd','/usr/bin/nm','/usr/bin/python3')}}
  closure_path=ROOT/'runtime/runtime-link-closure.json';closure_path.write_text(json.dumps(closure,indent=2)+'\n');descriptor.update(linkClosureReport=str(closure_path),linkClosureReportSHA256=sha(closure_path));(ROOT/'runtime/native-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
  pair={'passed':True,'nativeAcceptance':False,'scope':'Fresh307/319/315 diagnostic-only compile/runtime lookup tuple, no old205 or GTK02 acceptance transfer.','nativePair':{'core':{'path':core['binary'],'sha256':core['binarySHA256']},'plugin':descriptor['plugin'],'observer':descriptor['observer'],'aquamarine':{'path':aq['library'],'sha256':aq['librarySHA256']}},'files':{name:sha(ROOT/'runtime'/name) for name in ('candidate_host.py','native-build-report.json','aq-tuple.json','parent-probe-build.json','runtime-link-closure.json')},'owningCoreComponent':descriptor['coreComponentManifest'],'owningCoreComponentSHA256':descriptor['coreComponentManifestSHA256'],'owningHeaderCount':694,'owningHeaderTreeSHA256':descriptor['owningHeaderTreeSHA256'],'reviews':descriptor['reviews']}
  (ROOT/'runtime/qa/build-pair-manifest.json').write_text(json.dumps(pair,indent=2)+'\n')
  for path,row in list(inventory.items()):entry(path,row,{})
  report.update(passed=True,verifiedFiles=len(inventory),inputs=inventory,descriptor=descriptor,descriptorSHA256=sha(ROOT/'runtime/native-build-report.json'),headerCount=694,headerTreeSHA256=descriptor['owningHeaderTreeSHA256'],resolvedRuntimeLibraries=len(libraries),strongUndefined={k:len(v) for k,v in strong.items()},missingSymbols=missing)
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
 for p in [pathlib.Path(__file__),ROOT/'qa/tuple.py',ROOT/'REQUIREMENTS.md']:(out/p.name).write_bytes(p.read_bytes())
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
