"""Read-only test selection/log audit; no ancestor tests executed."""
import hashlib,json,os,re,stat
from pathlib import Path

QA=Path('/home/hoskinson/window-integration-qa');HERE=Path(__file__).resolve().parent
def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def main():
    inputs={}
    def read(path):inputs[str(path)]=stamp(path);return path.read_text()
    cli=Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/@informalsystems/quint/dist/src/cliHelpers.js')
    owning=read(cli);assert "return name.endsWith('Test');" in owning
    affected=[]
    for version in (3,4,5,6):
        root=QA/f'restore-focus-transaction-design-v{version}'
        model=root/'focus_transaction_test.qnt';text=read(model)
        names=re.findall(r'\brun\s+([A-Za-z_][A-Za-z0-9_]*)\s*=',text)
        report=json.loads(read(root/'formal-before-runtime.json'))
        command=next(c for c in report['checks'] if c['command'][1]=='test')
        log=Path(command['log']);output=read(log)
        if command['sha256']!=inputs[str(log)]['sha256']:raise ValueError('retained log hash differs')
        selected=[n for n in names if n.endswith('Test')]
        assert '--match' not in ' '.join(command['command']) and not selected and not re.search(r'\bok .* passed',output)
        affected.append({'version':version,'reportedNamed':report['named'],'declaredRuns':len(names),'selectedRuns':0,'logBytes':log.stat().st_size,'command':command['command'],'model':str(model),'log':str(log),'reportedNamedAuthority':'not demonstrated by actual test command; held','invariantCommand':report['checks'][2]})
    proof=json.loads(read(QA/'thumbnail-v14-cpu-proof-v1/report.json'));models=[]
    for command in proof['checks']:
        argv=command['argv']
        if len(argv)<3 or argv[1]!='test':continue
        model=Path(argv[2]);names=re.findall(r'\brun\s+([A-Za-z_][A-Za-z0-9_]*)\s*=',read(model))
        selector=next((v.split('=',1)[1] for v in argv if v.startswith('--match=')),None)
        selected=[n for n in names if re.search(selector,n)] if selector is not None else [n for n in names if n.endswith('Test')]
        log=Path(command['log']);output=read(log)
        if stamp(log)['sha256']!=command['sha256']:raise ValueError('B14 retained log hash differs')
        successes=re.findall(r'\bok ([A-Za-z_][A-Za-z0-9_]*) passed',output)
        missing=set(selected)-set(successes)
        models.append({'model':str(model),'command':argv,'declaredRuns':len(names),'selectedNames':selected,'loggedSuccesses':successes,'missingSelected':sorted(missing),'log':str(log),'logHashExact':True})
    assert len(models)==14 and all(not m['missingSelected'] and len(m['selectedNames'])==len(m['loggedSuccesses']) for m in models)
    total=sum(len(m['loggedSuccesses'])for m in models);assert total==205
    sampled=QA/'restore-planning-design-v4'
    sample=read(sampled/'parallel_planning_test.qnt');samplelog=read(sampled/'formal-1.log')
    samplenames=re.findall(r'\brun\s+([A-Za-z_][A-Za-z0-9_]*)\s*=',sample)
    assert all(n.endswith('Test') and 'ok '+n+' passed' in samplelog for n in samplenames)
    row={'result':'pass','meaning':'bounded actual selector audit; affected nominal focus counts explicitly held',
        'defaultSelector':"name.endsWith('Test')",'owningCLI':str(cli),'affectedFocusDesigns':affected,
        'B14RetainedOriginalModels':models,'B14ActualNamedLogged':total,'B14ActualModels':len(models),
        'sampledPlanningV4ActualLogged':len(samplenames),'sources':inputs,
        'ancestorReruns':False,'sourceEdits':False,'nativeLaunch':False,
        'limitations':['Does not audit every ancestral formal packet','Default zero-match exit0 is not named-test authority','CPU, source reviews, invariant traces and native outcomes remain separate']}
    for path,s in inputs.items():assert stamp(Path(path))==s
    with os.fdopen(os.open(HERE/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':'pass','affectedFocusVersions':[3,4,5,6],'B14ActualNamedLogged':total,'B14ActualModels':len(models),'report':str(HERE/'report.json'),'sha256':stamp(HERE/'report.json')['sha256']}))
if __name__=='__main__':main()
