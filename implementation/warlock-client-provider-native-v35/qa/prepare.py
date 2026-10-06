import hashlib,json,pathlib,resource,sys,time,subprocess,shlex,traceback
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 parent=REPO/'implementation/warlock-client-provider-native-v34';old=parent/'qa/preflight.json';pre=json.loads(old.read_text());assert pre['passed']
 inputs=dict(pre['inputs'])
 for p,h in inputs.items():assert sha(p)==h,p
 inputs[str(old)]=sha(old)
 baseline=parent/'qa/native-1791257839724867928/report.json';accepted=json.loads(baseline.read_text());assert accepted['passed'] and accepted['cleanupPassed'] and len(accepted['checks'])==1351 and all(row['passed'] for row in accepted['checks']) and len(accepted['ownedExitCodes'])==125 and all(row['exitCode']==0 for row in accepted['ownedExitCodes'])
 for rel,h in accepted['artifacts'].items():assert sha(baseline.parent/rel)==h,rel
 inputs[str(baseline)]=sha(baseline);pre['retainedFamilyObserverReport']=str(baseline)
 owner=REPO/'implementation/warlock-family-capture-v1';descriptor=owner/'native-build-report.json';pair=json.loads(descriptor.read_text());assert pair['result']=='pass' and sha(ROOT/'native-build-report.json')==sha(descriptor) and sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
 build=pathlib.Path(pair['pluginBuildReport']);assert sha(build)==pair['pluginBuildReportSHA256'];compiled=json.loads(build.read_text());assert compiled['passed'] and not compiled['missingSymbols']
 coreReport=pathlib.Path(pair['buildReport']);assert sha(coreReport)==pair['buildReportSHA256'];coreBuilt=json.loads(coreReport.read_text());assert coreBuilt['passed'] and pathlib.Path(coreBuilt['ancestor']['report']).parent/'Hyprland'==pathlib.Path(pre['pair']['core']['path'])
 coreManifest=pathlib.Path(pair['coreComponentManifest']);assert sha(coreManifest)==pair['coreComponentManifestSHA256'];held=json.loads(coreManifest.read_text())
 for rel,row in held['files'].items():assert sha(coreManifest.parent/rel)==row['sha256'],rel
 for proof in [compiled,coreBuilt]:
  for key in ['dependencies','linkDependencies','linkedLibraries','tools']:
   for p,h in proof.get(key,{}).items():assert sha(p)==h,p;inputs[p]=h
 for rel,h in compiled['inputs'].items():assert sha(owner/rel)==h,rel;inputs[str(owner/rel)]=h
 closure=pathlib.Path(pair['linkClosureReport']);assert sha(closure)==pair['linkClosureReportSHA256'] and not json.loads(closure.read_text())['missingSymbols']
 for p in [descriptor,build,closure,coreReport,coreManifest,pathlib.Path(pair['binary']),pathlib.Path(pair['plugin']['path']),*ROOT.glob('*'),*ROOT.joinpath('qa').glob('*.py')]:
  if p.is_file():inputs[str(p)]=sha(p)
 familyFD=REPO/'implementation/warlock-family-fd-qualification-v1/qa/test-report.json';pointer=json.loads(familyFD.read_text());familyFDReport=pathlib.Path(pointer['path']);assert sha(familyFDReport)==pointer['sha256'];proof=json.loads(familyFDReport.read_text());assert proof['passed'] and proof['evidence']['physicalFDClosed'] and proof['evidence']['physicalMappingClosed']
 for p,h in proof['inputs'].items():assert sha(p)==h,p;inputs[p]=h
 for rel,h in proof['artifacts'].items():assert sha(familyFDReport.parent/rel)==h,rel;inputs[str(familyFDReport.parent/rel)]=h
 inputs[str(familyFD)]=sha(familyFD);inputs[str(familyFDReport)]=sha(familyFDReport);pre['familyFDReport']=str(familyFDReport)
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libpng'],text=True))
 for name,key in [('modal-pixels','modalPixelOracle'),('family-pixels','familyPixelOracle')]:
  argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(ROOT/(name+'.cpp')),*flags,'-o',str(OUT/name)];p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr;inputs[str(OUT/name)]=sha(OUT/name);pre[key]=str(OUT/name)
 pre['pair']['core']={'path':pair['binary'],'sha256':pair['sha256']};pre['pair']['plugin']=pair['plugin'];pre['inputs']=inputs
 assert all(sha(p)==h for p,h in inputs.items());(ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');r.update(passed=True,inputs=inputs,pair=pre['pair'])
except Exception as e:r['error']=repr(e);r['traceback']=traceback.format_exc()
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
