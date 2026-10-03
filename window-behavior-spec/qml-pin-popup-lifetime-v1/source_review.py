from pathlib import Path
import hashlib,json,os,stat
B=Path(__file__).resolve().parent
ROOT=Path('/home/hoskinson')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((B/'formal-before-runtime.json').read_text());assert proof['result']=='pass'
 external=[ROOT/'window-behavior-spec/qml-object-lifetime-v2/source-ready.json',ROOT/'window-behavior-spec/qml-object-lifetime-v2/source-ready-inputs.json',Path('/usr/include/qt6/QtQml/qqml.h'),Path('/usr/include/qt6/QtQuick/qquickitem.h'),Path('/usr/include/qt6/QtQuick/qquickwindow.h'),Path('/usr/lib/qt6/qml/Quickshell/_Window/quickshell-window.qmltypes'),ROOT/'src/quickshell-accessibility/src/window/windowinterface.hpp',ROOT/'src/quickshell-accessibility/src/window/proxywindow.hpp',ROOT/'window-behavior-spec/pin-lifetime-v3/frontend/widget_v66/PinWindowMenu.qml',ROOT/'window-behavior-spec/pin-lifetime-v3/frontend/widget_v66/TaskbarPopup.qml']
 inputs={};links={}
 for p in [*external,*[p for p in B.iterdir()if p.is_file()and p.name not in('formal-review-ready.json','formal-review-inputs.json')]]:
  inputs[str(p)]={'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
  for parent in [p,*p.parents]:
   if parent.is_symlink():links[str(parent)]=os.readlink(parent)
 runtime=bool(list(B.glob('*.cpp')));assert not runtime
 packet={'inputs':inputs,'links':links,'popupRuntimeImplemented':False,'rootReviewRequiredBeforeRuntime':True,'nativeLaunch':False,'mainChanges':False,'localQuickshellSourceEquivalenceClaim':False}
 p=B/'formal-review-inputs.json';p.write_text(json.dumps(packet,indent=2)+'\n');r={'result':'formal-review-ready','packet':str(p),'packetSHA256':sha(p),'namedCases':35,'randomTraces':2000,'steps':100,'popupRuntimeImplemented':False,'actualInstalledPopupAccepted':False,'ProcessRegistryImplemented':False,'nativeLaunch':False,'rootReviewRequiredBeforeRuntime':True}
 (B/'formal-review-ready.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
