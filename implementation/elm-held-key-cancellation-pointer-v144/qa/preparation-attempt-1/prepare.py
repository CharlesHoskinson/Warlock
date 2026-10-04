from pathlib import Path
import hashlib,json,shutil
repo=Path('/home/hoskinson/omarchy-windows-parity');aq=repo/'implementation/elm-parent-held-key-cancellation-v138';manifest=aq/'component-manifest.json';build=next(aq.glob('build-*/report.json'));r=json.loads(build.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copied(old,new):shutil.copytree(old,new,ignore=lambda path,names:[n for n in names if n.startswith(('native-','menu-','freeze-','replay-','test-','build-','model-','cursor-')) and (Path(path)/n).is_dir()])
def update(root):
 desc={'manifest':str(manifest),'manifestSHA256':sha(manifest),'library':r['library'],'librarySHA256':r['librarySHA256']};(root/'aq-tuple.json').write_text(json.dumps(desc,indent=2)+'\n')
root=repo/'implementation/elm-held-key-cancellation-native-v139';copied(repo/'implementation/elm-parent-held-key-native-v135',root);update(root)
p=root/'REVIEW.md';p.write_text(p.read_text()+'\nV139 preserves135 native runner byte-for-byte, only private AQ descriptor changes to frozen138. Full AQ120 headers/all exported symbols retained. V135 actual held-key failure is preserved; native cancellation must satisfy its original assertions and6s deadlines.\n')
root2=repo/'implementation/elm-held-key-cancellation-masks-v140';root2.mkdir()
for mask in range(1,4):
 dest=root2/f'mask-{mask}';copied(root,dest);(dest/'held-mask.json').write_text(json.dumps({'schema':1,'mask':mask})+'\n')
 p=dest/'qa/native.py';s=p.read_text();a="   report['beforeLoss']={'devices':before";assert a in s;s=s.replace(a,"   check('actualModifierStateMatchesHeldShift',(state['mods']!=0)==bool(MASK&2),state=state)\n"+a);p.write_text(s)
 p=dest/'REVIEW.md';p.write_text(p.read_text()+'\nMask140 adds only the Shift modifier-before-fault assertion to unchanged139 behavior. Masks1/2/3 cover A/Shift/both. Actual GTK physical key identity and exact single per-key cancellation, zero Core keys/shortcut/modifier ledgers remain mandatory.\n')
for src,name in [('elm-held-cancellation-input-v122','elm-held-key-cancellation-input-v141'),('elm-held-cancellation-geometry-v125','elm-held-key-cancellation-geometry-v142'),('elm-held-cancellation-unheld-v127','elm-held-key-cancellation-unheld-v143')]:
 dest=repo/'implementation'/name;copied(repo/'implementation'/src,dest);update(dest)
 p=dest/'REVIEW.md';p.write_text(p.read_text()+'\nFresh AQ138-only descriptor derivative. Original native runner, full owning Core89/plugin90 pair, deadlines and assertions unchanged. Historical AQ105/120 scope strings remain but mapped AQ138 digest and frozen descriptor establish actual runtime tuple.\n')
# Original held-pointer mask7 tests the retained button cancellation with new keyboard cancellation.
dest=repo/'implementation/elm-held-key-cancellation-pointer-v144';copied(repo/'implementation/elm-held-cancellation-masks-v128/mask-7',dest);update(dest)
p=dest/'REVIEW.md';p.write_text(p.read_text()+'\nFresh AQ138-only descriptor derivative of original128 mask7 pointer cancellation. Original35 checks/6s/GTK per-button recipients retained; no keyboard key is held in this regression.\n')
print('reviewed frozen AQ138 tuple; original139 oracle and masks140 plus original input/geometry/unheld/pointer regressions')
