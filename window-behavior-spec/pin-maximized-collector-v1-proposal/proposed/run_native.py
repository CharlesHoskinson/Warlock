#!/usr/bin/python3
"""Root-only native Pin campaign A. Preflight/import never starts a desktop."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,stat,subprocess,sys,traceback
sys.path.append(str(Path(__file__).resolve().parent.parent))
from native_cases import NativeCases,PRODUCT,QA
import private_output_host,output_readiness,pair_binding
B=Path(__file__).resolve().parent.parent
HOST=B/'proposed'
AQ=QA/'aquamarine-nested-bootstrap-v2/prefix/lib/libaquamarine.so.0.15.0'
PLUGIN=pair_binding.PLUGIN
PROBE=B/'readonly-probe/libqt-modal-probe.so'
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def verify(path=None):
 p=path or B/'frozen-inputs.json';raw=p.read_bytes();packet=json.loads(raw)
 for name,digest in packet['inputs'].items():
  f=Path(name)
  if f.is_symlink() or not f.is_file() or sha(f)!=digest or stat.S_IMODE(f.stat().st_mode)!=packet['inputModes'][name]:raise RuntimeError('Exact source bytes/mode changed: '+name)
 for name,target in packet['symlinks'].items():
  if not Path(name).is_symlink() or os.readlink(name)!=target:raise RuntimeError('Exact source link changed: '+name)
 for name,mode in packet.get('directoryModes',{}).items():
  d=Path(name)
  if type(mode)is not int or d.is_symlink()or not d.is_dir()or stat.S_IMODE(d.stat().st_mode)!=mode:raise RuntimeError('Exact declared directory mode changed: '+name)
 return packet
def observer(mode,output,main,snapshot,digest=None):
 command=['/usr/bin/python3',str(QA/'browser-files-flow-v20/main_observer.py'),mode,'--folder',str(output),'--snapshot',str(snapshot),'--main-signature',main['HYPRLAND_INSTANCE_SIGNATURE'],'--main-runtime',main['XDG_RUNTIME_DIR'],'--main-home',main['HOME']]
 if digest:command+=['--snapshot-sha256',digest]
 r=subprocess.run(command,env=main,capture_output=True,text=True,timeout=30)
 if r.returncode:raise RuntimeError('Read-only original main observer refused: '+r.stderr)
 return json.loads(r.stdout)
def persist(p,row):p.write_text(json.dumps(row,indent=2,allow_nan=False)+'\n');p.chmod(0o600)
def transport(logs):
 text='\n'.join(logs);forbidden=r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
 return bool('Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend'in text and re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text) and not re.search(forbidden,text,re.I))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--preflight',action='store_true');ap.add_argument('--source-check',action='store_true');ap.add_argument('--attempt',type=Path);a=ap.parse_args()
 packet=verify(B/'source-ready-inputs-final-v1.json' if a.source_check else None)
 if a.preflight or a.source_check:
  print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),links=len(packet['symlinks']),nativeLaunch=False,sourceOnly=a.source_check)));return 0
 if not a.attempt:ap.error('Explicit fresh root-reviewed --attempt required')
 pair=pair_binding.read_pair(B/'PAIR_READY.json')
 scope=require_qa_scope();main_env=dict(os.environ);os.umask(0o077);output=a.attempt.resolve()
 if output.parent!=B or not re.fullmatch(r'attempt-[1-9][0-9]*',output.name):raise ValueError('Fresh exact owned attempt required')
 output.mkdir(mode=0o700);frozen=(B/'frozen-inputs.json').read_bytes();snapshot=output/'main-before.json'
 report=dict(result='pending',scope=scope,hostChecks=[],mainPreservation={},mainGUIWrites=False,mainRestorationWrites=False,
             bindingChecks=[],nativePinAccepted=False,taskbarFrontendAccepted=False,maxPinAccepted=False,fullWindowsParityAccepted=False,
             campaign='A legacy/native titlebar/physical keyboard/stacking/modal/lifetime/reload',sourceManifestSHA256=sha(B/'frozen-inputs.json'))
 before=None;host=None;cases=None
 def gate(name,value,**details):
  report['hostChecks'].append(dict(name=name,passed=value is True,**details));persist(output/'report.json',report)
  if value is not True:raise AssertionError(name)
 try:
  before=observer('capture',output/'before-main',main_env,snapshot)
  api=private_output_host.adapt(module('_pin_exact_private_host',HOST/'candidate_host.py'))
  lua=(QA/'browser-files-flow-v20/nested-qt.lua').read_bytes()+(B/'private-controls.lua').read_bytes()
  # Private authorization for this exact frozen keyboard producer only. No main permission edit.
  lua+=('\nhl.permission({binary='+json.dumps(str(PRODUCT/'keyboard-chords/physical-keyboard'))+',type="keyboard",mode="allow"})\n').encode()
  host=api.PrivateHyprSession(output/'host',main_env,1600,1000,lua,dri_prime='pci-0000_00_02_0',mesa_vendor=True)
  def binding_gate(session,phase,loaded=()):
   verify();current_pair=pair_binding.read_pair(B/'PAIR_READY.json')
   raw=pair_binding.attest(session,current_pair,phase,loaded)
   report['bindingChecks'].append(raw);persist(output/'report.json',report)
   if raw['passed'] is not True:raise AssertionError('Exact completed core/plugin/probe binding: '+phase)
  with host as session:
   binding_gate(session,'before-legacy-clients')
   loaded=probe_loaded=False;cases=NativeCases(session,output/'native')
   try:
    gate('Actual private mandatory parent DMA-BUF probe',bool(session.evidence.get('actualDmabuf')),actual=session.evidence.get('actualDmabuf'))
    report['outputReadiness']=output_readiness.collect(session,output/'host/output-readiness-evidence.json')
    monitors=session.data('monitors')
    gate('Unchanged exact1600x1000 scale1 private output',output_readiness.exact_outputs(monitors),actual=monitors)
    gate('Private Xwayland disabled',json.loads(session.ctl('getoption','xwayland:enabled','-j')).get('bool') is False)
    gate('No existing clients/plugins/errors before legacy fixture',session.data('clients')==[] and session.data('plugin','list')==[] and not session.ctl('configerrors').strip())
    maps=api.original.mapped_files(session.evidence['compositorPID'])
    gate('Exact reviewed bootstrap AQ mapped by private compositor',maps['files'].get(str(AQ))==packet['inputs'][str(AQ)],mappedSHA256=maps['files'].get(str(AQ)))
    ready=session.evidence['ipcReadiness']
    gate('Actual owned IPC version complete EOF before clients',len(ready)==1 and ready[0]['peer']['pid']==session.evidence['compositorPID'] and ready[0]['peer']['uid']==os.getuid() and ready[0]['completeServerEOF'] is True,actual=ready)
    # Real old windows exist before any product module or Service starts.
    cases.launch_legacy()
    if sha(PLUGIN)!=packet['inputs'][str(PLUGIN)] or session.ctl('plugin','load',str(PLUGIN)).strip()!='ok':raise RuntimeError('Exact completed matching native candidate load refused')
    loaded=True
    binding_gate(session,'candidate-loaded',(str(PLUGIN),))
    maps=api.original.mapped_files(session.evidence['compositorPID'])
    gate('Exact matching candidate privately mapped after genuine legacy creation',maps['files'].get(str(PLUGIN))==packet['inputs'][str(PLUGIN)] and len(session.data('plugin','list'))==1,mappedSHA256=maps['files'].get(str(PLUGIN)))
    if session.ctl('plugin','load',str(PROBE)).strip()!='ok':raise RuntimeError('Exact frozen read-only Seat/hit diagnostic load refused')
    probe_loaded=True;maps=api.original.mapped_files(session.evidence['compositorPID'])
    gate('Exact rebuilt byte-identical B20 readonly core/Seat/hit probe mapped',maps['files'].get(str(PROBE))==packet['inputs'][str(PROBE)],mappedSHA256=maps['files'].get(str(PROBE)))
    binding_gate(session,'before-genuine-original14',(str(PLUGIN),str(PROBE)))
    cases.run()
   finally:
    try:cases.close()
    finally:
     report['cases']=cases.report;persist(output/'report.json',report)
     session.guard();clients=session.data('clients');report['clientsBeforeUnload']=clients;persist(output/'report.json',report)
     if clients:raise RuntimeError('Native unload refused until every owned client is gone')
     if probe_loaded:
      report['actualReadonlyButtons']=json.loads(session.ctl('repl','print(hl.plugin.qt_modal_probe.events())'))
      report['actualPreCoreKeys']=json.loads(session.ctl('repl','print(hl.plugin.qt_modal_probe.keyboard_events())'))
      session.ctl('plugin','unload',str(PROBE));report['probeUnloadedNormally']=all(r['name']!='qt_modal_probe'for r in session.data('plugin','list'));persist(output/'report.json',report)
      if report['probeUnloadedNormally'] is not True:raise RuntimeError('Readonly probe not normally unloaded')
     if loaded:
      session.ctl('plugin','unload',str(PLUGIN));report['candidateUnloadedNormally']=session.data('plugin','list')==[];persist(output/'report.json',report)
      if report['candidateUnloadedNormally'] is not True:raise RuntimeError('Native candidate not normally unloaded')
  report['hostEvidence']=host.evidence
  closure=host.evidence.get('ownedNormalClosure',{})
  report['normalHostClosure']=closure;persist(output/'report.json',report)
  if closure.get('normal') is not True:raise AssertionError('Actual normal owned host closure required')
  gate('Exact normal private lifecycle no unknown descendants',host.evidence.get('runtimeGone') is True and not host.evidence.get('cleanupErrors') and not host.evidence.get('unexpectedInnerDescendants') and not host.evidence.get('remainingDescendants'))
  archives=[r for r in host.evidence.get('archivedRuntime',[])if Path(r['archive']).name=='hyprland.log']
  if len(archives)!=1:raise RuntimeError('One exact archived owned compositor log required')
  gate('Original strict mandatory parent transport healthy through teardown',transport([Path(archives[0]['archive']).read_text(),(output/'host/weston-renderer.log').read_text()]))
 except BaseException:report['error']=traceback.format_exc()
 finally:
  if host:report['hostEvidence']=host.evidence
  if cases:report['cases']=cases.report
  if before:
   try:report['mainPreservation']=observer('compare',output/'after-main',main_env,snapshot,before['snapshotSHA256'])['checks']
   except BaseException:report['mainObserverError']=traceback.format_exc()
  report['mainPreservation']['originalProcessEnvironmentUnchanged']=dict(os.environ)==main_env
  report['mainPreservation']['frozenManifestBytes']=(B/'frozen-inputs.json').read_bytes()==frozen
  try:verify();report['mainPreservation']['allFrozenInputsExact']=True
  except BaseException:report['mainPreservation']['allFrozenInputsExact']=False;report['sourceError']=traceback.format_exc()
  report['nativePinAccepted']=bool(before and not report.get('error') and not report.get('mainObserverError') and cases and cases.report['result']=='pass' and cases.report.get('normalCleanup') is True and report.get('candidateUnloadedNormally') is True and report.get('probeUnloadedNormally') is True and report.get('normalHostClosure',{}).get('normal') is True and len(report['bindingChecks'])==3 and all(r['passed'] is True for r in report['bindingChecks']) and len(report['hostChecks'])==10 and all(r['passed']for r in report['hostChecks']) and all(report['mainPreservation'].values()))
  report['result']='pass'if report['nativePinAccepted']else'fail';persist(output/'report.json',report)
 print(json.dumps(dict(result=report['result'],hostChecks=len(report['hostChecks']),nativePinAccepted=report['nativePinAccepted'],taskbarFrontendAccepted=False,maxPinAccepted=False,reportSHA256=sha(output/'report.json'),error=report.get('error'))));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
