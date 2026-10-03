"""Pre-command authority for exact real Lua occurrences; inert on import."""
import copy
import json
import os
import re
import secrets
import shlex
import time
from pathlib import Path
import helper_observer as observer
import helper_setup

PROLOGUE = r'''local evaluationNonce=os.getenv("WINDOW_QA_EVALUATION_NONCE")
local evaluationKind=os.getenv("WINDOW_QA_EVALUATION_KIND")
local evaluationLimit=os.getenv("WINDOW_QA_EVALUATION_LIMIT")
local evaluationCounts={initial=1,reload=1,["native-load"]=2,["native-unload"]=1,["probe-unload"]=1}
assert(evaluationNonce and #evaluationNonce==32 and evaluationNonce:match("^[0-9a-f]+$"),"Exact private evaluation nonce required")
assert(evaluationCounts[evaluationKind] and evaluationLimit==tostring(evaluationCounts[evaluationKind]),"Exact private evaluation command required")
local previousOrdinal=os.getenv("WINDOW_QA_EVALUATION_ORDINAL")
assert(previousOrdinal and previousOrdinal:match("^%d+$"),"Exact private evaluation ordinal required")
local evaluationOrdinal=tonumber(previousOrdinal)+1
hl.env("WINDOW_QA_EVALUATION_ORDINAL",tostring(evaluationOrdinal))
assert(evaluationOrdinal<=evaluationCounts[evaluationKind],"Unexpected extra private Lua evaluation")
'''


def repl(text):return 'do\n'+text+'\nend'


def prepare(env,config,session,candidate,probe):
    path=Path(env['WINDOW_QA_HELPER_CONFIG'])
    if observer.read_config(path)!=config or config['allowed']!=['generation:1:hydrate','generation:1:inactive-fileDrag']:
        raise RuntimeError('Fresh untouched helper authority required')
    with observer.locked_log(config['log']) as stream:
        if observer.rows(stream):raise RuntimeError('Evaluation authority must precede every helper')
        config['allowed']=[];config.pop('loadGeneration')
        config['evaluationTickets']=[];config['activeEvaluation']=None
        config['evaluationInitialCommand']=['repl',repl(helper_setup.paired_lua_script(PROLOGUE))]
        config['evaluationConfiguration']=observer.material_witness(session.evidence['compositorConfig'])
        config['evaluationArtifacts']={'native':observer.material_witness(candidate),'probe':observer.material_witness(probe)}
        helper_setup.write_json(path,config)


def events(config):
    with observer.locked_log(config['log']) as stream:return observer.rows(stream)


def pending_helper_processes(config):
    """Also find an actual spawned helper not yet able to journal its start."""
    entries={helper[key] for helper in config['helpers'].values() for key in ('wrapper','actual')}
    result=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            if path.stat().st_uid!=os.getuid():continue
            row=observer.process(int(path.name));argv=observer.cmdline(row['pid'])
            direct=any(value in entries for value in argv[:2])
            shell=False
            if row['parent']==config['compositor']['pid'] and len(argv)==3 and argv[1]=='-c' and (path/'exe').resolve()==Path('/bin/sh').resolve():
                words=shlex.split(argv[2]);shell=bool(words) and words[0] in entries|{config['helpers']['shell'].get('invocation','omarchy-shell')}
            if direct or shell:
                if (path/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise RuntimeError('Exact spawned helper left selected scope')
                result.append(dict(identity=row,argv=argv,exactEntry=direct,exactCompositorShell=shell))
        except (FileNotFoundError,ProcessLookupError):continue
    return result


def terminal_closure(rows,required=None,allow_refused=False):
    starts=[row for row in rows if row['event']=='started'];ends=[row for row in rows if row['event']=='terminal']
    if any(row['event'] not in ('started','terminal','refused') for row in rows):raise RuntimeError('Unknown helper event')
    if not allow_refused and any(row['event']=='refused' for row in rows):raise RuntimeError('Refused helper forbids feature evaluation authority')
    if len({row['operation'] for row in starts})!=len(starts) or len({row['operation'] for row in ends})!=len(ends) or any(end['operation'] not in {row['operation'] for row in starts} for end in ends):raise RuntimeError('Duplicate/orphan actual helper terminal')
    if len(ends)!=len(starts):return False
    for start in starts:
        matching=[row for row in ends if row.get('operation')==start['operation']]
        if len(matching)!=1 or (matching[0]['exitCode']!=0 and (not allow_refused or required is not None and start['operation'] in required)) or any(matching[0].get(key)!=start.get(key) for key in ('wrapper','delegate','class','queryRoot','helper','serviceOperation')):
            raise RuntimeError('Exact helper terminal mismatch')
    identities=[row[key] for row in rows for key in ('wrapper','delegate') if row.get(key)]
    if any(observer.still_live(row) for row in identities):return False
    if required is not None:
        actual=[row['operation'] for row in starts if row.get('class','compositor')=='compositor' and row['operation'] in required]
        if len(actual)!=len(set(actual)):raise RuntimeError('Duplicate evaluation callback')
        if set(actual)!=set(required):return False
    return True


def ordinal(session,ticket):
    session.guard()
    names=('WINDOW_QA_EVALUATION_NONCE','WINDOW_QA_EVALUATION_KIND','WINDOW_QA_EVALUATION_LIMIT','WINDOW_QA_EVALUATION_ORDINAL')
    text='print(table.concat({' + ','.join('os.getenv('+json.dumps(name)+') or ""' for name in names) + '},"\\n"))'
    result=session.ctl('repl',repl(text)).strip().splitlines()
    if len(result)!=4 or result[:3]!=[ticket['nonce'],ticket['kind'],str(ticket['count'])] or not re.fullmatch('0|[1-9][0-9]*',result[3]):
        raise RuntimeError('Actual compositor armed evaluation environment differs')
    value=int(result[3])
    if value>ticket['count']:raise RuntimeError('Unexpected extra actual Lua evaluation')
    return value


class Evaluations:
    def __init__(self,env,config,session,output,report):
        self.env=env;self.config=config;self.session=session;self.output=Path(output);self.report=report
        self.current=None;self.completed=set()

    def arm(self,kind,command,artifact=None,terminal=False):
        config=self.config;path=Path(self.env['WINDOW_QA_HELPER_CONFIG'])
        if kind not in observer.EVALUATION_RULES or terminal and kind not in ('native-unload','probe-unload'):
            raise RuntimeError('Unknown evaluation command authority')
        self.session.guard()
        if terminal:
            ordering=self.report.get('nativeUnloadOrdering',{})
            fields=('genuineInputsReleasedNormally','normalToolkitLifetimesGone','normalShellServiceLifetimesGone','allExactHelperProcessesGone','clientListEmpty')
            if any(ordering.get(name) is not True for name in fields) or self.session.data('clients'):
                raise RuntimeError('Bound terminal authority requires actual normal owned lifetime/input closure')
        if observer.read_config(path)!=config:raise RuntimeError('Evaluation configuration changed before arm')
        if self.current is not None:
            observed=ordinal(self.session,self.current)
            if observed!=self.current['count'] or self.current['nonce'] not in self.completed:
                # Failed features may still be normally unloaded once the exact
                # prior evaluation count is known. This never accepts a feature.
                if not terminal or observed!=self.current['count']:raise RuntimeError('Prior actual evaluation boundary not complete')
        deadline=time.monotonic()+8
        while not terminal_closure(events(config),allow_refused=terminal) or pending_helper_processes(config):
            if time.monotonic()>deadline:raise RuntimeError('Prior actual helpers not normally closed before arm')
            time.sleep(.03)
        ticket=dict(serial=len(config['evaluationTickets'])+1,nonce=secrets.token_hex(16),kind=kind,
                    count=observer.EVALUATION_RULES[kind][0],relayOrdinal=observer.EVALUATION_RULES[kind][1],
                    command=list(map(str,command)),root=copy.deepcopy(config['queryRoots']['harness']),
                    compositor=copy.deepcopy(config['compositor']),instance=config['instance'],
                    configuration=observer.material_witness(config['evaluationConfiguration']['path']),
                    artifact=observer.material_witness(artifact) if artifact is not None else None,
                    armIPC=observer.ipc_proof(config),armedNs=time.time_ns(),terminalAuthority=terminal)
        if ticket['configuration']!=config['evaluationConfiguration']:raise RuntimeError('Startup configuration changed')
        allowed=observer.evaluation_keys(ticket)
        # Verify the exact live authorizing root with the same checks the real
        # callback will perform; no future PID/name authorization is accepted.
        updated=copy.deepcopy(config);updated['evaluationTickets'].append(ticket);updated['activeEvaluation']=ticket['nonce'];updated['allowed']+=allowed
        environment=dict(WINDOW_QA_EVALUATION_NONCE=ticket['nonce'],WINDOW_QA_EVALUATION_KIND=kind,WINDOW_QA_EVALUATION_LIMIT=str(ticket['count']),WINDOW_QA_EVALUATION_ORDINAL='1')
        observer.evaluation_operation(updated,environment,'hydrate')
        with observer.locked_log(config['log']) as stream:
            if observer.read_config(path)!=config or not terminal_closure(observer.rows(stream),allow_refused=terminal) or pending_helper_processes(config):raise RuntimeError('Prior helper boundary changed during arm')
            helper_setup.write_json(path,updated);config.clear();config.update(updated)
        self.current=ticket
        self.report.setdefault('evaluationTickets',[]).append(copy.deepcopy(ticket))
        script='\n'.join('hl.env('+json.dumps(key)+','+json.dumps(value)+')' for key,value in {**environment,'WINDOW_QA_EVALUATION_ORDINAL':'0'}.items())
        self.session.ctl('repl',repl(script))
        if ordinal(self.session,ticket)!=0:raise RuntimeError('Evaluation ticket not armed before command')
        return ticket

    def complete(self,ticket):
        if ticket!=self.current or observer.read_config(self.env['WINDOW_QA_HELPER_CONFIG'])!=self.config:
            raise RuntimeError('Actual evaluation ticket changed')
        deadline=time.monotonic()+8;last=[]
        try:
            while time.monotonic()<deadline:
                count=ordinal(self.session,ticket);last=events(self.config)
                if terminal_closure(last,observer.evaluation_keys(ticket),allow_refused=ticket['terminalAuthority']) and count==ticket['count'] and not pending_helper_processes(self.config):
                    if observer.material_witness(ticket['configuration']['path'])!=ticket['configuration']:raise RuntimeError('Evaluation configuration witness changed')
                    if ticket['artifact'] is not None and observer.material_witness(ticket['artifact']['path'])!=ticket['artifact']:raise RuntimeError('Evaluation artifact witness changed')
                    selectors=dict(WINDOW_QA_EVALUATION_NONCE=ticket['nonce'],WINDOW_QA_EVALUATION_KIND=ticket['kind'],WINDOW_QA_EVALUATION_LIMIT=str(ticket['count']),WINDOW_QA_EVALUATION_ORDINAL=str(count))
                    observer.evaluation_operation(self.config,selectors,'hydrate')
                    completion_ipc=observer.ipc_proof(self.config)
                    self.session.guard()
                    self.completed.add(ticket['nonce'])
                    result=dict(ticket=ticket,completionIPC=completion_ipc,actualOrdinal=count,expectedOperations=observer.evaluation_keys(ticket),events=last,allExactProcessesGone=True,unloggedExactHelperProcesses=[],allExpectedNormal=True,fullEOF=True,terminalAuthority=ticket['terminalAuthority'])
                    helper_setup.write_json(self.output/('evaluation-'+str(ticket['serial'])+'.json'),result)
                    self.report.setdefault('completedEvaluations',[]).append(ticket['serial'])
                    return result
                time.sleep(.03)
            raise RuntimeError('Bound actual evaluation/callback completion timeout')
        except BaseException:
            helper_setup.write_json(self.output/('evaluation-'+str(ticket['serial'])+'-failure.json'),dict(ticket=ticket,events=last,accepted=False))
            raise

    def command(self,kind,command,artifact=None,terminal=False):
        ticket=self.arm(kind,command,artifact,terminal)
        result=self.session.ctl(*command)
        self.complete(ticket)
        return result,ticket
