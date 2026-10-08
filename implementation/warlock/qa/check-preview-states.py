"""Focused actual native key isolation plus bounded ownership model; no GUI claim."""
import json,os,pathlib,subprocess,tempfile,shlex
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope()
root=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='warlock-picker-keys-') as directory:
 p=pathlib.Path(directory)
 (p/'keys.cpp').write_text(r'''
#include "picker-probe-table.hpp"
#include "family_frame.hpp"
#include <cassert>
#include <map>
#include <stdexcept>
int main() {
  std::map<CaptureKey,int> records;
  records.emplace(CaptureKey(5),7);
  { CaptureSelection first(10); records.emplace(CaptureKey(5),11);
    { CaptureSelection second(20); records.emplace(CaptureKey(5),22); assert(records.at(CaptureKey(5))==22); }
    assert(records.at(CaptureKey(5))==11);
    try {CaptureSelection other(30);throw std::runtime_error("unwind");}catch(const std::runtime_error&){}
    assert(records.at(CaptureKey(5))==11);
  }
  assert(CaptureKey::selected==0 && records.at(CaptureKey(5))==7 && records.size()==3);
  {CaptureSelection foreign(10);assert(!records.contains(CaptureKey(6)));records.erase(CaptureKey(5));}
  {CaptureSelection untouched(20);assert(records.at(CaptureKey(5))==22);}
  assert(records.at(CaptureKey(5))==7);
  using namespace preview::bridge;
  FamilySourceObservation observed;observed.picker=true;
  Json refused("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-probe-context-stale\"}");
  bool known=false;
  try {decodeFamilyCapture(refused,observed,1,2);}catch(const PickerCaptureRefused&){known=true;}
  assert(known);
  Json unknown("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-probe-retire-required\"}");
  bool unproven=false;
  try {decodeFamilyCapture(unknown,observed,1,2);}catch(const PickerCaptureRefused&){assert(false);}catch(const std::runtime_error&){unproven=true;}
  assert(unproven);

}
''')
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','json-glib-1.0','gio-unix-2.0'],text=True))
 commands=[['g++','-std=c++20','-Wall','-Wextra','-Werror','-I'+str(root/'native'),str(p/'keys.cpp'),'-o',str(p/'keys'),*flags],[str(p/'keys')],['quint','typecheck','qa/picker-ownership.qnt'],['quint','test','qa/picker-ownership.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79101'],['quint','run','qa/picker-ownership.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79102']]
 for command in commands:
  result=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=120)
  print(json.dumps({'command':command[0:3],'exitCode':result.returncode}),flush=True)
  if result.returncode:raise RuntimeError(result.stdout+'\n'+result.stderr)
 print(json.dumps({'passed':True,'nativeAcceptance':False,'protectedScope':scope}),flush=True)
