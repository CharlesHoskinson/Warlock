from pathlib import Path
import shutil,json,hashlib
base=Path(__file__).resolve().parent
app=base/'app';qa=base/'qa-app'
if qa.exists():shutil.rmtree(qa)
shutil.copytree(app,qa)
p=qa/'explorer/Explorer.qml';s=p.read_text().replace('title: "Files"','title: "Files Responsive QA"')
# Diagnostic methods exist only in copied QA source.
methods=r'''
  function qaResize(w, h) { win.visible = false; Qt.callLater(function () { win.implicitWidth = Number(w); win.implicitHeight = Number(h); win.visible = true }) }
  function qaScenario(name) {
    ctx.close(); prompt.close(); lbOpen = false; sidebarRequested = false; detailOverlayRequested = false
    if (name === "home") { go(""); return }
    if (name === "folder-list" || name === "folder-grid") { go(Fs.home + "/fixture"); viewMode = name === "folder-list" ? "list" : "grid"; return }
    if (name === "details") { selectOnly(0); if (!detailDocked) detailOverlayRequested = true; detailOpen = true }
    if (name === "sidebar") sidebarRequested = true
    if (name === "menu") { selectOnly(0); ctx.openAt(500, 300, menuFor(0)) }
    if (name === "prompt") prompt.ask("mkdir", "New folder", "New folder", null, { hint: "in " + Fs.tilde(cwd), ok: "Create" })
    if (name === "long-prompt") prompt.ask("trash", "Move selected files to Trash?", "", null, { hint: "Long file name and folder location. ".repeat(30), ok: "Trash", confirm: true, danger: true })
    if (name === "preview") { selectOnly(0); openLightbox() }
    if (name === "path") { pathbar.startEdit(); pathbar.cands = ["alpha-long-directory-name", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa"]; pathbar.candIdx = 9 }
  }
  function qaScroll(name, end) {
    function find(o) { if (o.objectName === name) return o; var a=o.children || []; for (var i=0;i<a.length;i++) { var x=find(a[i]); if(x) return x } return null }
    var f=find(content); if (!f) return "missing"
    f.contentY = end === "end" ? Math.max(0, f.contentHeight - f.height) : Number(end)
    return JSON.stringify({ y:f.contentY, height:f.height, contentHeight:f.contentHeight })
  }
  function qaProbe() {
    function box(o) { var p = o.mapToItem(content, 0, 0); return { x:p.x, y:p.y, w:o.width, h:o.height, visible:o.visible } }
    var negative = [], named = {}
    function walk(o, parentVisible) {
      var shown = parentVisible && o.visible
      if (shown && (o.width < -0.01 || o.height < -0.01)) negative.push({ item:String(o), w:o.width, h:o.height })
      if (o.objectName && shown && o.mapToItem) named[o.objectName] = box(o)
      var a = o.children || []; for (var i = 0; i < a.length; i++) walk(a[i], shown)
    }
    walk(content, true)
    return JSON.stringify({ width:width, height:height, minWidth:minimumSize.width, minHeight:minimumSize.height,
      view:view, loading:loading, count:shown.length, mode:viewMode, nsel:nsel, sidebarDocked:sidebarDocked, detailDocked:detailDocked,
      detailVisible:detail.visible, fileColumns:area.columns, cellWidth:area.cw, thumbHeight:area.th, modifiedWidth:area.wDate, kindWidth:area.wKind,
      rects:{ toolbar:box(toolbar), nav:box(nav), tools:box(tools), extraTools:box(extraTools), filter:box(filterBox), path:box(pathbar), main:box(main), files:box(area), details:box(detail), sidebar:box(side), status:box(status) },
      named:named, negative:negative })
  }
'''
s=s.replace('  function grab(path) {',methods+'\n  function grab(path) {',1)
# Name diagnostic child rectangles without changing the deliverable app.
import re
for f in qa.rglob('*.qml'):
 t=s if f==p else f.read_text()
 t=re.sub(r'Flickable \{(?!\s*id:)\s*', lambda m:m.group(0)+'objectName: \"'+f.stem+'.scroller\"; ', t)
 t=re.sub(r'\bid:\s*(\w+)(?!\w)',lambda m:m.group(0) if re.search(r'Component\s*\{\s*$', t[:m.start()]) else m.group(0)+'; objectName: "'+f.stem+'.'+m.group(1)+'"',t)
 f.write_text(t)
p=qa/'shell.qml';s=p.read_text().replace('target: "files"','target: "files-responsive-qa"')
a=s.index('  Widget {');b=s.index('  Explorer {',a);s=s[:a]+s[b:]
s=s.replace('if (which === "widget") widget.grab(path); else explorer.grab(path)', 'explorer.grab(path)')
s=s.replace('    function state(): string { return explorer.state() }','''    function state(): string { return explorer.state() }
    function resize(w: string, h: string): void { explorer.qaResize(w, h) }
    function scenario(name: string): void { explorer.qaScenario(name) }
    function probe(): string { return explorer.qaProbe() }
    function scroll(name: string, end: string): string { return explorer.qaScroll(name, end) }
    function shutdown(): void { explorer.visible = false; Quickshell.quit() }''');p.write_text(s)
home=base/'isolated-home';fixture=home/'fixture';fixture.mkdir(parents=True,exist_ok=True)
for name,content in [('alpha-long-file-name-to-test-eliding.txt','responsive fixture\n'),('beta.txt','second fixture\n'),('image.svg','<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="blue"/></svg>')]:
 (fixture/name).write_text(content)
(fixture/'subfolder').mkdir(exist_ok=True)
state=base/'isolated-state';state.mkdir(exist_ok=True)
(state/'dashboard.json').write_text(json.dumps({'pins':[str(fixture),str(home)]}))
print(qa)
