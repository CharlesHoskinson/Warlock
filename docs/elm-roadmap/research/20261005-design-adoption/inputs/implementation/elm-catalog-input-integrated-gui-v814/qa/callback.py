import hashlib,json,pathlib,re,subprocess,sys,time,shlex,shutil
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];o=r/'qa'/('callback-'+str(time.time_ns()));o.mkdir();source=r/'native/host.c';s=source.read_text()
def extract(name):
 begin=s.index('static '+name);end=s.index('\n}\n',begin)+3;return s[begin:end]
a=extract('const char *asset_name(');c=extract('void scheme(');(o/'actual-asset-name.c').write_text(a);(o/'actual-scheme.c').write_text(c)
header=(r/'qa/callback_fixture.h').read_text();body=(r/'qa/callback_controls.c').read_text();rows=[]
for name,p in [('callback_fixture.h',r/'qa/callback_fixture.h'),('callback_controls.c',r/'qa/callback_controls.c'),('runner.py',pathlib.Path(__file__))]:shutil.copy2(p,o/name)
def command(name,args,expected):
 p=subprocess.run(args,capture_output=True,text=True,timeout=30);(o/(name+'.log')).write_text(p.stdout+p.stderr);rows.append({'name':name,'command':args,'exitCode':p.returncode,'expectedExitCode':expected});assert p.returncode==expected,(name,p.stderr);return p
flags=command('flags',['pkg-config','--cflags','--libs','gio-2.0'],0).stdout
sources=[('current',a,0),('omitted-activation-entry',a.replace(', "activation.js"',''),-6)]
for name,allow,expected in sources:
 p=o/(name+'.c');p.write_text(header+'\n'+allow+'\n'+c+'\n'+body);binary=o/name;command(name+'-compile',['cc','-std=c11','-D_GNU_SOURCE','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(binary),*shlex.split(flags)],0)
 assets=o/(name+'-assets');assets.mkdir(mode=0o700);(assets/'activation.js').write_text('exact activation source\n');(assets/'context.js').write_text('exact context source\n');result=command(name+'-cases',[str(binary),str(assets)],expected)
 if expected:assert 'request.error' in result.stderr and 'should be NULL' in result.stderr
report={'passed':True,'commands':rows,'actualCallbackBodyExtractedExactly':True,'actualFileIO':True,'captureOnlyWebKitAPIFixture':True,'actualNativeRequestObjectExecuted':False,'specificOmissionMutantKilled':True,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceHeld':source.read_text()==s,'nativeLaunched':False,'nativeAcceptance':False,'productQualified':False,'cases':15,'originalProductChangedOnlyActivationEntryAndSelftest':False,'scope':'Actual same786 callback/asset-name in combined814 GUI; no overall product-byte equality claim'};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(o/'report.json')
