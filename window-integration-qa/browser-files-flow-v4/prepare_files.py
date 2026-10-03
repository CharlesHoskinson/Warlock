"""Copy installed real Files bytes, append observation only in its copied host."""
from pathlib import Path
import hashlib,json,os,shutil
B=Path(__file__).resolve().parent
LIVE=Path('/home/hoskinson/.local/share/omarchy-files')
APP=B/'files-app'
ADAPTER='''
  // QA-only read-only observations. Signal listener does not replace/delegate handlers.
  // Additional listeners can perturb timing: no cadence/raster claim.
  property var qaObservedItems: []
  property var qaClickEvents: []
  function qaCollect() {
    var rows=[], content=explorer.contentItem
    function walk(o) {
      if(o.accessibleName !== undefined && o.actionIdentity !== undefined && o.clicked !== undefined) {
        if(qaObservedItems.indexOf(o)<0) {
          qaObservedItems.push(o)
          o.clicked.connect(function(mouse){
            qaClickEvents.push({name:String(o.accessibleName),identity:String(o.actionIdentity),button:mouse.button,modifiers:mouse.modifiers,viewMode:explorer.viewMode,time:Date.now()})
          })
        }
        var point=o.mapToItem(content,0,0)
        rows.push({name:String(o.accessibleName),identity:String(o.actionIdentity),rect:[point.x,point.y,o.width,o.height],visible:o.visible,enabled:o.enabled,enabled2:o.enabled2,objectName:String(o.objectName)})
      }
      var children=o.children || [];for(var i=0;i<children.length;i++)walk(children[i])
    }
    walk(content)
    return JSON.stringify({pid:Quickshell.processId,instance:Quickshell.instanceId,client:[content.width,content.height],visible:explorer.visible,backingVisible:explorer.backingWindowVisible,viewMode:explorer.viewMode,buttons:rows,clicks:qaClickEvents})
  }
'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 if APP.exists():raise RuntimeError('Never overwrite an earlier copied payload')
 shutil.copytree(LIVE,APP,symlinks=True)
 original=(APP/'shell.qml').read_bytes()
 text=original.decode();marker='    function migrationStatus(): string'
 assert text.count(marker)==1
 text=text.replace(marker,'    function qaButtons(): string { return qaCollect() }\n'+marker)
 assert text.rstrip().endswith('}')
 at=text.rfind('}');text=text[:at]+ADAPTER+text[at:]
 (APP/'shell.qml').write_text(text)
 rows=[]
 for source in sorted(LIVE.rglob('*')):
  if source.is_file() and not source.is_symlink():
   copied=APP/source.relative_to(LIVE);rows.append({'live':str(source),'copy':str(copied),'liveSHA256':sha(source),'copySHA256':sha(copied),'identical':sha(source)==sha(copied)})
 changed=[r for r in rows if r['liveSHA256']!=r['copySHA256']]
 assert len(changed)==1 and changed[0]['live']==str(LIVE/'shell.qml')
 record={'installedProductChanged':False,'onlyCopiedHostChanged':changed,'source':rows,'adapter':ADAPTER,'instrumentation':'Add actual clicked signal listeners only; original handlers remain byte-identical. Read rectangles/state; no focus/action method.'}
 (B/'files-copy-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
 (B/'copied-host-observation.diff').write_text(''.join(__import__('difflib').unified_diff(original.decode().splitlines(True),text.splitlines(True),fromfile=str(LIVE/'shell.qml'),tofile=str(APP/'shell.qml'))))
 print(json.dumps({'copiedFiles':len(rows),'changedHostOnly':True,'noProcessStarted':True}))
if __name__=='__main__':prepare()
