#!/usr/bin/python3
import hashlib,json,pathlib,subprocess,time,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/f'test-{time.time_ns()}';out.mkdir(mode=0o700);inputs=out/'inputs';inputs.mkdir()
 report={'passed':False,'nativeAcceptance':False,'checks':[]}
 try:
  build=json.loads((ROOT/'client-build-report.json').read_text());assert build['passed'];binary=pathlib.Path(build['artifact']['path']);assert sha(binary)==build['artifact']['sha256']
  for name,row in build['sources'].items():assert sha(ROOT/name)==row['sha256']
  for name in ['native/commands.h','native/gtk-role-client.c','qa/test.py','client-build-report.json']:
   q=inputs/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,q)
  valid=['1 open-sibling','2 close-sibling','3 reparent-sibling A','4 reparent-sibling B','1 create-owners','1 open-modal','1 close-modal','1 close-owner','1 create-family','2 open-nested','3 close-nested','4 open-popover','5 close-popover','6 inspect','7 quit','8 minimize A','9 restore C','10 maximize A','11 unmaximize C','9223372036854775807 inspect']
  invalid=['1 reparent-sibling','1 reparent-sibling C','1 reparent-sibling E','1 reparent-sibling AA','1 open-sibling A','1 close-sibling B','1 reparent-sibling B extra','','0 inspect','01 inspect','-1 inspect','+1 inspect','1.0 inspect','true inspect','9223372036854775808 inspect','9'*200+' inspect','1 unknown','1 minimize','1 minimize B','1 minimize AA','1 inspect A','1 quit extra extra','1 inspect extra','1 maximize C extra','1'*512]
  checks=[]
  def checked(label,args,expected):
   p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3);assert p.returncode==expected,(label,p.returncode,p.stderr);checks.append({'name':label,'passed':True})
  for index,line in enumerate(valid):checked(f'actual-cli-valid-{index}',[str(binary),'--validate-command',line],0)
  for index,line in enumerate(invalid):checked(f'actual-cli-invalid-{index}',[str(binary),'--validate-command',line],6)
  checked('describe-before-display',[str(binary),'--describe'],0)
  checked('reject-unowned-runtime-before-gtk',[str(binary),'--run'],2)
  # Compile the actual production parser and execute the same external contract table.
  cases='\n'.join('if(parse_command('+json.dumps(line)+',&c) != '+('true' if line in valid else 'false')+')return '+str(index+1)+';' for index,line in enumerate(valid+invalid))
  harness='#define _POSIX_C_SOURCE 200809L\n#include "commands.h"\nint main(void){struct command c;\n'+cases+'\nreturn 0;}\n'
  (out/'parser-test.c').write_text(harness);shutil.copyfile(ROOT/'native/commands.h',out/'commands.h')
  def compile_run(directory):
   p=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(directory/'parser-test.c'),'-o',str(directory/'test')],capture_output=True);(directory/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
   return subprocess.run([str(directory/'test')],timeout=3).returncode
  assert compile_run(out)==0;checks.append({'name':'actual-header-contract-table','passed':True})
  source=(ROOT/'native/commands.h').read_text()
  mutants=[('overflow-int64',source.replace('number>INT64_MAX || ','')),('unknown-operation',source.replace('(!targeted && !plain && !reparent)','false')),('leading-zero',source.replace(" || sequence[0]=='0'",''))]
  for name,mutant in mutants:
   directory=out/name;directory.mkdir();(directory/'commands.h').write_text(mutant);(directory/'parser-test.c').write_text(harness);code=compile_run(directory);assert code!=0,name;checks.append({'name':'unsafe-'+name+'-behaviorally-rejected','passed':True,'exit':code})
  report.update(passed=True,checks=checks,sourceInputs={str(p.relative_to(inputs)):{'sha256':sha(p)} for p in inputs.rglob('*') if p.is_file()},buildReport=str(ROOT/'client-build-report.json'),buildReportSHA256=sha(ROOT/'client-build-report.json'))
 except Exception as e:report['error']=str(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
