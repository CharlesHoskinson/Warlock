import hashlib,json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parent;REPO=ROOT.parents[2];OUT=ROOT/('pixel-proof-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
label=sys.argv[1];assert label in ['counterexample','fixed'];version={'counterexample':62,'fixed':63}[label]
reports=list((REPO/('implementation/warlock-client-provider-native-v'+str(version))).glob('qa/native-*/report.json'));assert len(reports)==1
report=reports[0];native=json.loads(report.read_text());assert native['cleanupPassed'] and all(row['exitCode']==0 for row in native['ownedExitCodes']) and native['passed']==(label=='fixed')
before=native['opacityConfigurationEvidence']['before'];root=next(row['geometry'] for row in before['members'] if row['incarnation']==before['scope']['context']['incarnation']);crop=before['crop'];base=report.parent/'private-evidence'
files=[base/(name+'.png') for name in ['config-opacity-half','config-opacity-opaque','config-opacity-half-native-output','config-opacity-opaque-native-output']]
inputs={str(p):sha(p) for p in [report,ROOT/'opacity-pixels.cpp',pathlib.Path(__file__),*files]}
program=OUT/'opacity-pixels';command=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(ROOT/'opacity-pixels.cpp'),'-o',str(program),'-lpng']
p=subprocess.run(command,capture_output=True,text=True,timeout=180);(OUT/'compile.stdout').write_text(p.stdout);(OUT/'compile.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
argv=[str(program),*map(str,files),crop['pixelX'],crop['pixelY'],*map(lambda x:str(int(x)),root[:4])]
p=subprocess.run(argv,capture_output=True,text=True,timeout=5);(OUT/'pixels.stdout').write_text(p.stdout);(OUT/'pixels.stderr').write_text(p.stderr)
result=json.loads(p.stdout);assert all(sha(p)==h for p,h in inputs.items())
r={'passed':p.returncode==0 and result['passed'],'label':label,'scope':scope,'inputs':inputs,'command':command,'argv':argv,'exitCode':p.returncode,'result':result,'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()},'nativeAcceptance':False,'fullReleaseAccepted':False}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'pixels':result}));raise SystemExit(not r['passed'])
