import hashlib,json,pathlib,resource,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,(root,pattern);return rows[0]
def evidence(path):
 j=json.loads(path.read_text())
 for rel,h in j.get('artifacts',{}).items():assert sha(path.parent/rel)==h,(path,rel)
 for p,h in j.get('inputs',{}).items():
  if pathlib.Path(p).is_absolute():assert sha(p)==h,p
 return j
model=REPO/'implementation/warlock-family-style-revisions-v6'
modelPath=only(model,'qa/model-*/report.json');m=evidence(modelPath);assert m['passed'] and len(m['selectedNames'])==15 and m['states']==53
controlsPath=only(model,'qa/test-*/report.json');t=evidence(controlsPath);assert t['passed'] and t['evidence']['checks']==314
source=REPO/'implementation/warlock-family-style-crop-capture-v5';pair=json.loads((source/'native-build-report.json').read_text());buildPath=pathlib.Path(pair['pluginBuildReport']);build=evidence(buildPath);assert build['passed'] and not build['missingSymbols']
assert sha(source/'native/style_revision.hpp')==sha(model/'native/style_revision.hpp')
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in build[key].items():assert sha(p)==h,p
assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
coreManifest=pathlib.Path(pair['coreComponentManifest']);core=json.loads(coreManifest.read_text());assert core['sourceHeld'] and core['evidenceIntegrityPassed'] and sha(coreManifest)==pair['coreComponentManifestSHA256']
for rel,row in core['files'].items():assert sha(coreManifest.parent/rel)==row['sha256'],rel
nativeRoot=REPO/'implementation/warlock-client-provider-native-v55';nativePath=only(nativeRoot,'qa/native-*/report.json');native=evidence(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
pre=json.loads((nativeRoot/'qa/preflight.json').read_text());assert pre['passed'] and pre['pair']==native['pair']
for p,h in pre['inputs'].items():assert sha(p)==h,p
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=evidence(originalPath);names=[row['name'] for row in original['checks']];assert len(names)==1783 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['configStyleOldConfigurationScopeRejectedBeforeAllocation','configStyleStaleConfigurationAllocatesNoProducer','configStyleNativeConfigurationOnlyChange','configStyleNativePixelsActuallyChanged','configStyleChangedNativePixelsRequireNewStyleEpoch','allOriginal1783OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
failedRoot=REPO/'implementation/warlock-client-provider-native-v54';failedPath=only(failedRoot,'qa/native-*/report.json');failed=evidence(failedPath);assert not failed['passed'] and failed['cleanupPassed'] and all(row['exitCode']==0 for row in failed['ownedExitCodes']) and any(row['name']=='allOriginal1783OrderedAssertionsRetained' and row['passed'] for row in failed['checks']) and any(row['name']=='configStyleChangedNativePixelsRequireNewStyleEpoch' and not row['passed'] for row in failed['checks'])
assert failed['renderConfigurationEvidence']['bytesChanged'] and not failed['renderConfigurationEvidence']['styleEpochChanged']
proof=OUT/'pixel-proof';assert not proof.exists();proof.mkdir();program=proof/'shadow-pixels'
command=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(OUT/'shadow-pixels.cpp'),'-o',str(program),'-lpng']
p=subprocess.run(command,capture_output=True,text=True,timeout=180);(proof/'compile.stdout').write_text(p.stdout);(proof/'compile.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
pixelProof=[]
for label,path,n in [('counterexample',failedPath,failed),('fixed',nativePath,native)]:
 before=n['renderConfigurationEvidence']['nativeScopeBefore'];root=next(row['geometry'] for row in before['members'] if row['incarnation']==before['scope']['context']['incarnation']);crop=before['crop'];base=path.parent/'private-evidence'
 files=[base/(name+'.png') for name in ['config-shadow-power-one','config-shadow-power-four','config-shadow-power-one-native-output','config-shadow-power-four-native-output']]
 argv=[str(program),*map(str,files),crop['pixelX'],crop['pixelY'],*map(lambda x:str(int(x)),root[:4])]
 p=subprocess.run(argv,capture_output=True,text=True,timeout=5);(proof/(label+'.stdout')).write_text(p.stdout);(proof/(label+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr+p.stdout
 result=json.loads(p.stdout);assert result['passed'];pixelProof.append({'label':label,'argv':argv,'exitCode':p.returncode,'images':{str(p):sha(p) for p in files},'result':result})
roots=[REPO/('implementation/warlock-family-style-revisions-v'+str(v)) for v in range(3,7)]+[REPO/('implementation/warlock-family-style-crop-capture-v'+str(v)) for v in range(3,6)]+[REPO/('implementation/warlock-client-provider-native-v'+str(v)) for v in range(51,56)]
components=[]
for root in roots:
 for path in root.glob('qa/*/report.json'):evidence(path)
 for path in root.glob('qa/preflight.json'):
  for p,h in json.loads(path.read_text())['inputs'].items():assert sha(p)==h,p
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
  if p.is_symlink():assert str(rel).endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[str(rel)]=str(p.readlink());continue
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'localBuildLinks':links,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'actualNativeConfigurationFreshnessQualified':root in [source,nativeRoot]}
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [modelPath,controlsPath,buildPath,originalPath,failedPath,nativePath]},'pixelProof':pixelProof,'pixelOracle':{'command':command,'sha256':sha(program),'sourceSHA256':sha(OUT/'shadow-pixels.cpp')},'nativeControls':len(native['checks']),'retainedOriginalControls':1783,'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeConfigurationFreshnessQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Qualify full shared Elm retained preview label/URI after live source configuration change, then remaining style/config/shader/transform/hardware/output and original preview13/full GUI gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'pixelProof':[p['result'] for p in pixelProof]}))
