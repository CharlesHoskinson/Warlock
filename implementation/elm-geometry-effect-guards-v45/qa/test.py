"""Compile actual native authority barrier and challenge it with independent set oracle."""
import hashlib,json,random,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
SOURCE=REPO/'implementation/elm-window-geometry-effects-v42/candidate/EffectBarrier.hpp'
OUT=ROOT/'qa'/('guards-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=SOURCE.read_text();source_sha=sha(SOURCE)
shutil.copy2(SOURCE,OUT/'EffectBarrier.hpp');shutil.copy2(__file__,OUT/'test.py')
fixture=r'''
#include "EffectBarrier.hpp"
#include <cstdio>
#include <set>
#include <utility>
using Elm::Geometry::Target;
using Elm::Geometry::Barriers;
unsigned checks=0;
bool check(bool value,const char*name){++checks;if(!value)std::fprintf(stderr,"FAIL %s\n",name);return value;}
#define REQUIRE(v,n) if(!check((v),(n)))return 1
int main(){
 Barriers b;
 REQUIRE(!b.begin({0,1})&&!b.begin({1,0})&&!b.begin({0,0}),"zero identities refuse without capacity use");
 REQUIRE(b.begin({7,11})&&b.blocked({7,11}),"reservation blocks exact native target");
 REQUIRE(!b.begin({7,11}),"duplicate operation cannot reserve again");
 REQUIRE(!b.blocked({8,11})&&!b.blocked({7,12}),"native lifetime/incarnation isolated");
 // No peer, frontend or effect version exists in the production key. A new
 // transport caller sees the same unresolved target and cannot reacquire it.
 REQUIRE(!b.begin({7,11}),"new caller cannot bypass unresolved target");
 b.definitive({8,11});b.retire({7,12});
 REQUIRE(b.blocked({7,11}),"unrelated receipts/retirements cannot clear Unknown");
 b.definitive({7,11});REQUIRE(!b.blocked({7,11})&&b.begin({7,11}),"definitive readback permits new reservation");
 b.retire({7,11});REQUIRE(!b.blocked({7,11}),"exact native retirement releases target");
 for(unsigned i=1;i<=256;++i)REQUIRE(b.begin({9,i}),"all256 slots usable");
 REQUIRE(!b.begin({9,257}),"full capacity refuses without eviction");
 for(unsigned i=1;i<=256;++i)REQUIRE(b.blocked({9,i}),"full refusal preserves prior unresolved targets");
 b.retire({9,128});REQUIRE(b.begin({9,257})&&!b.blocked({9,128}),"exact retirement permits one slot reuse");
 for(unsigned i=1;i<=257;++i)b.retire({9,i});
 // A fixed deterministic production replay against an independent mathematical
 // set. This is CPU evidence, not compositor reentrancy/retirement qualification.
 std::set<std::pair<unsigned long long,unsigned long long>> oracle;
 unsigned long long state=0x8d8bd43a74638a91ULL;
 for(unsigned i=0;i<50000;++i){state=state*6364136223846793005ULL+1442695040888963407ULL;
  Target target{(state>>48)%4,(state>>16)%340};auto key=std::make_pair(target.lifetime,target.incarnation);
  switch(state%4){
   case 0:{bool expected=target.lifetime&&target.incarnation&&!oracle.contains(key)&&oracle.size()<256;
    bool actual=b.begin(target);REQUIRE(actual==expected,"random begin matches independent set/capacity oracle");if(expected)oracle.insert(key);break;}
   case 1:b.definitive(target);oracle.erase(key);break;
   case 2:b.retire(target);oracle.erase(key);break;
   case 3:REQUIRE(b.blocked(target)==oracle.contains(key),"random lookup matches independent oracle");break;
  }
  for(const auto& entry:oracle)REQUIRE(b.blocked({entry.first,entry.second}),"remaining reservations never evicted");
 }
 std::printf("checks %u\n",checks);return 0;
}
'''
variants=[('actual',original),('unsafe-duplicate',original.replace(' || blocked(target)','')),('unsafe-drop-lifetime',original.replace('*e==target','e->incarnation==target.incarnation')),('unsafe-clear-all',original.replace('if(e && *e==target){e.reset();return;}','if(e){(void)target;e.reset();}')),('unsafe-evict-on-full',original.replace('        return false;\n    }\n    void definitive','        entries_[0]=target;return true;\n    }\n    void definitive')),('unsafe-zero-identity',original.replace('!target.lifetime || !target.incarnation || ',''))]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual V42 authority-wide barrier CPU set-oracle replay; no native effects, journal, receipt, compositor reentrancy or recovery acceptance','source':str(SOURCE),'sourceSHA256':source_sha,'checks':[]}
try:
 for name,header in variants:
  if name!='actual':assert header!=original,name
  out=OUT/name;out.mkdir();(out/'EffectBarrier.hpp').write_text(header);(out/'test.cpp').write_text(fixture)
  binary=out/'test';command=['g++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(out/'test.cpp'),'-o',str(binary)]
  build=subprocess.run(command,capture_output=True,text=True,timeout=60);(out/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
  result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15);(out/'run.log').write_text(result.stdout+result.stderr)
  r['checks'].append({'name':name,'passed':result.returncode==(0 if name=='actual' else 1),'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'command':command})
 assert sha(SOURCE)==source_sha,'Production header changed after capture'
 r['passed']=all(check['passed'] for check in r['checks'])
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
