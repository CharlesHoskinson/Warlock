import hashlib,json,os,resource,stat,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected QA required'
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'fullReleaseAccepted':False}
try:
    candidate=REPO/'implementation/elm-focus-visible-surfaces-gui-v327'
    before=REPO/'implementation/elm-responsive-confirmation-gui-v301'
    changes=[]
    for section in ('src','native','adapter','assets'):
        original={str(p.relative_to(before)):p for p in (before/section).rglob('*') if p.is_file()}
        current={str(p.relative_to(candidate)):p for p in (candidate/section).rglob('*') if p.is_file()}
        assert original.keys()==current.keys(),section
        changes.extend(name for name,p in original.items() if sha(p)!=sha(current[name]))
    assert sorted(changes)==['assets/bar-adapter.js','assets/context.js'],changes
    assert (candidate/'assets/context.js').read_bytes()==(REPO/'implementation/elm-recovery-focus-scope-gui-v324/assets/context.js').read_bytes()
    build=candidate/'qa/build-1791153542665422423/report.json';compiled=json.loads(build.read_text())
    assert compiled['passed'] and len(compiled['commands'])==19 and all(c['exitCode']==0 for c in compiled['commands'])
    native_root=REPO/'implementation/elm-focus-visible-surfaces-native-v330'
    native_reports=sorted((native_root/'qa').glob('native-*/report.json'));assert len(native_reports)==2
    runs=[json.loads(p.read_text()) for p in native_reports]
    assert {r['scale'] for r in runs}=={1,2}
    native_checks=0;references={str(build.relative_to(REPO)):sha(build)}
    for path,r in zip(native_reports,runs):
        assert r['passed'] and len(r['checks'])==52 and all(c['passed'] for c in r['checks'])
        assert not r['fullReleaseAccepted'] and 'Crafted presentation' in r['scope']
        assert r['cleanup']['runtimeGone'] and not r['finalCleanupErrors']
        assert not any(r['cleanup'].get(k) for k in ('cleanupErrors','remainingDescendants','unexpectedInnerDescendants'))
        for p,d in r['inputs'].items():assert sha(p)==d,p
        for name,d in r['artifacts'].items():assert sha(path.parent/name)==d,name
        references[str(path.relative_to(REPO))]=sha(path);native_checks+=len(r['checks'])
    cpu=REPO/'implementation/elm-recovery-focus-scope-context-qa-v325/qa/checks-1791153217331327293/report.json'
    controls=json.loads(cpu.read_text());assert controls['passed'] and len(controls['current']['checks'])==20 and all(c['passed'] for c in controls['current']['checks'])
    assert controls['counterexamples'] and all(c['passed'] for c in controls['before']['checks'] if c['name'].startswith('normal'))
    for p,d in controls['inputs'].items():assert sha(p)==d,p
    references[str(cpu.relative_to(REPO))]=sha(cpu)
    ancestor=REPO/'implementation/elm-recovery-context-feedback-v592/component-manifest.json'
    assert sha(ancestor)=='c30e3a6c9a86860bd882897c644b8d14a21e0459eae67d4e578440b01a8f48d8'
    references[str(ancestor.relative_to(REPO))]=sha(ancestor)
    inventory=[]
    roots=json.loads((ROOT/'owned-roots.json').read_text())
    for name in roots:
        base=REPO/name;assert base.is_dir(),name
        for p in sorted(base.rglob('*')):
            if p==ROOT/'acceptance-manifest.json' or p==out/'report.json':continue
            st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
            if p.is_symlink():row['symlink']=os.readlink(p)
            elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
            elif p.is_dir():continue
            else:raise RuntimeError('Unarchivable owned special file: '+str(p))
            inventory.append(row)
    m={'passed':True,'nativePresentationAccepted':True,'nativeUnknownReconciliationAccepted':False,'fullReleaseAccepted':False,'nativeChecks':native_checks,'nativeGroups':2,'logicalWidths':[400,800],'cpuContextControls':20,'compileCommands':19,'changesFrom301':changes,'references':references,'ownedRoots':roots,'files':inventory,'scope':'Synthetic typed presentation fixture through actual production327 native renderer/admission/input/pixels only; current global effect/recovery/nativeUnknown/fullGUI and release acceptance excluded','ancestry':'301 inherits frozen592 policy and278 responsive CSS; previous278 1406checks and301 public35 remain separately scoped ancestry','openGates':['coherent primary integration/native Unknown reconciliation','original GUI/window effects on current release tuple','fullGTK/Qt compatibility','capture/restore/motion','physical outputs/GPU/cadence','AT/IME','measured budgets/soak','representative user acceptance','packaging/reversible deployment/rollback']}
    (ROOT/'acceptance-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    report.update(passed=True,nativePresentationAccepted=True,nativeChecks=native_checks,files=len(inventory),manifestSHA256=sha(ROOT/'acceptance-manifest.json'))
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),**report}));raise SystemExit(not report['passed'])
