import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-preview-producer-refusal-v517/src/preview_broker.hpp'
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('qualification-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual Broker native producer-refusal retirement, cancellation and owned-buffer preservation with sanitizer and precise compiled regressions; no service integration or native acceptance','inputs':{str(SOURCE):sha(SOURCE),str(pathlib.Path(__file__)):sha(pathlib.Path(__file__))},'variants':[]}
fixture=r'''#include "preview_broker.hpp"
#include <iostream>
using namespace preview;
static unsigned checks=0;
static void check(bool ok,const char* text){if(!ok)throw std::runtime_error(text);++checks;}
struct Image final:Buffer{unsigned& frees;Image(unsigned& n):frees(n){}~Image(){++frees;}uint64_t charge()const noexcept override{return 32;}};
int main(){try{
 Scope scope{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{10},100,true,true,false,true};Job job{scope.binding,scope.context,{1},{11},scope.clock,102};
 Broker b({1,4,1,32});check(b.enroll(4,scope,32),"source enrolled");check(b.acquire(4,scope.binding,job).status==Result::Status::Admitted,"actual reserve");
 auto denied=b.producerRefused(5,job);check(denied.receipts.empty(),"wrong native entry cannot settle");auto wrong=job;wrong.context.content={10};check(b.producerRefused(4,wrong).receipts.empty(),"wrong native source job cannot settle");
 auto closed=b.producerRefused(4,job);check(closed.status==Result::Status::Complete && closed.receipts.size()==1 && closed.receipts[0].kind==Receipt::Kind::Refused && closed.receipts[0].job==job,"producer refusal has exact typed stable receipt");
 auto duplicate=b.producerRefused(4,job);check(duplicate.status==Result::Status::Duplicate && duplicate.receipts[0].sequence==closed.receipts[0].sequence,"duplicate refusal preserves receipt identity");
 unsigned frees=0;std::unique_ptr<const Buffer> late=std::make_unique<const Image>(frees);check(b.allocate(4,job,late,104).receipts.empty() && late && !frees,"late allocation cannot adopt a refused job");late.reset();
 auto next=job;next.request={2};check(b.acquire(4,scope.binding,next).status==Result::Status::Admitted,"producer refusal releases reserved budget");
 check(!b.acknowledge(4,scope.binding,job,{closed.receipts[0].sequence.value+1}),"wrong final receipt cannot erase ledger");check(b.acknowledge(4,scope.binding,job,closed.receipts.back().sequence),"exact final refusal acknowledgement retires ledger");check(b.acquire(4,scope.binding,job).receipts.empty(),"refused request floor survives acknowledgement");
 b.cancel(4,scope.binding,next);auto cancelled=b.producerRefused(4,next);check(cancelled.receipts.size()==2 && cancelled.receipts[0].kind==Receipt::Kind::Refused && cancelled.receipts[1].kind==Receipt::Kind::Cancelled,"cancel racing refusal retains both terminal proofs");check(b.acknowledge(4,scope.binding,next,cancelled.receipts.back().sequence),"cancellation final sequence retires exact ledger");
 auto owned=job;owned.request={3};check(b.acquire(4,scope.binding,owned).status==Result::Status::Admitted,"owned job admitted");std::unique_ptr<const Buffer> image=std::make_unique<const Image>(frees);auto allocated=b.allocate(4,owned,image,104);check(!image && allocated.receipts.size()==1,"actual buffer adopted");
 auto refusal=b.producerRefused(4,owned);check(refusal.receipts.empty() && frees==1,"owned packet cannot produce refusal or free physical image");auto fence=b.producerComplete(4,owned);check(fence.receipts.size()==1 && b.fetch(4,scope.binding,allocated.receipts[0].packet->token),"owned packet survives attempted producer refusal");b.cancel(4,scope.binding,owned);check(b.consumerComplete(4,owned),"consumer retires after native cancellation");auto released=b.destroy(4,owned);check(frees==2 && released.receipts.size()==2 && released.receipts[0].kind==Receipt::Kind::Released,"actual owned buffer frees before release proof");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''
try:
 for name,old,new,oracle in [('sanitize',None,None,None),('budget','r->bytes=0; r->terminal=true;\n        auto refused=','r->terminal=true;\n        auto refused=','producer refusal releases reserved budget'),('owned','if(r->packet || r->buffer) return {};','if(false) return {};','owned packet cannot produce refusal or free physical image'),('cancel','if(r->cancelled) {auto cancelled=receipt(Receipt::Kind::Cancelled,*r); if(cancelled) r->proof.push_back(*cancelled);}','/* lost cancellation proof */','cancel racing refusal retains both terminal proofs')]:
  folder=OUT/name;folder.mkdir();s=SOURCE.read_text()
  if old:assert s.count(old)==1;s=s.replace(old,new,1)
  (folder/'preview_broker.hpp').write_text(s);(folder/'checks.cpp').write_text(fixture);args=['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror',str(folder/'checks.cpp'),'-o',str(folder/'checks')]
  if name=='sanitize':args+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  p=subprocess.run(args,capture_output=True,text=True,timeout=180);(folder/'compile.stdout').write_text(p.stdout);(folder/'compile.stderr').write_text(p.stderr);row={'name':name,'compile':{'argv':args,'exitCode':p.returncode}};r['variants'].append(row);assert p.returncode==0,p.stderr[-3000:]
  p=subprocess.run([str(folder/'checks')],capture_output=True,text=True,timeout=30);(folder/'checks.stdout').write_text(p.stdout);(folder/'checks.stderr').write_text(p.stderr);row.update(binarySHA256=sha(folder/'checks'),execution={'exitCode':p.returncode})
  if name=='sanitize':assert p.returncode==0 and not p.stderr;row['checks']=json.loads(p.stdout)['checks']
  else:assert p.returncode==1 and p.stderr.strip()==oracle;row.update(detected=True,expectedAssertion=oracle)
  print(name,p.returncode,flush=True)
 r['passed']=True
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
