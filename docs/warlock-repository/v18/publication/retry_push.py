"""Retry the identical prepared publication after a terminal HTTP408 failure."""
import json,pathlib,subprocess,sys
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).parent
receipt=json.loads((OUT/'prepared.json').read_text());branch='refs/heads/feature/elm'
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
assert git(['ls-remote','github',branch],text=True).split()[0]==receipt['priorPublication']
assert git(['--git-dir='+str(MIRROR),'rev-parse',branch],text=True).strip()==receipt['publishedCommit']
verified={}
for row in git(['--git-dir='+str(MIRROR),'ls-tree','-rz',receipt['publishedCommit'],'--',*[x['path'] for x in receipt['inventory']]]).split(b'\0'):
    if not row:continue
    metadata,name=row.split(b'\t',1);mode,kind,oid=metadata.decode().split();assert kind=='blob';verified[name.decode()]=(mode,oid)
assert len(verified)==receipt['ownedFiles'] and all(verified[x['path']]==(x['mode'],x['gitBlob']) for x in receipt['inventory'])
command=['git','--git-dir='+str(MIRROR),'-c','http.postBuffer=268435456','-c','http.version=HTTP/1.1','push','origin',branch+':'+branch]
result=subprocess.run(command,capture_output=True,text=True,timeout=180)
(OUT/'retry-push.stdout').write_text(result.stdout);(OUT/'retry-push.stderr').write_text(result.stderr)
observed=git(['ls-remote','github',branch],text=True).split()[0]
receipt.update(gitPushExitCode=result.returncode,remoteObserved=observed,pushCompleted=observed==receipt['publishedCommit'],retryCommand=command)
(OUT/('delivery.json' if receipt['pushCompleted'] else 'retry-failure.json')).write_text(json.dumps(receipt,indent=2)+'\n')
assert receipt['pushCompleted'],'Identical prepared commit not published; retain failure and inspect remote'
print(json.dumps({'publishedCommit':receipt['publishedCommit'],'ownerFiles':receipt['ownedFiles'],'remoteVerified':True}))
