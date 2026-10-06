"""Generate exact current GUI freeze, retaining asynchronous failures and proofs."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'docs/warlock-preview/v89/hold89.py';assert not p.exists()
s=(r/'docs/warlock-preview/v88/hold88.py').read_text().replace('warlock-preview-provider-v88','warlock-preview-provider-v89').replace('docs/warlock-preview/v88/','docs/warlock-preview/v89/').replace('GUI88','GUI89').replace('native125','native126')
marker='files = {}\n';assert s.count(marker)==1
extra="""async_path=only('qa/retirement-async-check-*/report.json');asynchronous=verify(async_path);assert asynchronous['evidence']['checks']==9
refine_path=only('qa/retirement-refinement-check-v2-*/report.json');refinement=verify(refine_path)
assert refinement['namedScenarios']==10 and refinement['invariantSamples']==300 and refinement['unsafeModelMutantsDetected']==3
assert len(refinement['evidence']['coupledTraces'])==30 and refinement['evidence']['statesCompared']==641
mutant_path=only('qa/retirement-elm-mutations-*/report.json');mutations=verify(mutant_path);assert mutations['unsafeCompiledElmMutantsDetected']==3
assert all(row['compiled'] and row['observableMismatch'] for row in mutations['mutants'])
ancestor=only('qa/retirement-async-ancestor88-*/report.json');old=json.loads(ancestor.read_text())
assert not old['passed'] and 'Exact delayed completion' in old['error']
failed_refinement=only('qa/retirement-refinement-check-[0-9]*/report.json');failed=json.loads(failed_refinement.read_text())
assert not failed['passed'] and 'premature-removal' in failed['error']
reports.update(asynchronousRetirementReport=str(async_path),asynchronousRefinementReport=str(refine_path),asynchronousElmMutantReport=str(mutant_path),retainedAncestor88Counterexample=str(ancestor),retainedRefinementWitnessFailure=str(failed_refinement))
"""
s=s.replace(marker,extra+marker)
old="'elmRetirementControls':33,"
new="'asynchronousRetirementControls':9,'asynchronousRetirementScenarios':10,'asynchronousRetirementTraces':30,'asynchronousRetirementStates':641,'unsafeAsynchronousModelMutants':3,'unsafeAsynchronousElmMutants':3,"+old
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('Real WebKit/native retirement activation, captured physical retirement','Independent sibling observations/completions pass9 compiled controls and10 explicit selected Quint scenarios/30 coupled traces/641 observed state-and-command comparisons; three exact named model mutants and three separately compiled Elm mutants detected. Shared cutoff admission witnesses stay monotone. Real WebKit/native retirement activation, captured physical retirement')
s=s.replace('Native retirement observation/readiness/completion routing and real continuing native/Elm turnover remain unqualified','Independent sibling delivery qualified10/30/641 with3 model and3 compiled Elm mutants; native retirement observation/readiness/completion routing and real continuing native/Elm turnover remain unqualified')
ast.parse(s);p.write_text(s)
