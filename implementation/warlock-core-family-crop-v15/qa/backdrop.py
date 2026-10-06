import hashlib,json,pathlib,resource,shutil,subprocess,sys,time,shlex
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('backdrop-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
TOOL='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
paths=[pathlib.Path(__file__),ROOT/'qa/backdrop.qnt',ROOT/'qa/backdrop-replay.cpp',ROOT/'candidate/src/render/warlock/shader_plane.hpp',ROOT/'SPEC.md']
owner=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-family-style-crop-capture-v13/native');paths+=list(owner.glob('*.hpp'))
inputs={str(p):sha(p) for p in paths}
for p in paths[:5]:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'inputs':inputs,'commands':[]}
try:
 names=['backdropOutputPlanePeakTest','backdropCropOnlyCapacityRefusedTest','backdropExactCapacityTest','backdropOneByteShortTest','backdropOffOutputRefusedTest','backdropOutsideRightRefusedTest','backdropOversizedOutputRefusedTest','backdropInsufficientEncodedPlanTest','backdropMaximumPlaneTest']
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0'],text=True))
 commands=[('compile',['g++','-std=c++23','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-Wall','-Wextra','-Werror','-I'+str(OUT),str(OUT/'backdrop-replay.cpp'),*flags,'-o',str(OUT/'replay')]),('typecheck',[TOOL,'typecheck',str(OUT/'backdrop.qnt')]),('selected',[TOOL,'test',str(OUT/'backdrop.qnt'),'--main=backdrop','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=800017','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')])]
 for name,argv in commands:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 traces=sorted(OUT.glob('named-*.itf.json'));assert len(traces)==len(names);replays=[]
 for trace in traces:
  states=json.loads(trace.read_text())['states'];number=lambda row,k:int(row[k]['#bigint']);projection=OUT/(trace.stem+'.tsv');projection.write_text(''.join(' '.join(map(str,[*[number(row,k) for k in ['w','h','x','y','cw','ch','encoded','limit']],int(row['valid']),number(row,'peak'),int(row['admitted'])]))+'\n' for row in states));p=subprocess.run([str(OUT/'replay'),str(projection)],capture_output=True,text=True,timeout=5);(OUT/(trace.stem+'.stdout')).write_text(p.stdout);(OUT/(trace.stem+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr;j=json.loads(p.stdout);assert j['states']==len(states) and j['passed'];replays.append(j)
 assert all(sha(p)==h for p,h in inputs.items());r.update(passed=True,selectedNames=names,states=sum(j['states'] for j in replays),replays=replays)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
