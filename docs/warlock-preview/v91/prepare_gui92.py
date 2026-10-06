"""Verify/hold GUI91 native journal scope, then own fresh Elm transport slice."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-preview-provider-v91'
target=repo/'implementation/warlock-preview-provider-v92'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports={}
for key,pattern in [('buildReport','qa/build-*/report.json'),
                    ('retirementChannelReport','qa/actor-retirement-channel-check-v2-*/report.json'),
                    ('retirementJournalReport','qa/retirement-journal-check-*/report.json')]:
    found=list(root.glob(pattern));assert len(found)==1,found
    path=found[0];proof=json.loads(path.read_text());assert proof['passed'],path
    for name,value in proof['inputs'].items():
        p=pathlib.Path(name);assert sha(p if p.is_absolute() else root/p)==value,name
    for name,value in proof.get('artifacts',{}).items():assert sha(path.parent/name)==value,name
    assert not proof['nativeAcceptance'] and not proof['fullReleaseAccepted']
    assert all(row['exitCode']==0 for row in proof['commands'] if row['name']!='ancestor-zero-floor')
    reports[key]=str(path)
    if key=='buildReport':
        assert len(proof['commands'])==95
        assert sha(path.parent/'elm-host')==proof['binarySHA256']
        for section in ['compilerDependencies','linkedLibraries','tools']:
            for name,row in proof[section].items():assert sha(pathlib.Path(name))==row['sha256'],name
    elif key=='retirementChannelReport':
        assert proof['checks']==14467
        assert proof['evidence'][0]['zeroFloorActorRetired']
        assert proof['evidence'][2]['sequentialSubjects']==280
    else:
        assert proof['evidence']['checks']==1530 and proof['evidence']['sequentialCompletions']==280
assert not (root/'component-manifest.json').exists() and not target.exists()
files={}
for path in sorted(root.rglob('*')):
    rel=path.relative_to(root)
    if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
    assert not path.is_symlink(),path
    if path.is_file():files[str(rel)]={'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))}
manifest=root/'component-manifest.json'
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,**reports,'files':files,'nativeAcceptance':False,'actorTurnoverAccepted':False,'fullReleaseAccepted':False,'scope':'Current full95 compile and synthetic C/socket14467 plus standalone1530 journal checks. Original zero-floor and unconfirmed-completion close failures retained in held89/90. Actual Elm/host retention routing, captured physical retirement, continuing real windows and original GUI gates remain open.'},indent=2)+'\n')
def ignore(path,names):
    p=pathlib.Path(path)
    if p==root:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
    if p==root/'qa':return [n for n in names if (p/n).is_dir() and n!='toolchain']
    return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(root,target,ignore=ignore)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Strict typed retained retirement delivery, immutable Elm processing prefix, explicit original-binding channel activation and no legacy downgrade; actual host routing follows qualification.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS heldGUI91 full95/Csocket14467/standalone1530, close and zero-floor fixes qualified at bounded component scope. Own freshGUI92: explicit channel activation before retirement, strict wrappers and contiguous immutable Elm processing ACK with loss/replay/gap/binding/downgrade controls and selected Quint/compiled traces. Then actual host/native transport and real turnover/physical/GUI release gates.'], 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
