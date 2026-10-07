"""Pause actual legacy admission before CAS across actual controlled C close."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('preview-realm-race-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+[str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual C owner opens and passes all original strict-close guards on the original authenticated synthetic Native socket while a real legacy thread pauses after checking namespace state but before its original atomic compare/exchange. Only QA header adds the pause hook; production logic and full original close/claim lifecycle remain unchanged. Refusal preserves permanent controlled mode across stale CAS. Each owned fixture exits normally before its final behavior assertion; no real Core/WebKit/live-window detachment acceptance.'}
def run(name,args,cwd,required=True):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0'],out/'inputs').stdout)
 h=out/'inputs/native/preview_client.hpp';s=h.read_text();needle='if(owner.previewNamespaces_.compare_exchange_weak(count,count+1,std::memory_order_acq_rel))break;';assert s.count(needle)==1
 s=s.replace(needle,'::preview_realm_legacy_before_cas();'+needle)
 s=s.replace('#pragma once','#pragma once\nvoid preview_realm_legacy_before_cas();',1);h.write_text(s)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/preview-realm-c-test-v3.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args,out/'inputs');p=run('actual-threaded-legacy-admission',[str(out/'checks'),'race'],out/'inputs');e=json.loads(p.stdout);assert e['checks']>30 and e['normalOwnedExit'] and e['nativeRealmEpochThrough']=='1'
 target=out/'unsafe-zero-close';shutil.copytree(out/'inputs',target);h=target/'native/preview_client.hpp';s=h.read_text();needle='previewNamespaces_.compare_exchange_strong(expected,controlledPreviewBit_-1,std::memory_order_acq_rel)';assert s.count(needle)==1;s=s.replace(needle,'previewNamespaces_.compare_exchange_strong(expected,0,std::memory_order_acq_rel)');h.write_text(s)
 mutant=[*args];mutant[mutant.index('-o')+1]=str(target/'checks');run('unsafe-zero-close-compile',mutant,target)
 p=run('unsafe-zero-close-witness',[str(target/'checks'),'race'],target,required=False)
 assertion='Legacy claim cannot cross controlled realm close using stale CAS';assert p.returncode==1 and p.stderr.strip()==assertion,(p.returncode,p.stderr)
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items())
 report.update(passed=True,evidence=e,unsafeCompiledVariantsDetected=1,mutant={'compiled':True,'failedOriginalAssertion':assertion,'normalOwnedCleanupBeforeAssertion':True})
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1800]}),flush=True);sys.exit(not report['passed'])
