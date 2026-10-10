"""Protected three-TU floating MAX/input-region policy; preserve the exact owning core archive."""
import hashlib, importlib.util, json, pathlib, resource, shlex, shutil, subprocess, sys, time
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope = require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OWNER = REPO / 'implementation/maximized-stack-v1/native-core-v2'
pointer=json.loads((ROOT/'qa/current-max-core.json').read_text())
PRIOR=(REPO/pointer['report']).parent
HELPER = REPO/'implementation/warlock-core-family-crop-v16/qa/archive.py'
spec = importlib.util.spec_from_file_location('owning_archive', HELPER)
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)
OUT = ROOT / 'qa/runs' / ('scene-core-' + str(time.time_ns()))
OUT.mkdir()
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r = dict(passed=False, nativeAcceptance=False, installed=False, protectedScope=scope, commands=[],
         scope='Three owning committed MAX scene TUs and exact relink; native eligibility/input remains separately verified')

def run(name, argv):
    p = subprocess.run(list(map(str, argv)), cwd=OWNER/'build', capture_output=True, timeout=240)
    (OUT/(name+'.stdout')).write_bytes(p.stdout)
    (OUT/(name+'.stderr')).write_bytes(p.stderr)
    r['commands'].append(dict(name=name, command=list(map(str, argv)), exitCode=p.returncode))
    print(name, p.returncode, flush=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p.stdout

def dependencies(path):
    names = shlex.split(path.read_text().replace('\\\n', ' ').split(':', 1)[1])
    names = names[:next((i for i, name in enumerate(names) if name.endswith(':')), len(names))]
    return {str((pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n).resolve()):
            sha(pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n) for n in names}

try:
    assert sha(PRIOR/'report.json')==pointer['reportSHA256']
    prior = json.loads((PRIOR/'report.json').read_text())
    assert prior['passed'] and sha(PRIOR/'Hyprland') == prior['binarySHA256']
    assert sha(PRIOR/'libhyprland_lib.a') == prior['archiveSHA256']
    originals = archive.archive_payloads(PRIOR/'libhyprland_lib.a')
    assert len(originals) == 433
    renderer_path=REPO/'implementation/warlock-core-family-crop-v16/build-1791282659756472310/report.json'
    renderer=json.loads(renderer_path.read_text());assert renderer['passed']
    tree = OUT/'owning-headers'
    for rel, digest in prior['owningHeaders'].items():
        p=PRIOR/'owning-headers'/rel;assert sha(p)==digest
        q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    for name,digest in renderer['dependencies'].items():
        original=pathlib.Path(name)
        if name.startswith(str(renderer_path.parent/'owning-headers')+'/') and original.suffix=='.inc':
            assert sha(original)==digest
            rel=original.relative_to(renderer_path.parent/'owning-headers');q=tree/rel
            q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,q)
    header=ROOT/'native/core/CommittedScene.hpp';shutil.copyfile(header,tree/'CommittedScene.hpp')
    modal_header=ROOT/'native/core/ModalRecipient.hpp';shutil.copyfile(modal_header,tree/'ModalRecipient.hpp')
    input_path=REPO/'implementation/elm-core-seat-focus-restoration-v450/build-1791131758410759196/report.json'
    input_record=json.loads(input_path.read_text());assert input_record['passed']
    specs=[('src/render/Renderer.cpp',renderer_path,renderer),('src/desktop/state/ViewHitTester.cpp',PRIOR/'report.json',prior),
           ('src/managers/input/InputManager.cpp',input_path,input_record)]
    entries=json.loads((OWNER/'build/compile_commands.json').read_text())
    source_hashes={'native/core/CommittedScene.hpp':sha(header),'native/core/ModalRecipient.hpp':sha(modal_header)};baseline_sources={};deps={};replacements={}
    target=OUT/'libhyprland_lib.a';shutil.copyfile(PRIOR/'libhyprland_lib.a',target)
    for rel,baseline_report,baseline in specs:
        name=pathlib.Path(rel).name;member=name+'.o'
        rows=[row for row in originals if row['name']==member];assert len(rows)==1
        if baseline is not prior: assert rows[0]['sha256']==baseline['rebuiltArchiveMembers'][member]
        else: assert sha(baseline_report)==pointer['reportSHA256']
        baseline_source=(pathlib.Path(next(k for k in baseline['dependencies'] if k.endswith('/InputManager.cpp'))) if baseline is input_record else baseline_report.parent/'owning-headers'/rel)
        baseline_hash=sha(baseline_source)
        baseline_deps=baseline['dependencies']
        assert baseline_deps[str(baseline_source)]==baseline_hash
        baseline_sources[rel]={'path':str(baseline_source),'sha256':baseline_hash,
            'report':str(baseline_report),'reportSHA256':sha(baseline_report),'objectSHA256':rows[0]['sha256']}
        source=ROOT/'native/core'/name;source_hashes['native/core/'+name]=sha(source)
        compiled=tree/rel;shutil.copyfile(source,compiled)
        original=OWNER/rel
        entry=next(e for e in entries if e['file']==str(original))
        args=shlex.split(entry['command']);command=[];i=0
        while i<len(args):
            a=args[i]
            if a in ('-o','-include'):i+=2;continue
            if a=='-c' or a==str(original):i+=1;continue
            if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:
                a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
            command.append(a);i+=1
        for policy,digest in renderer['retainedPolicyHeaders'].items():assert sha(policy)==digest
        command.append('-I'+str(renderer_path.parent/'inputs/candidate'))
        obj=OUT/member;dep=OUT/(name+'.d')
        run('compile-'+name,command+['-MD','-MF',str(dep),'-o',str(obj),'-c',str(compiled)])
        current=dependencies(dep);assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/src/') for p in current)
        deps.update(current)
        intermediate=OUT/('archive-'+name+'.a')
        archive.replace_payload(target,intermediate,rows[0]['sha256'],obj)
        shutil.move(intermediate,target);replacements[member]=sha(obj)
    run('archive-index',['ar','s',target])
    new=archive.archive_payloads(target);assert len(new)==len(originals)
    for a,b in zip(originals,new):
        assert a['name']==b['name']
        assert b['sha256']==replacements[a['name']] if a['name'] in replacements else a==b
    link = next(c['command'] for c in prior['commands'] if c['name'] == 'link').copy()
    for i, a in enumerate(link):
        if i and link[i-1] == '-o': link[i] = str(OUT/'Hyprland')
        elif a == str(PRIOR/'libhyprland_lib.a'): link[i] = str(target)
        elif a.startswith('-Wl,--dependency-file='): link[i] = '-Wl,--dependency-file='+str(OUT/'link.d')
    run('link', link)
    actual = dependencies(OUT/'link.d')
    expected = {str(target) if p == str(PRIOR/'libhyprland_lib.a') else p:
                sha(target) if p == str(PRIOR/'libhyprland_lib.a') else digest
                for p, digest in prior['linkDependencies'].items()}
    assert actual == expected
    exports = []
    for name, binary in [('ancestor', PRIOR/'Hyprland'), ('candidate', OUT/'Hyprland')]:
        exports.append({tuple(line.split()[1:]) for line in run(name+'-exports', ['nm', '-D', '--defined-only', binary]).decode().splitlines()})
    old_strong={x for x in exports[0] if x[0] not in ('W','V','u')}
    assert old_strong <= exports[1], 'Existing strong exports changed'
    additions=exports[1]-exports[0]
    assert all(x[0] in ('W','V','u') or 'CommittedScene' in x[-1] for x in additions), 'Unrelated added API'
    assert any('CommittedScene' in x[-1] for x in additions)
    assert all(sha(ROOT/p)==digest for p,digest in source_hashes.items())
    for rel, digest in prior['owningHeaders'].items(): assert sha(tree/rel) == digest
    for p, digest in deps.items(): assert sha(p) == digest
    r.update(passed=True, binary=str(OUT/'Hyprland'), binarySHA256=sha(OUT/'Hyprland'),
             archiveSHA256=sha(target), sourceHashes=source_hashes, baselineSources=baseline_sources, addedExports=sorted(additions), existingStrongExportsPreserved=True,
             owningHeaders=prior['owningHeaders'], existingPublicHeadersUnchanged=True,
             existingObjectLayoutsUnchanged=True, unchangedArchiveMembers=430,
             ancestor=dict(report=str(PRIOR/'report.json'), reportSHA256=sha(PRIOR/'report.json')),
             archiveHelperSHA256=sha(HELPER), dependencies=deps, linkDependencies=actual,
             aqLibrary=prior['aqLibrary'], aqLibrarySHA256=prior['aqLibrarySHA256'])
except Exception as error:
    import traceback
    r.update(error=repr(error), traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(dict(passed=r['passed'], report=str(OUT/'report.json'), error=r.get('error'))))
raise SystemExit(not r['passed'])
