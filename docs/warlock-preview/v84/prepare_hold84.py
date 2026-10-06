"""Derive the existing full provider freeze contract with the two new boundaries."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v82/hold81.py').read_text()
text=text.replace('GUI81','GUI84').replace('warlock-preview-provider-v81','warlock-preview-provider-v84').replace('docs/warlock-preview/v82/','docs/warlock-preview/v84/')
marker='evidence = {}\n';assert text.count(marker)==1
extra='''retirement_path = only('qa/retirement-decoder-check-*/report.json')
retirement = verify(retirement_path)
assert retirement['namedScenarios'] == 13 and len(retirement['coupledTraces']) == 25
assert retirement['statesCompared'] == 439 and retirement['unsafeMutantsDetected'] == 3
assert retirement['fullBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}
reports['retirementDecoderReport'] = str(retirement_path)
c_path = only('qa/retirement-c-check-*/report.json')
c = verify(c_path)
assert [row['mode'] for row in c['controls']] == ['valid','retired','bad-clock','bad-request','regress']
assert c['checks'] == sum(row['checks'] for row in c['controls'])
assert c['fullBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}
reports['retirementCReport'] = str(c_path)
'''
text=text.replace(marker,extra+marker)
text=text.replace('Same-host third picker lease/native image/ACK qualification remains open;', 'Current authenticated native retirement decoder13/25/439states/3mutants and actual C/socket receiver/ownership controls pass. Real typed C/native retirement path and atomic actor turnover remain open;')
text=text.replace('Qualify expired unissued resume on a third actual picker lease in native117; preserve all116 stable controls, then continue actor/history retirement, ordinary capture and original release gates.', 'Qualify current GUI84/native122 typed C retirement observations on core16/plugin18, preserving all original native121 runtime identities/deadlines, then atomic actor/history retirement beyond256, ordinary capture and all original release gates.')
text=text.replace('Native third lease117 next.', 'Typed retirement decoder and C/socket suites passed; actual native122 next. Actor turnover is not accepted.')
target=pathlib.Path(__file__).parent/'hold84.py';assert not target.exists();target.write_text(text)
print(target)
