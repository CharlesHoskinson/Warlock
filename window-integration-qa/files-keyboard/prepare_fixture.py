from pathlib import Path
import shutil,re
B=Path(__file__).resolve().parent; P=B/'qa-app'
assert not P.exists(), 'Never replace an active fixture tree'
shutil.copytree(B/'app',P)
for f in P.rglob('*.qml'):
 s=f.read_text()
 s=re.sub(r'\bid:\s*(\w+)(?!\w)',lambda m:m.group(0) if re.search(r'Component\s*\{\s*$',s[:m.start()]) else m.group(0)+'; objectName:"'+f.stem+'.'+m.group(1)+'"',s)
 f.write_text(s)
f=P/'explorer/Explorer.qml';s=f.read_text().replace('title: "Files"','title: "Files Keyboard QA"');f.write_text(s)
f=P/'shell.qml';s=f.read_text().replace('import QtQuick','import QtQuick\nimport "'+(P/'FixtureKeys').as_uri()+'"',1)
a=s.index('  Widget {');b=s.index('  Explorer {',a);s=s[:a]+s[b:]
s=s.replace('target: "files"','target: "files-keyboard-qa"')
s=s.replace('    function state():', '''    function key(key:int,mods:int):bool { return FixtureKeys.tap(explorer,key,mods) }
    function focus(name:string):bool {
      function find(o) { if(o.objectName===name || o.accessibleName===name) return o;var ch=o.children || [];for(var i=0;i<ch.length;i++){var r=find(ch[i]);if(r)return r};return null }
      var item=find(explorer.contentItem);if(!item)return false;item.forceActiveFocus();return true
    }
    function locus():string { return FixtureKeys.focus(explorer) }
    function state():''')
f.write_text(s)
shutil.copytree(B/'fixture-keys',P/'FixtureKeys',ignore=shutil.ignore_patterns('build'))
shutil.copy2(B/'fixture-keys/build/libfixturekeys.so',P/'FixtureKeys/libfixturekeys.so')
# Isolated directory data contains no user paths or files.
home=B/'isolated-home';(home/'fixture/subfolder').mkdir(parents=True,exist_ok=True)
(home/'fixture/alpha.txt').write_text('fixture\n');(home/'fixture/beta.txt').write_text('fixture\n')
