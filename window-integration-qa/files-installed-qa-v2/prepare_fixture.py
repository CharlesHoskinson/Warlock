"""Copy the actual installed app and add diagnostic names/IPC only; never edit it."""
from pathlib import Path
import hashlib,json,re,shutil
B=Path(__file__).resolve().parent;LIVE=Path.home()/'.local/share/omarchy-files'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(folder):
 app=folder/'app';shutil.copytree(LIVE,app,ignore=shutil.ignore_patterns('ui-migration.json','*.new'))
 before={str(p.relative_to(app)):digest(p) for p in app.rglob('*') if p.is_file()};changes={}
 for p in app.rglob('*.qml'):
  t=p.read_text()
  t=re.sub(r'\bid:\s*(\w+)(?!\w)',lambda m:m.group(0) if re.search(r'Component\s*\{\s*$',t[:m.start()]) else m.group(0)+'; objectName: "'+p.stem+'.'+m.group(1)+'"',t)
  p.write_text(t)
 p=app/'explorer/Explorer.qml';s=p.read_text();s=s.replace('  function grab(path) {',(B/'diagnostic-methods.qmlfrag').read_text()+'\n  function grab(path) {',1)
 s=s.replace('  function qaResize', '  property bool qaEditorAlive:true\n  function qaResize',1)
 needle='    id: content; objectName: "Explorer.content"';assert needle in s
 s=s.replace(needle,needle+'\n    Loader { active:win.qaEditorAlive; x:8;y:160;width:180;height:60;z:9999;sourceComponent:TextEdit {objectName:"QA.TextEdit";Accessible.role:Accessible.EditableText;Accessible.name:"Native editable QA";text:"ABCDEF";width:180;height:60} }',1);p.write_text(s)
 shutil.copytree(B/'FixtureKeys',app/'FixtureKeys')
 p=app/'shell.qml';s=p.read_text().replace('import QtQuick','import QtQuick\nimport "'+(app/'FixtureKeys').as_uri()+'"',1)
 a=s.index('  Widget {');z=s.index('  Explorer {',a);s=s[:a]+s[z:]
 s=s.replace('target: "files"','target: "files-keyboard-qa"').replace('if (which === "widget") widget.grab(path); else explorer.grab(path)','explorer.grab(path)')
 methods='''
    property var retainedItem:null
    function key(key:int,mods:int):bool {return FixtureKeys.tap(explorer,key,mods)}
    function locus():string {return FixtureKeys.focus(explorer)}
    function focus(name:string):bool {
      function find(o) {if(o.objectName===name || o.accessibleName===name)return o;var a=o.children || [];for(var i=0;i<a.length;i++){var x=find(a[i]);if(x)return x};return null}
      var item=find(explorer.contentItem);if(!item)return false;item.forceActiveFocus();return true
    }
    function retain(name:string):string {
      function find(o) {if(o.objectName===name || o.accessibleName===name)return o;var a=o.children || [];for(var i=0;i<a.length;i++){var x=find(a[i]);if(x)return x};return null}
      retainedItem=find(explorer.contentItem);return FixtureKeys.retain(retainedItem)
    }
    function prepareText(text:string):bool {return FixtureKeys.prepareText(text)}
    function controlProperty(key:string,value:string):bool {return FixtureKeys.controlProperty(key,value)}
    function mutate(operation:string):string {return FixtureKeys.mutate(operation)}
    function dispatch(action:string):string {return FixtureKeys.dispatch(action)}
    function rawToggle():bool {return FixtureKeys.rawAttachedToggle()}
    function mappedSet(value:string):void {explorer.visible=value==="true"}
    function editorLifetime(value:string):void {explorer.qaEditorAlive=value==="true"}
    function resize(w:string,h:string):void {explorer.qaResize(w,h)}
    function scenario(name:string):void {explorer.qaScenario(name)}
'''
 s=s.replace('    function state(): string',methods+'\n    function state(): string',1);p.write_text(s)
 after={str(p.relative_to(app)):digest(p) for p in app.rglob('*') if p.is_file()}
 (folder/'fixture-provenance.json').write_text(json.dumps({'source':'Actual installed app copied byte-for-byte before diagnostic-only instrumentation','originalInstalledBytes':before,'executedFixtureBytes':after,'diagnostics':'objectName labels, isolated IPC/Qt event helper, QA scenario/size/query methods, uninstantiated PanelWindow host omission, diagnostic TextEdit. All product action/key routing and authority guards untouched.','nativeUrl':json.loads((B/'installed-source-plan.json').read_text())['nativeDestination']},indent=2)+'\n')
 return app
