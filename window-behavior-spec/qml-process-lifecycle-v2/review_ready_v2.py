from pathlib import Path
import hashlib,json,os,stat,re
B=Path(__file__).resolve().parent
V5=Path('/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not list(B.glob('*.cpp'))
 proof=json.loads((B/'formal-before-runtime.json').read_text());assert proof['result']=='pass'and proof['sourceUnchanged'];assert all(sha(p)==h for p,h in proof['inputs'].items())
 inputs={};links={}
 def add(p):
  p=Path(p).absolute()
  for q in (p,*p.parents):
   if q.is_symlink():links[str(q)]=os.readlink(q)
  q=p.resolve(strict=True);inputs[str(q)]={'sha256':sha(q),'mode':stat.S_IMODE(q.stat().st_mode)}
 for p in B.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and p.name not in ('formal-review-inputs.json','formal-review-ready.json'):add(p)
 predecessor=json.loads((B/'reviewed-predecessor.json').read_text());assert sha(predecessor['path'])==predecessor['sha256'];add(predecessor['path'])
 old=json.loads(Path(predecessor['path']).read_text())
 for name,row in old['inputs'].items():
  assert sha(name)==row['sha256']and stat.S_IMODE(Path(name).stat().st_mode)==row['mode'];add(name)
 for p in ['/usr/lib/qt6/qml/Quickshell/Io/quickshell-io.qmltypes','/usr/include/qt6/QtCore/qprocess.h','/usr/include/qt6/QtCore/qvariant.h','/usr/include/qt6/QtCore/qmetatype.h','/home/hoskinson/src/quickshell-accessibility/src/io/process.hpp','/home/hoskinson/src/quickshell-accessibility/src/io/process.cpp','/home/hoskinson/src/quickshell-accessibility/src/io/datastream.hpp','/home/hoskinson/src/quickshell-accessibility/src/io/datastream.cpp','/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/pin_helper.py','/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/pin_capture.py','/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/widget_v66/PinWindowMenu.qml','/home/hoskinson/window-integration-qa/pin-helper-v1-root-source-handoff-v1.json','/home/hoskinson/window-integration-qa/pin-input-episode-v2-component-handoff-v1.json','/home/hoskinson/window-integration-qa/qa_run.py','/home/hoskinson/window-integration-qa/qa_launch.py']:
  add(p)
 named=int(re.search(r'(\d+) passing',proof['commands'][0]['stdout'])[1]);assert named==74
 packet={'inputs':inputs,'links':links,'registryImplemented':False,'QMLSemanticsChanged':False,'nativeLaunch':False,'mainChanges':False,'rootReviewRequiredBeforeRuntime':True,'localQuickshellRevisionEquivalenceClaim':False,'formalNamedCases':named,'formalRandomTraces':2000,'formalSteps':100,'popupComponentDistinct':str(V5),'reviewedPredecessor':predecessor}
 path=B/'formal-review-inputs.json';path.write_text(json.dumps(packet,indent=2)+'\n')
 row={'result':'formal-source-review-ready','packet':str(path),'packetSHA256':sha(path),'inputs':len(inputs),'links':len(links),'formalNamedCases':named,'randomTraces':2000,'steps':100,'runtimeImplemented':False,'GUI':False,'wholeBReady':False,'rootReviewBeforeRuntime':True}
 (B/'formal-review-ready.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row))
if __name__=='__main__':main()
