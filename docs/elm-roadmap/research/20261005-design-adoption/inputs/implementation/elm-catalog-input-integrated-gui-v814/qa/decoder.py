import hashlib,json,pathlib,shutil,subprocess,sys,time,os
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify,command as pin_command
r=pathlib.Path(__file__).resolve().parents[1];o=r/'qa'/('decoder-'+str(time.time_ns()));o.mkdir();inputs=o/'inputs';shutil.copytree(r/'src',inputs/'src');shutil.copy2(r/'elm.json',inputs/'elm.json');shutil.copy2(r/'qa/DecoderProbe.elm',inputs/'src/DecoderProbe.elm');shutil.copy2(r/'qa/decoder.cjs',o/'decoder.cjs');held=verify();shutil.copytree(r/held['elmHome'],o/'mutable-elm-home');rows=[]
good={'surfaceProtocol':2,'kind':'surface-action','surface':'bar','publication':'1','lease':'0','id':'bar:group:A'};cases=[]
def case(name,raw,accepted):cases.append({'name':name,'raw':raw,'accepted':accepted})
case('exact-six-fields',good,True);case('canonical-max-counters',{**good,'publication':'18446744073709551615','lease':'18446744073709551615'},True);case('max-identity512',{**good,'id':'x'*512},True);case('valid-popup',{**good,'surface':'popup'},True)
for field in good:case('missing-'+field,{k:v for k,v in good.items() if k!=field},False)
for name,field,value in [('extra','extra',0),('zero-publication','publication','0'),('leading-zero','publication','01'),('overflow','publication','18446744073709551616'),('numeric-publication','publication',1),('negative-lease','lease','-1'),('leading-zero-lease','lease','00'),('numeric-lease','lease',0),('invalid-surface','surface','other'),('wrong-kind','kind','other'),('wrong-protocol','surfaceProtocol',3),('empty-id','id',''),('identity513','id','x'*513),('C0-id','id','x'+chr(1))]:case(name,{**good,field:value},False)
(o/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n')
mutants=[('omit-strict-fields','if List.sort (List.map Tuple.first pairs) /= fields','if False','extra decoder assertion'),('permit-overlong-identity','String.length value.identity<=512','True','identity513 decoder assertion'),('remint-encoded-publication','UInt64.string value.publication','UInt64.string (UInt64.next value.publication |> Maybe.withDefault UInt64.zero)','exact-six-fields decoder assertion')]
report={'passed':False,'commands':rows,'nativeAcceptance':False,'sourceAuthentication':False,'productQualified':False,'cases':len(cases)}
def run(name,cmd,cwd):
 verify();p=subprocess.run(pin_command(cmd),cwd=cwd,capture_output=True,text=True,timeout=180,env=dict(os.environ,ELM_HOME=str(o/'mutable-elm-home'),http_proxy='http://127.0.0.1:9',https_proxy='http://127.0.0.1:9',HTTP_PROXY='http://127.0.0.1:9',HTTPS_PROXY='http://127.0.0.1:9'));verify();(o/(name+'.log')).write_text(p.stdout+p.stderr);rows.append({'name':name,'command':pin_command(cmd),'exitCode':p.returncode});return p
try:
 original=(inputs/'src/CapturedAction.elm').read_text()
 for name,before,after,oracle in [('original',None,None,None)]+mutants:
  (inputs/'src/CapturedAction.elm').write_text(original if before is None else original.replace(before,after));assert before is None or original.count(before)==1
  shutil.copy2(inputs/'src/CapturedAction.elm',o/(name+'-CapturedAction.elm'));worker=o/(name+'.js');p=run(name+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/DecoderProbe.elm','--optimize','--output='+str(worker)],inputs);assert p.returncode==0,p.stderr
  p=run(name+'-cases',['node',str(o/'decoder.cjs'),str(worker),str(o/'fixtures.json'),str(o/(name+'-rows.json'))],inputs)
  assert (p.returncode==0 if oracle is None else p.returncode!=0 and oracle in p.stderr),(name,p.stderr)
 report['passed']=True;report['typedMutantsKilled']=len(mutants);report['elmToolchain']=held;report['sourceHeld']=(r/'src/CapturedAction.elm').read_text()==original
except BaseException as e:report['error']=repr(e)
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(o/'report.json');raise SystemExit(not report['passed'])
