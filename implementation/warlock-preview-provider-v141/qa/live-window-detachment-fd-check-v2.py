"""Actual C/socket/SCM_RIGHTS/imported mapping/readers and committed allocator failure."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];plugin=root.parent/'warlock-family-style-crop-capture-v19'
out=root/'qa'/('live-window-detachment-fd-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()};inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
external=sha(plugin/'native/capture-resources.hpp')
report={'passed':False,'inputs':inputs,'pluginResourceHeaderSHA256':external,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual controlled C/Native authenticated synthetic socket and binary SCM_RIGHTS transfer into real ImportedClients mapping/Broker; actual GIO reader/read denial and physical FD closure independently follow scoped backend zero. Controlled allocator-fault derivative enables actual global operator-new failure on the second real Broker adoption allocation after shared storage transfer. Original mapping pointer and packet survive, producer completion and actual Released/Cancelled proofs precede final ACK/scoped detachment/control closure while the synthetic Native application stays Active; readiness is retained before physical cleanup and cannot bypass final job ACK. A lost producer response is repaired without recapture. No compositor pixels/real Core capture/server registry/WebKit/native GUI acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(plugin/'native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/live-window-detachment-fd-test-v2.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args);reader=json.loads(run('actual-mapped-reader',[str(out/'checks')]).stdout)
 assert reader['passed'] and reader['actualImportedFDClosed'] and reader['actualReaderDrained'] and reader['normalOwnedExit']
 lost=json.loads(run('actual-lost-producer-response',[str(out/'checks'),'normal','resource-lost-retire']).stdout);assert lost['passed'] and lost['normalOwnedExit']
 fault=out/'post-transfer-allocator-fault';shutil.copytree(out/'inputs',fault);header=fault/'native/client_import.hpp';s=header.read_text()
 old='namespace preview::bridge {';assert s.count(old)==1
 s=s.replace(old,old+'\nextern thread_local int mappedResourceAllocationFault;extern bool mappedResourceFaultEnabled;')
 old='auto result=broker.allocate(entry,job,payload,expires);';assert s.count(old)==1
 s=s.replace(old,'if(mappedResourceFaultEnabled)mappedResourceAllocationFault=2;\n        '+old);header.write_text(s)
 faultargs=[*args];faultargs[faultargs.index('-o')+1]=str(fault/'checks');run('controlled-allocator-fault-compile',faultargs,fault)
 adoption=json.loads(run('actual-post-transfer-allocator-fault',[str(fault/'checks'),'post-transfer'],fault).stdout)
 assert adoption['passed'] and adoption['postTransferAllocationFault'] and adoption['actualImportedFDClosed'] and adoption['normalOwnedExit']
 mutants=[]
 for name,old,new,witness in [
  ('keep-reader-authorized-after-binding-quarantine','if(quarantined)return {};',';', 'Binding quarantine revokes actual existing reader before first cleanup poll'),
  ('close-imported-mapping-with-live-reader','if(!broker.consumerComplete(entry,f.job))return false;','broker.consumerComplete(entry,f.job);','Native backend zero cannot close mapping or clear charge while actual reader owns it')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/'native/imported_clients.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  result=run(name+'-witness',[str(target/'checks')],target,False);assert result.returncode!=0 and witness in result.stderr.splitlines(),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 assert all(sha(root/rel)==value for rel,value in inputs.items()) and sha(plugin/'native/capture-resources.hpp')==external
 report.update(passed=True,readerEvidence=reader,lostProducerResponseEvidence=lost,postTransferEvidence=adoption,actualSyntheticNativeActiveFact=True,actualWaylandWindowAcceptance=False,controlledFaultHeaderSHA256=sha(header),unsafeCompiledVariantsDetected=2,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
