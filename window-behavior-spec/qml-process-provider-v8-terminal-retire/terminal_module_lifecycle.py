from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,uuid
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();build=json.loads((B/'terminal-module-build-v1.json').read_text());assert build['result']=='pass' and all(sha(p)==h for p,h in build['sources'].items());assert sha(B/'libobjectlifetime-process-terminal.so')==build['outputs'][str(B/'libobjectlifetime-process-terminal.so')] and sha(B/'cpu-terminal-dso')==build['outputs'][str(B/'cpu-terminal-dso')];before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py','.moc')};runtime=Path('/run/user')/str(os.getuid())/'wqa'/uuid.uuid4().hex[:4];runtime.mkdir(mode=0o700);home=runtime/'home';home.mkdir(mode=0o700);image=home/'libobjectlifetime.so';shutil.copyfile(B/'libobjectlifetime-process-terminal.so',image);image.chmod(0o644);env=dict(os.environ)
 for k in ('DISPLAY','WAYLAND_DISPLAY','WAYLAND_SOCKET','DBUS_SESSION_BUS_ADDRESS','DBUS_SYSTEM_BUS_ADDRESS','LD_PRELOAD','LD_AUDIT','QML_IMPORT_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM','WINDOW_OBJECT_LIFETIME_CONFIG'):env.pop(k,None)
 config=home/'lifetime.config';env.update(HOME=str(home),XDG_RUNTIME_DIR=str(runtime),WINDOW_OBJECT_LIFETIME_CONFIG=str(config));argv=[str(B/'cpu-terminal-dso'),str(image),'lifecycle'];r=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=30);stable=all(sha(p)==h for p,h in before.items());row=dict(result='pass'if r.returncode==0 and stable else'fail',argv=argv,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr,sourceUnchanged=stable,sources=before,actualLibrarySHA256=sha(image),productionBuildSHA256=sha(B/'terminal-module-build-v1.json'),QCoreCPUOnly=True,GUI=False,installedQSProcessAccepted=False,ProcessRouteKernelAcceptanceProvenByThisCase=False,normalPrivateRuntimeRemoved=False)
 if config.exists():row['actualConfigRaw']=config.read_text()
 if r.returncode==0:shutil.rmtree(runtime);row['normalPrivateRuntimeRemoved']=not runtime.exists()
 else:row['retainedFailureRuntime']=str(runtime)
 p=B/f'terminal-module-lifecycle-{time.time_ns()}.json';p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p),exitCode=r.returncode)));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
