from pathlib import Path
import importlib.util,json,os,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewed_durable_driver',B/'terminal_product_once.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
def main():
 require_qa_scope();case=sys.argv[1];assert case in ['actual-public-provider-refusal','final-admission-primitive'];build=json.loads((B/'terminal-module-build-v1.json').read_text());assert build['result']=='pass'and all(driver.sha(p)==h for p,h in build['sources'].items())
 binary=B/('cpu-public-provider-retire-refusal'if case=='actual-public-provider-refusal'else'cpu-final-admission-primitive');assert driver.sha(binary)==build['outputs'][str(binary)]
 command=[str(binary)]
 if case=='actual-public-provider-refusal':
  module=build['reusedCurrentProviderModule'];assert driver.sha(module['path'])==module['sha256'];command.append(module['path'])
 directory=B/'narrow-components'/case;directory.mkdir(parents=True,mode=0o700,exist_ok=False);directory.chmod(0o700)
 row={'case':case,'command':command,'actualCurrentBinarySHA256':driver.sha(binary),'actualBuildPath':str(B/'terminal-module-build-v1.json'),'actualBuildSHA256':driver.sha(B/'terminal-module-build-v1.json'),'GUI':False,'helperLaunches':0,'retries':0,'observerDeadlineSeconds':8,'EOFWaitSeconds':5};driver.persist(directory,'attempt-before-launch.json',row)
 actor=None;before=time.monotonic()
 try:
  actor=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,text=True);out,err=actor.communicate(timeout=8);row.update(stdout=out,stderr=err,exitCode=actor.returncode,result='pass'if actor.returncode==0 else'fail',elapsedSeconds=time.monotonic()-before,normalProcessExitObserved=actor.returncode==0)
 except BaseException as error:
  row.update(result='fail',error=repr(error),elapsedSeconds=time.monotonic()-before)
  if isinstance(error,subprocess.TimeoutExpired):
   row['partialStdout']=(error.stdout or b'').decode(errors='replace')if isinstance(error.stdout,bytes)else(error.stdout or '')
   row['partialStderr']=(error.stderr or b'').decode(errors='replace')if isinstance(error.stderr,bytes)else(error.stderr or '')
  driver.persist(directory,'failure-before-cleanup.json',row)
 finally:
  if actor and actor.poll()is None:
   try:actor.wait(timeout=5)
   except subprocess.TimeoutExpired:
    row.update(diagnosticActorStillLive=True,normalCleanupAccepted=False,actorPID=actor.pid)
    own=Path('/proc')/str(actor.pid);row['ownedActorEvidence']={}
    for name in ['stat','status','wchan','cgroup']:
     try:row['ownedActorEvidence'][name]=(own/name).read_text()[:65536]
     except OSError as error:row['ownedActorEvidence'][name]={'error':repr(error)}
  if actor and actor.poll()is not None:row['actualChildExitCode']=actor.returncode;row['actualActorGone']=not(Path('/proc')/str(actor.pid)).exists()
 row['sourcesUnchanged']=all(driver.sha(p)==h for p,h in build['sources'].items());report=directory/'report.json';driver.persist(directory,report.name,row);print(json.dumps({'result':row['result'],'report':str(report),'exitCode':row.get('exitCode')}));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
