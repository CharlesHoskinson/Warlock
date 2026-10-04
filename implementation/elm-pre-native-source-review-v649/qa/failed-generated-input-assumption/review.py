import ast,hashlib,json,os,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent
GUI=BASE/'elm-recovery-delivery-integrated-gui-v640';P630=BASE/'elm-recovery-delivery-integration-v630';P642=BASE/'elm-informational-history-drain-v642';P626=BASE/'elm-reconciliation-startup-order-v626';P641=BASE/'elm-native-lost-release-preparation-v641';CORE=BASE/'elm-grant-retirement-runtime-v595'
checks=[];pins={};notes=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,b):checks.append({'name':n,'passed':bool(b)});assert b,n
def pin(p,h=None):p=pathlib.Path(p);d=sha(p);check('pin:'+str(p),h is None or d==h);pins[str(p)]={'sha256':d,'size':p.stat().st_size};return d
for parent in [P630,P642,P626,P641]:
 manifest=parent/'component-manifest.json';pin(manifest);m=json.loads(manifest.read_text());files=m['files'];files=files.items() if isinstance(files,dict) else [(r['path'],r) for r in files]
 for n,v in files:pin(parent/n,v['sha256'])
for directory in ['adapter','native']:
 expected={str(p.relative_to(P630)) for p in (P630/directory).rglob('*') if p.is_file()};actual={str(p.relative_to(GUI)) for p in (GUI/directory).rglob('*') if p.is_file()};check('inventory630-'+directory,expected==actual)
 for n in expected:check('actual640-equals630:'+n,pin(GUI/n)==sha(P630/n))
expected={p.name for p in (P630/'src').glob('*.elm')};check('frontend640-exact-module-inventory',{p.name for p in (GUI/'src').glob('*.elm')}==expected)
for n in expected:
 parent=P642 if n in ['ReconciliationTracking.elm','SurfaceController.elm'] else P626
 check('frontend-parent-selection:'+n,pin(GUI/'src'/n)==sha(parent/'src'/n))
for p in (P626/'assets').glob('*'):
 if p.is_file():check('asset626:'+p.name,pin(GUI/'assets'/p.name)==sha(p))
check('strict-decoder-not-weakened',sha(GUI/'src/ReconciliationFrame.elm')==sha(P642/'src/ReconciliationFrame.elm'))
pointer=GUI/'qa/current-build.json';pin(pointer);buildpath=pathlib.Path(json.loads(pointer.read_text())['report']);pin(buildpath);build=json.loads(buildpath.read_text());check('selected640-build-passed',build['passed'])
for n,h in build['inputs'].items():
 pin(buildpath.parent/'inputs'/n,h)
 if sha(GUI/n)!=h and n.startswith('qa/'):notes.append({'kind':'postbuild-QA-source','path':n,'builtSHA256':h,'currentSHA256':sha(GUI/n)})
 else:pin(GUI/n,h)
pin(buildpath.parent/'elm-host',build['binarySHA256'])
for n,h in build['artifacts'].items():pin(buildpath.parent/n,h)
for group in ['compilerDependencies','tools','linkedLibraries']:
 for n,row in build[group].items():pin(n,row['sha256']);check('resolved:'+n,str(pathlib.Path(n).resolve())==row['resolved'])
check('all-build-commands-success',all(r['exitCode']==0 for r in build['commands']))
for main in ['Main','Bar','Popup']:check('optimized-'+main,any(r['command'][0]=='npm' and 'src/'+main+'.elm' in r['command'] and '--optimize' in r['command'] for r in build['commands']))
for label,count in [('tests-1791153820316433749',51),('drain-1791153891368556594',21),('controls-1791153924910941912',20)]:
 p=GUI/'qa'/label/'report.json';pin(p);r=json.loads(p.read_text());check('actual640-'+label,r['passed'] and len(r['checks'])==count)
 if label.startswith('tests'):
  for n,h in r['sourceSHA256'].items():pin(GUI/'src'/n,h);pin(p.parent/'inputs/src'/n,h)
 if label.startswith('drain'):
  for n,h in r['frontendSourceHashes'].items():pin(GUI/'src'/n,h)
  for n,h in r['sourceHashes'].items():pin(n,h)
 if label.startswith('controls'):check('actual640-six-compiled-targeted-mutants',len(r['compiledControls'])==6 and all(v['detected'] for v in r['compiledControls']))
pairpath=CORE/'qa/build-pair-manifest.json';pin(pairpath);pair=json.loads(pairpath.read_text());check('native-owning-pair-passed',pair['passed'])
for n,h in pair['files'].items():pin(CORE/n,h)
for n,row in pair['nativePair'].items():pin(row['path'],row['sha256'])
for n in ['owningAcceptance','producerEvidence','keyboardAcceptance','owningCoreComponent']:pin(pair[n],pair[n+'SHA256'])
descriptor=json.loads((CORE/'native-build-report.json').read_text());pin(CORE/'native-build-report.json');pin(descriptor['pluginBuildReport'],descriptor['pluginBuildReportSHA256']);native=json.loads(pathlib.Path(descriptor['pluginBuildReport']).read_text());check('plugin-built-for-selected-core',native['passed'] and native['core']['sha256']==pair['nativePair']['core']['sha256'])
for group in ['dependencies','linkedLibraries']:
 for n,h in native[group].items():pin(n,h)
manifest641=json.loads((P641/'component-manifest.json').read_text());check('641-25-controls-preparation-only',manifest641['checks']==25 and not(manifest641['nativeLaunched']))
for n,target in manifest641['intentionalUnsafeFixtureSymlinks'].items():check('641-retained-unsafe-fixture:'+n,os.readlink(P641/n)==target)
old=ast.parse((BASE/'elm-reconciliation-native-journey-v627/qa/regression.py').read_text());new=ast.parse((P641/'qa/runner.py').read_text())
for n in ['wait','click']:
 a=next(v for v in ast.walk(old) if isinstance(v,ast.FunctionDef) and v.name==n);b=next(v for v in ast.walk(new) if isinstance(v,ast.FunctionDef) and v.name==n);check('unchanged-pointer-deadline-AST:'+n,ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False))
notes.append({'kind':'bounded-toolchain-provenance','detail':'Build pins C compiler/tools/header/library inputs and generated optimized Elm outputs. npm elm@0.19.2-0 command version recorded, but exact Elm compiler binary and Elm package-source dependency hashes not separately captured; no full toolchain reproducibility claim.'})
notes.append({'kind':'native-status','detail':'No native execution by649; new coherent640/641 acceptance and source-bound future646 preflight required. Original626 135/473 acceptance not transferred.'})
r={'passed':True,'verdict':'ready-for-reviewed-native-preflight','checks':len(checks),'rows':checks,'pins':pins,'notes':notes,'nativeAcceptance':False,'mainDesktopActions':False,'newBuildOrBehaviorExecution':False,'scope':'New read-only byte/source/artifact/tool/library/owningABI verification; existing reports reviewed, not rerun'};(ROOT/'qa/report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'pins':len(pins),'notes':notes}))
