"""Prepare exact qualified native126 freeze, preserving all earlier controls."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'docs/warlock-preview/v89/freeze_native126.py';assert not p.exists()
s=(r/'docs/warlock-preview/v88/freeze_native125.py').read_text().replace('warlock-client-provider-native-v125','warlock-client-provider-native-v126').replace('warlock-preview-provider-v88','warlock-preview-provider-v89').replace('docs/warlock-preview/v88/','docs/warlock-preview/v89/').replace("len(proof['checks'])==2464","len(proof['checks'])==2465")
marker='files={}\n';assert s.count(marker)==1
extra="""prior125=json.loads(pathlib.Path(preflight['retainedNative125Report']).read_text());comparison125=audit.compare(prior125,proof,stable)
assert comparison125['fixedOrderedControls']==2457
assert any(row['name']=='allPriorNative125FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison125 for row in proof['checks'])
for field in ['asynchronousRetirementReport','asynchronousRefinementReport','asynchronousElmMutantReport']:
 evidence=pathlib.Path(gui[field]);checked=json.loads(evidence.read_text());assert checked['passed']
 for rel,value in checked['inputs'].items():
  file=pathlib.Path(rel);file=file if file.is_absolute() else provider.parent/file;assert sha(file)==value,rel
 for rel,value in checked['artifacts'].items():assert sha(evidence.parent/rel)==value,rel
"""
s=s.replace(marker,extra+marker)
marker="(repo/'docs/warlock-preview/v89/report.json').write_text";assert s.count(marker)==1
s=s.replace(marker,"report.update(prior125FixedOrderedControls=2457,asynchronousRetirementControls=9,asynchronousRetirementScenarios=10,asynchronousRetirementTraces=30,asynchronousRetirementStates=641,unsafeAsynchronousModelMutants=3,unsafeAsynchronousElmMutants=3,next='Qualified exact GUI89/native126/core16/plugin18, preserving every original125 gate. Fresh GUI90 implements retained observation/readiness/completion journal and zero-floor encoding; compile and couple actual C/native/Elm delivery, then continuing >256 real native/Elm turnover, ordinary capture and all original GUI release gates. PUBLIC62 8e68d74 and receiptb3a539 remain verified; publish current qualified slice separately from mutable GUI90.')\n"+marker)
marker="sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop";assert s.count(marker)==1
s=s[:s.index(marker)]+"""sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),
 ['PROGRESS native126 exact currentGUI89/core16/plugin18 PASS2465/277normalclean/all2457prior125fixed; original allocator trials and deadlines unchanged. Full95/original12/C96/decoder13-25-439states-3mutants/aggregate9068through280synthetic/Elm33/Cprefix7-15-180states-3mutants/adapter10 plus asynchronous10selected/30actualElmtraces/641state-command comparisons/3model/3compiledElm mutants held. PUBLIC62 8e68d74 receiptb3a539 verified. FreshGUI90 native retained observation/readiness/completion C APIs and zero-floor encoder fix building10402; transport journal synthetic280controls passed its first standalone scope. Native/Elm final routing, completion delivery, real >256native/Elm turnover, ordinary capture and all original release gates remain.'],
 'progress',[str(manifest.relative_to(repo)),'docs/warlock-preview/v89/report.json']))
"""
ast.parse(s);p.write_text(s)
