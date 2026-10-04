"""Exact held owning dependencies; CPU/source only, never a native launch."""
import hashlib,importlib.util,json,os,pathlib,stat,sys,time,resource,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(path):
 with pathlib.Path(path).open('rb') as stream:
  h=hashlib.sha256()
  for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
 pins=json.loads((ROOT/'pins.json').read_text());files={}
 lineage_path=REPO/'implementation/elm-gtk-role-native-v238/planning-lineage.json';assert sha(lineage_path)=='839a32869dbe856a55237fb8af5b0708504940b292d2f8621909379cc6696b0d';lineage=json.loads(lineage_path.read_text())
 historical_path=pathlib.Path(lineage['historical']['path']);assert sha(historical_path)==lineage['historical']['sha256'];historical=json.loads(historical_path.read_text());current=json.loads(pathlib.Path(lineage['current']['observedSource']).read_text())
 for key in historical:
  if key!='boundedImplementationEvidence':assert historical[key]==current[key],key
 files[str(historical_path)]=sha(historical_path)
 def entry(path,row):
  path=pathlib.Path(path)
  if type(row) is str:row={'sha256':row}
  if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink'],str(path);files[str(path)]={'symlink':row['symlink']};return
  if path.is_symlink():
   assert str(path).startswith('/usr/') and path.is_file(),str(path);files[str(path)+'#symlink']={'symlink':os.readlink(path),'resolved':str(path.resolve(strict=True))}
  assert path.is_file(),str(path)
  digest=row.get('sha256')
  if str(path)==lineage['current']['observedSource'] and digest==lineage['historical']['sha256']:path=historical_path
  if digest is not None:assert sha(path)==digest,str(path);files[str(path)]=digest
  if 'size' in row:assert path.stat().st_size==row['size'],str(path)
  if 'mode' in row:
   mode=int(row['mode'],8) if type(row['mode']) is str else row['mode'];assert stat.S_IMODE(path.stat().st_mode)==mode,str(path)
 for name,digest in pins['manifests'].items():
  base=REPO/'implementation'/name;manifest=base/'component-manifest.json';entry(manifest,digest);packet=json.loads(manifest.read_text());assert packet.get('sourceHeld') is True
  for section,prefix in [('files',base),('externalFiles',None)]:
   rows=packet.get(section,{})
   for rel,row in (rows.items() if type(rows) is dict else ((r['path'],r) for r in rows)):
    if prefix is not None:assert not pathlib.Path(rel).is_absolute() and '..' not in pathlib.Path(rel).parts
    entry(prefix/rel if prefix else rel,row)
 gui=REPO/'implementation'/pins['GUI'];build=gui/pins['GUIBuild'];entry(build,pins['GUIBuildSHA256']);packet=json.loads(build.read_text());assert packet['passed']
 for rel,digest in packet['inputs'].items():
  captured=build.parent/'inputs'/rel
  # Generated GUI JS is checked against actual output artifact map below.
  if rel not in ('assets/elm.js','assets/popup.js') and captured.is_file():entry(captured,digest)
 for rel,digest in packet['artifacts'].items():entry(build.parent/rel,digest)
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope();host=load('full_gtk_private_host',ROOT/'runtime/candidate_host.py');host.verify_inputs();host.aq_tuple()
 core=json.loads((ROOT/'runtime/native-build-report.json').read_text());entry(core['binary'],core['sha256']);entry(core['plugin']['path'],core['plugin']['sha256']);entry(core['buildReport'],core['buildReportSHA256']);entry(core['pluginBuildReport'],core['pluginBuildReportSHA256']);entry(core['linkClosureReport'],core['linkClosureReportSHA256'])
 fixture=json.loads((REPO/'implementation'/pins['GTKFixture']/'client-build-report.json').read_text());assert fixture['passed'];entry(fixture['artifact']['path'],fixture['artifact']['sha256'])
 observer_root=REPO/'implementation'/'elm-keyboardless-toolkit-owning-observer-v223';observer_manifest=json.loads((observer_root/'component-manifest.json').read_text());observer=json.loads(pathlib.Path(observer_manifest['buildReport']).read_text());assert observer['passed'] and not observer['missingSymbols'];assert observer['core']['path']==core['binary'] and observer['core']['sha256']==core['sha256'];entry(observer['binary'],observer['binarySHA256'])
 probe=json.loads((REPO/'implementation'/'elm-parent-keyboard-canonical-observer-v247'/'parent-probe-build-report.json').read_text());assert json.loads((ROOT/'runtime/parent-probe-build.json').read_text())==probe
 keymap=json.loads((ROOT/'keymap-build-report.json').read_text());entry(keymap['buildReport'],keymap['buildReportSHA256']);entry(keymap['binary'],keymap['binarySHA256']);keymap_report=json.loads(pathlib.Path(keymap['buildReport']).read_text());assert keymap_report['passed']
 for section in ('inputs','artifacts','libraries','dependencies','tools'):
  for path,row in keymap_report[section].items():entry(path,row)
 domain_descriptor=ROOT/'qt-domains-build-report.json';domains=json.loads(domain_descriptor.read_text());entry(domain_descriptor,sha(domain_descriptor));entry(domains['report'],domains['sha256']);entry(domains['binary'],domains['binarySHA256']);domain_report=json.loads(pathlib.Path(domains['report']).read_text());assert domain_report['passed'];assert domain_report['sourceSHA256']==sha(ROOT/'native/qt-domains.cpp')
 for section in ('dependencies','libraries','tools'):
  for path,digest in domain_report[section].items():entry(path,digest)
 for name,row in json.loads((ROOT/'qa/owning-qt-source/origin.json').read_text())['sources'].items():entry(ROOT/'qa/owning-qt-source'/name,row)
 return host,core,fixture,observer,probe,build.parent,keymap,files

def main():
 assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
 out=ROOT/'qa'/('preflight-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False}
 for source in [pathlib.Path(__file__),ROOT/'pins.json']:(out/source.name).write_bytes(source.read_bytes())
 try:
  _,core,fixture,observer,probe,build,keymap,files=verify();report.update(passed=True,verifiedFiles=len(files),inputs=files,owningCore=core['sha256'],fixture=fixture['artifact'],eventTypes=json.loads((ROOT/'qt-domains-build-report.json').read_text())['constants'],GUIBuild=str(build))
 except BaseException as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
