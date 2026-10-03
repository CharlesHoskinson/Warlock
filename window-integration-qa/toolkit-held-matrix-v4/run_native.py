#!/usr/bin/env python3
"""Root-reviewed serial held52 campaign. Import/preflight never starts native clients."""
import argparse,hashlib,importlib.util,json,os,re,signal,subprocess,sys,time,traceback
from pathlib import Path
import helper_observer,helper_setup,private_shell,qs_lifecycle,transport_check
from held_controller import HeldController
from held_route import CaseRoute,wait
from frontend_route import FrontendLifecycle,SERVICE
from input_control import PinnedInput
B=Path(__file__).resolve().parent;QA=B.parent
PROOF=QA/'recovery-audit/keyboard-monitor/production-native-proof-v4/native-fixture'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    with Path(path).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    Path(path).chmod(0o600)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def observer(mode,output,main,snapshot,digest=None):
    command=[sys.executable,str(B/'main_observer.py'),mode,'--folder',str(output),'--snapshot',str(snapshot),'--main-signature',main['HYPRLAND_INSTANCE_SIGNATURE'],'--main-runtime',main['XDG_RUNTIME_DIR'],'--main-home',main['HOME']]
    if digest:command+=['--snapshot-sha256',digest]
    result=subprocess.run(command,env=main,capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError('Read-only main observer failed: '+result.stderr)
    return json.loads(result.stdout)
def repl(text):return 'do\n'+text+'\nend'

def variant_run(variant,cases,output,main,closure,matrix):
    output.mkdir(mode=0o700);report=dict(variant=variant['name'],result='pending',cases=[],processes=[],cleanup={},normalNativeUnload=False,mainWrites=False);logs=[];config=None;host=None
    host_api=module('_held_host_'+variant['name'].replace('-','_'),QA/variant['host']/'weston_host.py')
    plugin=Path(matrix['candidate']);probe=Path(matrix['probe']);shell=None;shell_lifecycle=None;frontend=None;pointer=keyboard=None;active=None;loaded=False;probe_loaded=False
    lua=(QA/'qt-modal-private-v9/nested-qt.lua').read_text()+ '\nhl.permission({binary='+json.dumps(str(PROOF/'native-input'))+',type="keyboard",mode="allow"})\n'
    # Install reload behavior before compositor startup. The first context cannot
    # load Snap until the exact runtime helper path has been set after QS ping.
    # A later config write would itself trigger the real automatic watcher.
    lua+='\nlocal heldConfig=os.getenv("WINDOW_QA_HELPER_CONFIG")\nif heldConfig and heldConfig==os.getenv("XDG_RUNTIME_DIR").."/taskbar-home/helper-config.json" then\n'
    lua+='hl.config({plugin={hyprbars={enabled=true,bar_height=24,bar_part_of_window=true}}})\n'
    lua+='dofile('+json.dumps(str(helper_setup.OMARCHY_BIND))+')\ndofile('+json.dumps(str(helper_setup.SNAP))+')\no.bind("SUPER + mouse:273","Resize window",hl.dsp.window.resize(),{mouse=true})\nend\n'

    host=host_api.PrivateHyprSession(output/'host',main,1600,1000,lua.encode(),dri_prime='pci-0000_00_02_0',mesa_vendor=True)
    try:
      with host as session,helper_setup.retain_before_runtime_delete(lambda:config,output/'terminal-helpers',report):
        env=None
        def launch(label,command,environment,register=None):
            session.guard();stream=(output/(label+'.log')).open('x');logs.append(stream);read_fd=write_fd=None
            try:
                actual=command
                if register is not None:
                    read_fd,write_fd=os.pipe2(os.O_CLOEXEC);actual=['/usr/bin/python3',str(B/'exec_gate.py'),str(read_fd),'--',*command]
                process=subprocess.Popen(actual,env=environment,stdout=stream,stderr=stream,start_new_session=True,pass_fds=() if read_fd is None else (read_fd,))
                identity=helper_observer.process(process.pid);report['processes'].append(dict(role=label,identity=identity,argv=command,gatedArgv=actual if register else None))
                if register:
                    os.close(read_fd);read_fd=None;register(identity);session.guard();os.write(write_fd,b'1')
                return process
            except BaseException:
                if write_fd is not None:os.close(write_fd);write_fd=None
                if 'process' in locals():process.wait(timeout=5)
                raise
            finally:
                if read_fd is not None:os.close(read_fd)
                if write_fd is not None:os.close(write_fd)
        def ipc(*words):
            session.guard();return subprocess.check_output([str(B/'payload/omarchy/bin/omarchy-shell'),*words],env=env,text=True,timeout=5).strip()
        def generation(number,actualReload=False):
            if not actualReload:raise RuntimeError('Actual owned configuration reload required')
            result=helper_setup.wait_and_archive(config,output/('generation-'+str(number)+'.json'),require_all=False)
            if not result['allNormal'] or not result['allExactProcessesGone']:raise RuntimeError('Exact generation helpers not normally complete')
            report.setdefault('loadGenerations',[]).append(number)
        try:
            if sha(plugin)!=matrix['candidateSHA256'] or closure[str(probe)]!=sha(probe):raise RuntimeError('Exact reviewed native pair changed')
            expected_x=variant['backend'] in ('xcb','x11')
            if len(session.data('monitors'))!=1 or json.loads(session.ctl('getoption','xwayland:enabled','-j'))['bool']!=expected_x:raise RuntimeError('Actual private output/backend mismatch')
            if session.ctl('plugin','load',str(plugin)).strip()!='ok':raise RuntimeError('Actual candidate load refused')
            loaded=True
            if session.ctl('plugin','load',str(probe)).strip()!='ok':raise RuntimeError('Actual read-only public probe load refused')
            probe_loaded=True
            session.ctl('repl','hl.config({plugin={hyprbars={enabled=true,bar_height=24,bar_part_of_window=true}}})')
            env=private_shell.prepare_home(session.env,session.evidence['compositorPID'],session.evidence['compositorStart']);env['WINDOW_MOTION_NATIVE_CONFIG']=str(Path(env['HOME'])/'held-native-frontend.json')
            config=helper_setup.prepare(env,session);qs=['/usr/bin/qs','-p',str(B/'payload/omarchy/shell')]
            frontend=FrontendLifecycle(session,env,output,config,None,qs,launch,ipc,closure);report['frontendInstall']=frontend.install()
            def register(identity):helper_setup.register_query_roots(env,config,identity,qs,helper_observer.process(os.getpid()),helper_observer.cmdline(os.getpid()))
            shell=launch('taskbar-shell',qs,env,register=register);frontend.shell=shell
            shell_record=next(row for row in report['processes'] if row['role']=='taskbar-shell')
            shell_lifecycle=qs_lifecycle.Lifecycle(shell,shell_record['identity'],qs,env,session.guard,B/'payload/omarchy/shell/shell.qml',gate_command=shell_record['gatedArgv'])
            report['exactQSReadiness']=shell_lifecycle.await_ready()
            report['pairedInitialLua']=helper_setup.install_lua(env,config,session,repl)
            initial=helper_setup.wait_and_archive(config,output/'generation-1.json',require_all=False)
            if not initial['allNormal'] or not initial['allExactProcessesGone']:raise RuntimeError('Initial actual helper load failed')
            # The startup-installed reload source stays immutable. Record its
            # actual descriptor/path witness without triggering auto reload.
            path=Path(session.evidence['compositorConfig']);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            try:
                before=os.fstat(fd);base=os.read(fd,1048576);after=os.fstat(fd);named=path.lstat()
                witness=lambda row:(row.st_dev,row.st_ino,row.st_size,row.st_mtime_ns,row.st_ctime_ns)
                if len(base)!=before.st_size or witness(before)!=witness(after) or witness(before)!=witness(named):raise RuntimeError('Owned compositor configuration witness changed')
            finally:os.close(fd)
            report['reloadConfigurationWitness']=dict(path=str(path),device=after.st_dev,inode=after.st_ino,sha256=sha(path),fullSourcesUnchanged=True,installedBeforeStartup=True,postStartupConfigWrites=False)
            # Install the real resize binding in the existing initial Lua context.
            session.ctl('repl','o.bind("SUPER + mouse:273","Resize window",hl.dsp.window.resize(),{mouse=true})')
            input_env=dict(env,HYPR_A11Y_BRIDGE_PRIVATE='1',POINTER_QA_COMPOSITOR_PID=str(session.evidence['compositorPID']),POINTER_QA_COMPOSITOR_START=str(session.evidence['compositorStart']));input_env.pop('DISPLAY',None);input_env.pop('XAUTHORITY',None)
            def input_guard():
                session.guard()
                if helper_observer.read_config(Path(env['WINDOW_QA_HELPER_CONFIG']))!=config:raise RuntimeError('Exact input private configuration changed')
                proof=helper_observer.ipc_proof(config)
                session.guard()
                if proof['completeServerEOF'] is not True:raise RuntimeError('Actual input native IPC full EOF required')
            def producer(kind,binary):
                stream=(output/(kind+'-producer.log')).open('x');logs.append(stream);command=[str(binary)];process=subprocess.Popen(command,env=input_env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stream,text=True,start_new_session=True)
                report['processes'].append(dict(role=kind,identity=helper_observer.process(process.pid),argv=command));return PinnedInput(process,command,input_env,input_guard,kind)
            pointer=producer('pointer',PROOF/'native-pointer');keyboard=producer('keyboard',PROOF/'native-input')
            for index,case in enumerate(cases):
                active=CaseRoute(session,env,output/('case-'+str(index+1)),variant,config,pointer,keyboard,plugin,matrix['candidateSHA256'],host_api,closure,frontend,generation)
                report['cases'].append(active.report)
                try:active.prepare(case,index+1);HeldController(active).run(case);active.report['result']='pass'
                except BaseException:active.report['result']='fail';active.report['error']=traceback.format_exc();raise
                finally:
                    if active.process is not None:report['processes'].append(dict(role='fixture-'+str(index+1),identity=active.process_identity,argv=active.command))
                    # Real releases precede normal public quit even on failure.
                    for code in sorted(pointer.down):pointer.button(code,False)
                    for code in sorted(keyboard.down):keyboard.key(code,False)
                    try:active.close()
                    except BaseException:active.report['result']='fail';active.report['cleanup']['error']=traceback.format_exc();raise
                    finally:
                        if active.folder.is_dir():save(active.folder/'report.json',active.report)
                active=None
            report['result']='pass'
        finally:
            # Every cleanup action rechecks the exact captured native identity.
            for kind,producer in (('pointer',pointer),('keyboard',keyboard)):
                if producer:
                    try:report['cleanup'][kind]=producer.close()
                    except BaseException:report['cleanup'][kind]={'error':traceback.format_exc()};report['result']='fail'
            if frontend and frontend.service:
                process=frontend.service
                try:
                    session.guard();subprocess.run(['/usr/bin/python3',str(SERVICE/'native_runtime.py'),'--root',str(frontend.service_root),'--session',env['HYPRLAND_INSTANCE_SIGNATURE'],'--stop'],env=env,capture_output=True,text=True,timeout=8,check=True);process.wait(timeout=8)
                    if process.returncode!=0:raise RuntimeError('Exact service normal stop failed')
                    report['cleanup']['service']=dict(exitCode=0,exactOriginalGone=not helper_observer.still_live(next(row['identity'] for row in report['processes'] if row['role']=='held-service')))
                except BaseException:report['cleanup']['service']={'error':traceback.format_exc()};report['result']='fail'
                if report['cleanup'].get('service',{}).get('exitCode')==0:
                    try:
                        evidence=json.loads((output/'service-evidence.json').read_text())
                        if evidence['serviceClosed'] is not True or evidence['failure'] or evidence['serviceFailure'] or evidence['productActorCountAfterStop'] or evidence['productRetiringActorCountAfterStop'] or evidence['productResourceErrors']:raise RuntimeError('Actual normal service resource acceptance failed')
                        if any(row['exitCode']!=0 or not row['closed'] or row['failed'] or row['closeError'] for row in evidence['transports']):raise RuntimeError('Actual renderer resource acceptance failed')
                        report['serviceEvidenceAcceptance']=dict(serviceClosed=True,transportCount=len(evidence['transports']),allNormal=True)
                        if frontend.setup is not None:save(output/'frontend-events.json',dict(config=frontend.setup,events=[json.loads(row) for row in Path(frontend.setup['log']).read_text().splitlines()]))
                    except BaseException:report['serviceAcceptanceError']=traceback.format_exc();report['result']='fail'
            if shell:
                try:
                    if shell_lifecycle is None:raise RuntimeError('Exact owned QS lifecycle not established')
                    report['cleanup']['shell']=shell_lifecycle.close()
                except BaseException:report['cleanup']['shell']={'error':traceback.format_exc()};report['result']='fail'
            if shell_lifecycle is not None:
                save(output/'qs-lifecycle.json',dict(identity=shell_lifecycle.identity,ready=shell_lifecycle.ready,killSent=shell_lifecycle.kill_sent,records=shell_lifecycle.records))
            # Failed normal shutdown still must dispose only captured private groups.
            # Forced disposal is retained as failure, never normal acceptance.
            for row in report['processes']:
                identity=row['identity']
                if helper_observer.still_live(identity):
                    failure=dict(identity=identity,normalLifecycle=False,forcedTermination=True)
                    try:
                        if identity['pgid']!=identity['pid'] or Path('/proc/'+str(identity['pid'])+'/cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise RuntimeError('Exact isolated private process group/scope required for cleanup')
                        os.killpg(identity['pgid'],signal.SIGTERM)
                        end=time.monotonic()+3
                        while helper_observer.still_live(identity) and time.monotonic()<end:time.sleep(.03)
                        if helper_observer.still_live(identity):os.killpg(identity['pgid'],signal.SIGKILL);failure['forcedKill']=True
                    except BaseException:failure['error']=traceback.format_exc()
                    report['cleanup']['forced-'+row['role']]=failure;report['result']='fail'
            if session.data('clients'):raise RuntimeError('Actual owned clients must be gone before native unload')
            helper_gate_error=None
            if config:
                try:
                    report['completedHelpers']=helper_setup.wait_and_archive(config,output/'completed-helpers.json',expect_harness=True,expect_service=True)
                    if not report['completedHelpers']['allNormal'] or not report['completedHelpers']['allExactProcessesGone'] or not report['completedHelpers']['allQueriesNormal'] or not any(row['queryRoot']=='qs' for row in report['completedHelpers']['queryEvents']):raise RuntimeError('Exact helper normal retirement failed')
                except BaseException:
                    helper_gate_error=traceback.format_exc();report['helperAcceptanceError']=helper_gate_error;report['result']='fail'
            # Feature/helper acceptance cannot jump over teardown. Native unload
            # is permitted only after actual normal input/client shutdown and
            # every recorded helper identity has gone, including refusal paths.
            terminal_events=[]
            if config is not None:
                with helper_observer.locked_log(config['log']) as stream:terminal_events=helper_observer.rows(stream)
            exact_helpers=[event[key] for event in terminal_events for key in ('wrapper','delegate') if event.get(key)]
            deadline=time.monotonic()+6
            while any(helper_observer.still_live(row) for row in exact_helpers) and time.monotonic()<deadline:time.sleep(.03)
            all_helpers_gone=all(not helper_observer.still_live(row) for row in exact_helpers)
            inputs_normal=all(report['cleanup'].get(kind,{}).get('normalEOF') is True and report['cleanup'][kind].get('knownDownTransitionsReleased') is True for kind,producer in (('pointer',pointer),('keyboard',keyboard)) if producer is not None)
            fixtures_normal=all(row['cleanup'].get('normalPublicQuit') is True and row['cleanup'].get('fixtureExitCode')==0 for row in report['cases'] if row.get('processIdentity'))
            roots_normal=all(report['cleanup'].get(role,{}).get('exitCode')==0 and report['cleanup'][role].get('exactOriginalGone') is True for role in ('shell','service') if (role=='shell' and shell) or (role=='service' and frontend and frontend.service))
            report['nativeUnloadOrdering']=dict(genuineInputsReleasedNormally=inputs_normal,normalToolkitLifetimesGone=fixtures_normal,normalShellServiceLifetimesGone=roots_normal,allExactHelperProcessesGone=all_helpers_gone,clientListEmpty=True,helperIdentities=exact_helpers)
            if loaded:
                if not(inputs_normal and fixtures_normal and roots_normal and all_helpers_gone):raise RuntimeError('Normal owned lifetimes/releases/helper disposal required before native unload')
                if sha(plugin)!=matrix['candidateSHA256']:raise RuntimeError('Exact native artifact changed before unload')
                report['actualNativeUnloadReply']=session.ctl('plugin','unload',str(plugin))
                if report['actualNativeUnloadReply'].strip()!='ok' or any(row['name']=='hyprbars' for row in session.data('plugin','list')):raise RuntimeError('Normal candidate unload refused')
                loaded=False;report['normalNativeUnload']=True
            if probe_loaded:
                report['actualProbeUnloadReply']=session.ctl('plugin','unload',str(probe))
                if report['actualProbeUnloadReply'].strip()!='ok':raise RuntimeError('Normal probe unload refused')
                probe_loaded=False
            if session.data('plugin','list'):raise RuntimeError('Native private plugin list must be empty')
            if any('error' in row or row.get('forcedTermination') for row in report['cleanup'].values()):raise RuntimeError('Normal lifecycle gate failed')
            transport_check.verify_authority(closure)
            health=transport_check.transport_log_gate([Path(session.evidence['hyprland']['log']).read_text(),(output/'host/weston-renderer.log').read_text()])
            report['mandatoryParentTransport']=health
            if not health['passed']:raise RuntimeError('Actual mandatory parent transport failed')
            bus=Path(session.evidence['privateBus']['log']).read_text();activations=re.findall(r"Activating service name='([^']+)'",bus)
            report['privateBusActivations']=activations
            if activations:raise RuntimeError('Unexpected private bus service activation')
    except BaseException:report['result']='fail';report['error']=traceback.format_exc()
    finally:
        for process in ([shell] if shell else [])+([frontend.service] if frontend and frontend.service else [])+([pointer.process] if pointer else [])+([keyboard.process] if keyboard else [])+([active.process] if active and active.process else []):
            try:
                if process.poll() is not None:process.wait(timeout=1)
            except BaseException:report['result']='fail'
        if active and active.log and not active.log.closed:active.log.close()
        for stream in logs:stream.close()
        report['hostEvidence']=host.evidence
        if host.evidence.get('cleanupErrors') or host.evidence.get('remainingDescendants') or host.evidence.get('unexpectedInnerDescendants') or not host.evidence.get('runtimeGone'):report['result']='fail'
        report['allRecordedOriginalProcessesGone']=all(not helper_observer.still_live(row['identity']) for row in report['processes'])
        if not report['allRecordedOriginalProcessesGone']:report['result']='fail'
        save(output/'report.json',report)
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--attempt',type=Path);args=parser.parse_args()
    from freeze_packet import verify
    frozen=verify()
    if args.preflight:print(json.dumps(dict(result='pass',inputs=len(frozen['inputs']),links=len(frozen['symlinks']),nativeLaunch=False)));return 0
    if not args.attempt:parser.error('Explicit fresh --attempt required')
    sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
    require_qa_scope();main_env=dict(os.environ);os.umask(0o077);output=args.attempt.resolve()
    if output.parent!=B or not output.name.startswith('attempt-'):raise ValueError('Fresh owned attempt path required')
    output.mkdir(mode=0o700);matrix=json.loads((B/'matrix.json').read_text());report=dict(result='pending',variants=[],mainWrites=False,mainRestorationWrites=False,fullWindowsParityAccepted=False,physicalCadenceAccepted=False,sourceManifestSHA256=sha(B/'frozen-inputs.json'));before=None;snapshot=output/'main-before.json'
    try:
        before=observer('capture',output/'before-main',main_env,snapshot)
        for variant in matrix['variants']:
            row=variant_run(variant,matrix['casesPerVariant'],output/variant['name'],main_env,frozen['inputs'],matrix);report['variants'].append(row)
            if row['result']!='pass':raise RuntimeError('Actual held variant failed: '+variant['name'])
        if sum(len(row['cases']) for row in report['variants'])!=52:raise RuntimeError('All52 actual held lifetimes required')
        report['result']='pass'
    except BaseException:report['result']='fail';report['error']=traceback.format_exc()
    finally:
        if before:
            try:
                comparison=observer('compare',output/'after-main',main_env,snapshot,before['snapshotSHA256']);report['mainPreservation']=comparison['checks']
                if not all(comparison['checks'].values()):report['result']='fail'
            except BaseException:report['mainObserverError']=traceback.format_exc();report['result']='fail'
        report.setdefault('mainPreservation',{})['OriginalEnvironmentUnchanged']=dict(os.environ)==main_env
        try:verify();report['mainPreservation']['AllFrozenInputsExact']=True
        except BaseException:report['mainPreservation']['AllFrozenInputsExact']=False;report['result']='fail'
        report['mainPreservation']['SourceManifestUnchanged']=sha(B/'frozen-inputs.json')==report['sourceManifestSHA256']
        if not all(report['mainPreservation'].values()):report['result']='fail'
        save(output/'report.json',report)
    print(json.dumps(dict(result=report['result'],report=str(output/'report.json'))));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
