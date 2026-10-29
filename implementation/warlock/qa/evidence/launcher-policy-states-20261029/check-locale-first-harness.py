#!/usr/bin/python3
"""Protected focused compilation of current original launcher-policy witnesses."""
import hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';OUT=Path(__file__).resolve().parent/'output-locale-v1'
sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1);OUT.mkdir(exist_ok=False)
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':'Current compiled policy and state projection; no native presentation, input or AT acceptance','protectedScope':scope,'driverSHA256':sha(__file__),'commands':[]}
 try:
  paths=sorted((P/'src').rglob('*.elm'))+sorted((P/'qa').glob('*.elm'))+[P/'elm.json',P/'qa/feedback-replay.js',P/'adapter/taskbar_catalog.py',P/'adapter/catalog_authority.py']
  assert not any(p.is_symlink() for p in paths)
  before={str(p):sha(p) for p in paths};report['sourcesBefore']=before
  spec=importlib.util.spec_from_file_location('held_search_toolchain',H/'qa/toolchain.py');toolchain=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolchain);pinned=toolchain.verify()
  compiler=H/pinned['compiler'];report['compilerSHA256']=sha(compiler);assert report['compilerSHA256']=='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
  workspace=OUT/'workspace';workspace.mkdir();(workspace/'src').symlink_to(P/'src',target_is_directory=True);(workspace/'qa').symlink_to(P/'qa',target_is_directory=True)
  config=json.loads((P/'elm.json').read_text());config['source-directories']=['src','qa'];(workspace/'elm.json').write_text(json.dumps(config))
  shutil.copytree(H/pinned['elmHome'],OUT/'elm-home');env={**os.environ,'ELM_HOME':str(OUT/'elm-home'),'PYTHONDONTWRITEBYTECODE':'1'}
  def run(name,args):
   proc=subprocess.run([str(x) for x in args],cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
   for stream,data in [('stdout',proc.stdout),('stderr',proc.stderr)]: (OUT/(name+'.'+stream)).write_bytes(data)
   report['commands'].append({'name':name,'argv':[str(x) for x in args],'exit':proc.returncode,'stdoutSHA256':sha(OUT/(name+'.stdout')),'stderrSHA256':sha(OUT/(name+'.stderr'))})
   assert proc.returncode==0,(name,proc.returncode)
  run('compile-locale',[compiler,'make','qa/CatalogLocaleReplay.elm','--optimize','--output='+str(OUT/'locale.js')])
  nodeExecutable=Path(shutil.which('node')).resolve(strict=True);report['node']={'path':str(nodeExecutable),'sha256':sha(nodeExecutable)}
  node="const fs=require('node:fs'),vm=require('node:vm');const [file,flags,out]=process.argv.slice(2);const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(file,'utf8'),sandbox);const app=sandbox.Elm.CatalogLocaleReplay.init({flags:JSON.parse(fs.readFileSync(flags,'utf8'))});app.ports.outgoing.subscribe(rows=>{fs.writeFileSync(out,JSON.stringify(rows,null,2));process.exit(0);});setTimeout(()=>process.exit(2),3000);"
  (OUT/'replay.js').write_text(node)
  sys.path.insert(0,str(P/'adapter'));from catalog_authority import Authority
  home=OUT/'data';applications=home/'applications';applications.mkdir(parents=True);cache=OUT/'cache';cache.mkdir(mode=0o700)
  desktop='[Desktop Entry]\nType=Application\nName=BaseFiles\nGenericName=BaseManager\nKeywords=BaseFolders;\nName[de]=Dateien\nName[de_DE@formal]=FormelleDateien\nGenericName[de@formal]=DokumentVerwaltung\nKeywords[de]=Ordner;\nName[fr]=Fichiers\nGenericName[fr]=Gestionnaire\nKeywords[fr]=Dossiers;\nExec=/nonexistent-warlock-exec-sentinel\n'
  for name in ['z-locale.desktop','a-locale.desktop']:(applications/name).write_text(desktop)
  report['desktopInputs']={str(p):sha(p) for p in applications.iterdir()}
  authority=Authority(str(home),[],str(cache));report['localeCases']=[];checks={}
  cases=[('all-precedence',{'LC_ALL':'de_DE.UTF-8@formal','LC_MESSAGES':'fr_FR.UTF-8','LANG':'C'},'FormelleDateien','DokumentVerwaltung','Ordner'),('messages-precedence',{'LC_MESSAGES':'fr_FR.UTF-8','LANG':'de_DE.UTF-8@formal'},'Fichiers','Gestionnaire','Dossiers'),('lang-fallback',{'LANG':'de_CH.UTF-8@formal'},'Dateien','DokumentVerwaltung','Ordner'),('unlocalized-C',{'LANG':'C'},'BaseFiles','BaseManager','BaseFolders')]
  expected_ids=['a-locale.desktop','z-locale.desktop'];prior_generation=0
  for name,locale,name_expected,generic_expected,keyword_expected in cases:
   for key in ['LC_ALL','LC_MESSAGES','LANG']:os.environ.pop(key,None)
   os.environ.update(locale);snapshot=authority.snapshot();cached=authority.snapshot();assert cached==snapshot
   assert int(snapshot['generation'])>prior_generation;prior_generation=int(snapshot['generation'])
   assert all(set(e)=={'id','name','iconHint','wmclass','genericName','keywords'} for e in snapshot['entries'])
   assert all(e['name']==name_expected and e['genericName']==generic_expected and e['keywords']==[keyword_expected] for e in snapshot['entries'])
   queries=[name_expected.upper(),generic_expected.upper(),keyword_expected.upper(),name_expected[:4]+' '+generic_expected[:4]+' '+keyword_expected[:4],'nonexistent-warlock-exec-sentinel','absent-query-term']
   flags=OUT/(name+'-flags.json');flags.write_text(json.dumps({'snapshot':snapshot,'queries':queries}));output=OUT/(name+'-result.json')
   run('replay-'+name,[nodeExecutable,OUT/'replay.js',OUT/'locale.js',flags,output]);rows=json.loads(output.read_text());assert rows['ok'] and rows['lifetime']==snapshot['lifetime'] and rows['generation']==snapshot['generation']
   assert all([e['id'] for e in r['entries']]==(expected_ids if i<4 else []) for i,r in enumerate(rows['results']))
   assert all(e['name']==name_expected and e['genericName']==generic_expected and e['keywords']==[keyword_expected] for e in rows['entries'])
   checks[name]=True;report['localeCases'].append({'name':name,'environment':locale,'snapshot':snapshot,'compiled':rows,'cachedSnapshotEqual':True})
  flags=OUT/'invalid-flags.json';snapshot={**snapshot,'generation':1};flags.write_text(json.dumps({'snapshot':snapshot,'queries':['BaseFiles']}));output=OUT/'invalid-result.json'
  run('reject-numeric-generation',[nodeExecutable,OUT/'replay.js',OUT/'locale.js',flags,output]);assert not json.loads(output.read_text())['ok'];checks['numeric-authority-rejected']=True
  assert sha(nodeExecutable)==report['node']['sha256'];report['checks']=checks
  report['sourcesAfter']={str(p):sha(p) for p in paths};assert report['sourcesAfter']==before;toolchain.verify();assert sha(__file__)==report['driverSHA256'];report['passed']=True
 except Exception as e: report['error']=repr(e);(OUT/'failure.txt').write_text(traceback.format_exc())
 finally:(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}))
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
