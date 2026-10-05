"""Commit exact held owner files without applying archive Git filters."""
import hashlib,json,os,pathlib,stat,subprocess
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='63868acc7ef86d0d420a8e2be5ac2acd854ff096'
assert not git(['diff','--cached','--name-only'])
foreign=git(['diff','--name-only'],text=True).splitlines();assert foreign==[
 'docs/elm-roadmap/delivery/implementation-status.json',
 'implementation/elm-shared-observation-recovery-v121/README.md',
 'implementation/elm-shared-observation-recovery-v121/SPEC.md',
 'implementation/elm-shared-observation-recovery-v121/src/Shell.elm',
 'implementation/elm-unsent-operation-disposition-v122/qa/test.py']
foreignSHA={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in foreign}
roots=['warlock-preview-provider-v7','warlock-preview-provider-v8','warlock-preview-provider-v9','warlock-preview-provider-v10','warlock-client-provider-native-v1','warlock-client-source-decoder-checks-v1','warlock-source-presenter-model-v1','warlock-source-presenter-model-v2']
paths=set()
for name in roots:
 root=REPO/'implementation'/name;manifest=root/'component-manifest.json';held=json.loads(manifest.read_text());assert held['sourceHeld']
 for rel,row in held['files'].items():
  p=root/rel
  if row['kind']=='symlink':assert p.is_symlink() and os.readlink(p)==row['target']
  else:assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'] and p.stat().st_size==row['size'],p
  paths.add(str(p.relative_to(REPO)))
 paths.add(str(manifest.relative_to(REPO)))
for rel in ['docs/warlock-preview/v11','docs/warlock-preview/v12','docs/warlock-repository/v10/publication','implementation/warlock-preview-provider-v11']:
 for p in (REPO/rel).glob('*'):
  if p.is_file():paths.add(str(p.relative_to(REPO)))
for name in ['20261005T220950.322483Z--f6779148-8f5d-4bdf-8a0f-044184e486f2--f97800e4068d4181b0c711b9b8114c2b.json','20261005T223126.831047Z--f6779148-8f5d-4bdf-8a0f-044184e486f2--4b40c18bce89472b9034e3f7c4728ad4.json','20261005T224026.933003Z--f6779148-8f5d-4bdf-8a0f-044184e486f2--cf49d6933cf841f4b79ffd2f3b841c8f.json']:
 paths.add('docs/elm-roadmap/delivery/build-loop-events/'+name)
regular=sorted(p for p in paths if not (REPO/p).is_symlink());assert all('\n' not in p and '\t' not in p for p in paths)
hashes=git(['hash-object','-w','--no-filters','--stdin-paths'],input=('\n'.join(regular)+'\n').encode()).decode().splitlines();assert len(hashes)==len(regular)
rows=[]
for p,h in zip(regular,hashes):rows.append(('100755' if os.access(REPO/p,os.X_OK) else '100644',h,p))
for p in sorted(paths-set(regular)):
 h=git(['hash-object','-w','--stdin','--no-filters'],input=os.readlink(REPO/p).encode()).decode().strip();rows.append(('120000',h,p))
index=''.join(mode+' '+h+'\t'+p+'\0' for mode,h,p in rows).encode();git(['update-index','-z','--index-info'],input=index)
staged=set(git(['diff','--cached','--name-only'],text=True).splitlines());assert staged<=paths and not (staged & set(foreign))
git(['commit','-m','Integrate typed client preview sources and retained physical receipts'])
head=git(['rev-parse','HEAD'],text=True).strip();tree={}
for entry in git(['ls-tree','-rz',head,'--',*sorted(paths)]).split(b'\0'):
 if not entry:continue
 fields,name=entry.split(b'\t',1);mode,kind,h=fields.decode().split();assert kind=='blob';tree[name.decode()]=(mode,h)
assert all(tree[p]==(mode,h) for mode,h,p in rows)
assert git(['diff','--name-only'],text=True).splitlines()==foreign
assert all(hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h for p,h in foreignSHA.items())
(OUT/'source-commit.json').write_text(json.dumps({'schema':1,'sourceCommit':head,'ownedHeldFiles':len(rows),'changedOwnedFiles':len(staged),'foreignChangesPreserved':foreign,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'sourceCommit':head,'ownedHeldFiles':len(rows),'changedOwnedFiles':len(staged),'foreignChangesPreserved':True}))
