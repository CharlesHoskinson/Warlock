"""Publish exact-version explicit votes; retain all previous evidence."""
from pathlib import Path
import collections,hashlib,json
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
request=json.loads((ROOT/'request.json').read_text());ballot=json.loads((ROOT/'candidates-v3.json').read_text());votes=[]
for r in request['reviewers']:
 raw=(ROOT/'ratification'/(r['id']+'.md'))
 out=ROOT/'ratification'/(r['id']+'.votes.json')
 if not out.exists():
  s=raw.read_text().strip()
  if s.startswith('```'):s=s.split('\n',1)[1].rsplit('```',1)[0].strip()
  v=json.loads(s);out.write_text(json.dumps(v,indent=2)+'\n')
 v=json.loads(out.read_text());assert v['reviewer']==r['id'];assert v['ballotSHA256']==sha(ROOT/'candidates-v2.json');assert v['philosophySHA256']==sha(ROOT/'PHILOSOPHY-V2.md');assert v['remainingWorkSHA256']==sha(ROOT/'remaining-work-v2.json');assert len(v['votes'])==30;votes.append(v)
amendments=[]
for r in request['reviewers']:
 out=ROOT/'amendment'/(r['id']+'.votes.json')
 if not out.exists():
  v=json.loads((ROOT/'amendment'/(r['id']+'.md')).read_text());out.write_text(json.dumps(v,indent=2)+'\n')
 a=json.loads(out.read_text());assert a['reviewer']==r['id'];assert a['finalBallotSHA256']==sha(ROOT/'candidates-v3.json');assert a['previousBallotSHA256']==sha(ROOT/'candidates-v2.json');assert a['decision']=='accept' and a['carryForwardUnchangedVotes'];amendments.append(a)
matrix=[]
for r in ballot['requirements']:
 decisions={v['reviewer']:('accept' if r['id']=='ELM-ADOPT-030' else next(x['decision'] for x in v['votes'] if x['id']==r['id'])) for v in votes}
 ok=all(x=='accept' for x in decisions.values()) if r['id']!='ELM-ADOPT-015' else all(x in ['accept','defer'] for x in decisions.values())
 matrix.append({'id':r['id'],'title':r['title'],'decisions':decisions,'converged':ok,'disposition':'deferred conditional export' if r['id']=='ELM-ADOPT-015' else 'accepted draft refinement'})
assert all(r['converged'] for r in matrix)
assert all(v['philosophy']['decision']=='accept' and v['remainingWork']['decision']=='accept' for v in votes)
result={'schema':1,'status':'ten-reviewer explicit draft consensus','ballotSHA256':sha(ROOT/'candidates-v3.json'),'previousBallotSHA256':sha(ROOT/'candidates-v2.json'),'amendments':amendments,'philosophySHA256':sha(ROOT/'PHILOSOPHY-V2.md'),'remainingWorkSHA256':sha(ROOT/'remaining-work-v2.json'),'originalProposals':53,'draftRequirements':30,'draftScenarios':67,'acceptedRefinements':29,'deferredConditional':['ELM-ADOPT-015'],'matrix':matrix,'votes':votes,'nativeAcceptance':False,'baselineAmended':False,'name':'Aletheia (working editorial proposal, not technical unanimity)'}
(ROOT/'CONSENSUS.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Ten-reviewer consensus','','Five Sol6.1 and five actual Opus5.5/high reviewers researched independently, cross-reviewed the first ballot, requested corrections and explicitly ratified the corrected ballot. All29 core contracts converge as guarded draft refinements. Local diagnostic export015 stays deferred and conditional. Acceptance of a conditional contract is not selection of its mechanism.','','The53 original proposals, first30/60 ballot, all first votes, corrected30/67 ballot, final ten votes and all ten explicit endorsements of the single030 scenario correction remain preserved. changes-v1-v2.json records the actual field differences; correction-ledger.json explains resolutions. No agreement is inferred from silence.','','All ten ratified the philosophy and remaining-work audit. Aletheia is a working name proposed in response to the user; reviewers agreed with design fidelity, not a claim of universal naming preference.','','| ID | Final disposition | Votes |','| --- | --- | --- |']
for r in matrix:
 counts=collections.Counter(r['decisions'].values());lines.append('| '+r['id']+' | '+r['disposition']+' | '+', '.join(str(n)+' '+k for k,n in sorted(counts.items()))+' |')
lines+=['','## Corrections that changed the plan','','- Malformed or unauthorized events produce bounded rejection diagnostics; they cannot fabricate terminal Refused outcomes.','- Valid authenticated historical receipts can reconcile retained Unknown without authorizing a new binding or renewing a deadline.','- Native protocol-specific evidence and commit validation govern effect dependencies.','- Replay/refinement includes commands, retained obligations and every concrete field, with explicit reviewed abstractions.','- Presentation, physical cleanup, source liveness and frame freshness are separate claims.','- Focused native AT identity governs activation; stable semantics and one announcement owner are qualified separately.','- Preview latest-content demand needs both bounded retention and a frozen pacing policy.','- Original baseline scope, deadlines, keyboard delivery phase and package gates remain unchanged.','','## Remaining work and limits','','The release audit maps all242 original requirements/417 scenarios to S01–S16 and optional C00–C06, preserving every original EARS/scenario string. Mandatory230/405 and optional12/12 remain separate. Right-click24/48 remains additive. Twenty-four closure contracts clarify acceptance, not24 new product features. All12 existing work items and44 earlier findings are crosswalked.','','These are research and specification results. Production provider integration, native preview13, restore38/recovery34 with their original deadlines, drag/resize52, hardware, native AT/IME, resources and a coherent reversible release remain open. There is no native acceptance or baseline amendment in this packet.']
(ROOT/'CONSENSUS.md').write_text('\n'.join(lines)+'\n')
request['status']='research, cross-review, corrections and exact-version ten-reviewer ratification complete; draft integration and implementation remain';request['consensusPolicy']='Independent research, explicit cross-review, corrected exact-version ratification and unanimous one-scenario amendment; dissent retained in earlier votes.'
(ROOT/'request.json').write_text(json.dumps(request,indent=2)+'\n')
print(json.dumps({'status':result['status'],'requirements':30,'scenarios':67,'accepted':29,'deferred':1}))
