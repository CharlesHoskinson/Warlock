#!/usr/bin/python3
"""Review and freeze the one-expression overlap oracle correction."""
import datetime, importlib.util, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
Q=Path('/home/hoskinson/window-integration-qa');B=Q/'pin-max-native-campaign-b-v4';P=Q/'pin-max-native-campaign-b-v3'
sys.path.insert(0,str(Q));from qa_launch import require_qa_scope
scope=require_qa_scope()
spec=importlib.util.spec_from_file_location('root_pin_review',Q/'review_pin_campaign_b_controller_v1.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
sha=review.digest
assert sha(B/'SOURCE_READY.json')=='00b6838a19af63de49397c17de2b46f3fe5d18fdf687e18b57ce17279ac436d7'
assert sha(B/'SOURCE_INPUTS.json')=='37f5b4f000343d09aff88a7f65e95ef78e7d8b7433953cc0bbcd8628860eb856'
packet=json.loads((B/'SOURCE_INPUTS.json').read_bytes());review.verify(packet)
parent=json.loads((P/'frozen-inputs.json').read_bytes());review.contains(packet,parent)
sys.path.insert(0,str(B));import overlap_source_check, capture_overlap_packet as capture
assert overlap_source_check.verify()==json.loads((B/'overlap-source-conservation.json').read_bytes())
old=(P/'controller/minimal_controller.py').read_text();new=(B/'controller/minimal_controller.py').read_text()
operand="peer_box=self.qt_box(actor,'peer',peer)"
assert new.count(operand)==1 and new.replace(operand,"peer_box=peer_max['body']['visualBox']",1)==old
oldpair=json.loads((P/'PAIR_READY.json').read_bytes());pair=json.loads((B/'PAIR_READY.json').read_bytes())
for key,value in oldpair.items():
    if key in ['inputs','inputModes']:assert all(pair[key].get(k)==v for k,v in value.items())
    else:assert pair[key]==value,key
inherited=(B/'overlap-inherited19-cpu.log').read_text()
assert 'Ran 19 tests' in inherited and inherited.rstrip().endswith('OK')
audit=Q/'pin-max-native-b-v3-overlap-audit-v1'
assert sha(audit/'audit.json')=='78627cfd1bac109fa8bc1abac5df489b107df18653986c9e30c5749c32752c0b'
focused=(audit/'overlap-proposal-cpu.log').read_text()
assert 'Ran 4 tests' in focused and focused.rstrip().endswith('OK')
assert sha(audit/'test_overlap_proposal.py')=='9a47d6c32d6148ca46d7ae5fad0979e03b410f97fba57503657bbf15d3c9133b'
out=Q/'pin-max-native-b-v4-root-source-review-v1.json'
result=dict(result='pass',schema='root-pin-b-overlap-v4-review-v1',scope=scope,
    observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceReadySHA256=sha(B/'SOURCE_READY.json'),
    files=len(packet['inputs']),fullFrozenParent=len(parent['inputs']),allBytesModesLinksDirectoriesMatch=True,
    wholeControllerInverseExact=True,inherited19TestsExactAndPassed=True,fourWholeBodyCPUAdaptersPassed=True,
    reviewed='Complete one-expression diff, actual-current Qt button geometry path, complete controller inverse, four source-bound CPU adapters, full source/raw ancestry and pair conservation.',
    approved='Freeze exact complete union; frozen preflight; one serial private B01-B12 attempt.',
    productChanged=False,nativeExecuted=False,fullCampaignBAccepted=False,fullParityAccepted=False)
capture.publish(out,result)
row=capture.inventory()
for p in [out,Path(__file__).resolve(),Q/'pin-max-native-b-v4-source-preflight.json']:
    w=capture.meta(p);row['inputs'][str(p)]=w['sha256'];row['inputModes'][str(p)]=w['mode']
review.contains(row,packet);review.verify(row)
capture.publish(B/'frozen-inputs.json',row)
print(json.dumps(dict(result='pass',reviewSHA256=sha(out),manifestSHA256=sha(B/'frozen-inputs.json'),files=len(row['inputs']),links=len(row['symlinks']),nativeExecuted=False)))
