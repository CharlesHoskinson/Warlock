"""Closed source/owning tuple CPU check; no native session is created."""
import hashlib,importlib.util,json,os,resource,shlex,subprocess,sys,time
from pathlib import Path
SLICE=Path(__file__).resolve().parents[1];REPO=SLICE.parents[1]
def sha(path):
 with Path(path).open('rb') as source:
  h=hashlib.sha256()
  for part in iter(lambda:source.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
 pins=json.loads((SLICE/'pins.json').read_text());files={}
 lineage_path=Path(pins['planningLineage']['path']);assert sha(lineage_path)==pins['planningLineage']['sha256'];lineage=json.loads(lineage_path.read_text());assert lineage['passed']
 for field in ('historical','current','registry'):assert sha(lineage[field]['path'])==lineage[field]['sha256']
 def entry(path,value):
  path=Path(path);row=value if type(value) is dict else {'sha256':value}
  if 'symlink' in row:
   assert path.is_symlink() and str(path.readlink())==row['symlink'],str(path)
  if 'sha256' in row:
   expected=row['sha256']
   if str(path)==lineage['current']['path'] and expected==lineage['historical']['sha256']:expected=lineage['current']['sha256']
   assert sha(path)==expected,str(path);files[str(path)]=expected
 for name,digest in pins['manifests'].items():
  root=REPO/'implementation'/name;manifest=root/'component-manifest.json';entry(manifest,digest);data=json.loads(manifest.read_text());assert data['sourceHeld']
  for section,base in [('files',root),('externalFiles',None)]:
   values=data.get(section,{})
   if type(values) is dict:
    for path,value in values.items():entry((base/path) if base is not None else path,value)
   else:
    for value in values:entry(base/value['path'] if base else value['path'],value)
 for path,digest in pins['files'].items():entry(path,digest)
 host=load('gtk_role_private_host',SLICE/'runtime/candidate_host.py');host.original.qa.require_qa_scope();host.verify_inputs();host.aq_tuple()
 assert (SLICE/'runtime/candidate_host.py').read_bytes()==(REPO/'implementation/elm-xdg-pointer-current-tuple-v229/runtime/candidate_host.py').read_bytes()
 fixture=json.loads((REPO/'implementation/elm-gtk-role-journal-fixture-v233/client-build-report.json').read_text())
 observer=json.loads((REPO/'implementation/elm-toolkit-popup-owned-observer-v240/component-manifest.json').read_text());build=json.loads(Path(observer['buildReport']).read_text());assert build['passed'] and not build['missingSymbols']
 core=json.loads((SLICE/'runtime/native-build-report.json').read_text());assert build['core']['path']==core['binary'] and build['core']['sha256']==core['sha256'];entry(build['binary'],build['binarySHA256'])
 probe=json.loads((REPO/'implementation/elm-parent-keyboard-surface-observer-v239/parent-probe-build-report.json').read_text());probe_build=json.loads(Path(probe['buildReport']).read_text());assert probe_build['passed']
 entry(probe['buildReport'],probe['buildReportSHA256'])
 assert json.loads((SLICE/'runtime/parent-probe-build.json').read_text())=={'buildReport':probe['buildReport'],'buildReportSHA256':probe['buildReportSHA256']}
 for field in ('module','client'):entry(probe[field]['path'],probe[field]['sha256'])
 return host,core,fixture,build,probe,files

def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=SLICE/'qa'/('preflight-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
 try:
  host,core,fixture,observer,probe,files=verify();report['inputs']=files
  # Actual enum values compiled from the same installed GTK header captured233.
  header=Path('/usr/include/gtk-4.0/gdk/gdkevents.h');fixture_report=json.loads(Path(fixture['client']['buildReport']).read_text());assert fixture_report['dependencies'][str(header)]==sha(header)
  source=out/'gdk-enums.c';source.write_text('#include <stdio.h>\n#include <gdk/gdk.h>\nint main(void){printf("{\\"button-press\\":%d,\\"button-release\\":%d,\\"key-press\\":%d,\\"key-release\\":%d}\\n",GDK_BUTTON_PRESS,GDK_BUTTON_RELEASE,GDK_KEY_PRESS,GDK_KEY_RELEASE);return 0;}\n')
  flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','gtk4'],text=True));binary=out/'gdk-enums';cmd=['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-MD','-MF',str(out/'gdk-enums.d'),*flags,str(source),'-o',str(binary)]
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60);(out/'compile.stdout').write_bytes(result.stdout);(out/'compile.stderr').write_bytes(result.stderr);assert result.returncode==0
  result=subprocess.run([str(binary)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3);assert result.returncode==0;types=json.loads(result.stdout);assert set(types)=={'button-press','button-release','key-press','key-release'} and all(type(v) is int for v in types.values());report['eventTypes']=types;report['enumCompilation']={'argv':cmd,'sourceSHA256':sha(source),'binarySHA256':sha(binary),'compilerSHA256':sha('/usr/bin/cc'),'headerSHA256':sha(header)}
  report['checks']=[{'name':'held source inventories + external closure + exact470/plugin471/AQ155/233/240/239', 'passed':True,'files':len(files)},{'name':'actual owning GTK enum compilation','passed':True}];report['passed']=True
 finally:
  report['sourceSHA256']=sha(__file__);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
if __name__=='__main__':main()
