"""Bind reviewed fixture and independent PNG oracle to the exact new native tuple."""
import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 old=REPO/'implementation/warlock-client-source-native-v1/qa/preflight.json';pre=json.loads(old.read_text());assert pre['passed']
 for path,digest in pre['inputs'].items():assert sha(path)==digest,path
 fixture=REPO/'implementation/warlock-client-child-fixture-v1';build=fixture/'qa/client-build-1791235154755754755/report.json';packet=json.loads(build.read_text());assert packet['passed'] and sha(packet['client'])==packet['clientSHA256']
 for key in ['inputs','tools','dependencies','linkedLibraries']:
  for path,digest in packet[key].items():assert sha(path)==digest,path
 inputs=dict(pre['inputs']);inputs[str(old)]=sha(old);inputs[str(build)]=sha(build);inputs[packet['client']]=packet['clientSHA256']
 owner=REPO/'implementation/warlock-client-source-revisions-v2';descriptor=json.loads((owner/'native-build-report.json').read_text());assert descriptor['result']=='pass'
 core=pathlib.Path(descriptor['coreComponentManifest']);assert sha(core)==descriptor['coreComponentManifestSHA256'];corePacket=json.loads(core.read_text());assert corePacket['sourceHeld'] and corePacket['evidenceIntegrityPassed']
 for rel,row in corePacket['files'].items():assert sha(core.parent/rel)==row['sha256'];inputs[str(core.parent/rel)]=row['sha256']
 inputs[str(core)]=sha(core);inputs[descriptor['binary']]=descriptor['sha256'];inputs[descriptor['plugin']['path']]=descriptor['plugin']['sha256'];inputs[descriptor['pluginBuildReport']]=descriptor['pluginBuildReportSHA256']
 for path in [*ROOT.glob('*.py'),*ROOT.glob('*.json'),*owner.glob('*.json'),*owner.joinpath('native').glob('*'),*owner.joinpath('candidate').glob('*')]:
  if path.is_file():inputs[str(path)]=sha(path)
 pre['pair']['core']={'path':descriptor['binary'],'sha256':descriptor['sha256']};pre['pair']['plugin']=descriptor['plugin']
 for path in [*fixture.glob('*.json'),*fixture.glob('*.md'),*fixture.joinpath('native').glob('*'),*fixture.joinpath('qa').glob('*.py'),ROOT/'peer.py',ROOT/'pixels.cpp',*ROOT.joinpath('qa').glob('*.py')]:
  if path.is_file():inputs[str(path)]=sha(path)
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libpng'],text=True));cmd=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(ROOT/'pixels.cpp'),'-o',str(OUT/'pixels'),*flags];p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(OUT/'compile.stdout').write_text(p.stdout);(OUT/'compile.stderr').write_text(p.stderr);r.update(argv=cmd,exitCode=p.returncode);assert p.returncode==0,p.stderr
 validation=subprocess.run([packet['client'],'--validate'],capture_output=True,text=True,timeout=5);(OUT/'fixture-validation.stdout').write_text(validation.stdout);(OUT/'fixture-validation.stderr').write_text(validation.stderr);assert validation.returncode==0 and json.loads(validation.stdout)['valid']
 inputs[str(OUT/'pixels')]=sha(OUT/'pixels');assert all(sha(path)==digest for path,digest in inputs.items())
 pre.update(inputs=inputs,pixelOracle=str(OUT/'pixels'),fixtureClient=packet['client'],nativeLaunched=False,nativeAcceptance=False,fullReleaseAccepted=False,scope='Actual desync/sync queued-versus-applied child state, nested membership/geometry/retirement on exact applied-revision-core/source plugin. No production eligibility or full release acceptance')
 (ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');r.update(passed=True,inputs=inputs,pair=pre['pair'])
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
