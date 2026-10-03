"""Run exactly two independent requested Grok 4.7 audits of frozen local text."""
import concurrent.futures,datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];AUDIT=ROOT/'audits'
packet=(AUDIT/'review-packet.md').read_text();sha=hashlib.sha256(packet.encode()).hexdigest()
focuses={
 'grok-layering':'Native architecture and layering. Evaluate Elm/native boundary, Mutter/KWin adaptation, scene truth, eligibility, fullscreen/MAX/pin/transients/modal families, minimized/inactive surfaces, animation proxies and input targeting. Evaluate GPU acceleration, WebGPU secure-origin/API availability, device loss, native frame import/copies and host selection. Identify specific contradiction/race counterexamples or missing requirements.',
 'grok-delivery':'Complete requirements and execution readiness. Evaluate EARS atomicity/testability, OpenSpec scenarios and traceability, phase dependencies/effort/staffing, source closure and inherited native acceptance, security/assistive technology/IME, hardware/performance budget freezing, package/ABI/recovery/upgrade/rollback and comprehensive architecture study. Identify uncovered user requirements and insufficient gates.'}
def run(name,focus):
 prompt=AUDIT/(name+'-prompt.md')
 pre='''You are an independent Grok 4.7 auditor of an Elm desktop/window-system ROADMAP, not an implementer. The user explicitly requested two independent Grok 4.7 audit sessions. You are one session. Use ONLY read-only tools to inspect the frozen packet and files. Do not edit files, execute code/tests/builds/native commands, make changes, send messages, or claim native testing. The frozen audit material is in local files listed below. Review it adversarially with concrete counterexamples. A future gated implementation and openly unresolved owner/experiment decision is not intrinsically a planning defect. Do not claim to have reviewed all source code: primary-source interpretations and full corpus are available locally; state exactly which source files you inspect.
Return a comprehensive Markdown report with input SHA256, verdict, scope/limitations, findings grouped by severity, then coverage strengths. Every finding needs stable ID, severity critical/high/medium/low, requirement IDs, artifact/heading, concrete defect/counterexample, exact correction and whether it blocks implementation admission. Prefix finding IDs '''+('GRK-L' if name.endswith('layering') else 'GRK-D')+'''. Suggest explicit EARS wording for missing requirements. Do not invent severity to meet a quota. Distinguish user requirements from recommendations. All implementation/native/GPU acceptance is pending.\n\n'''
 prompt.write_text(pre+'Input SHA256: '+sha+'\nFocus: '+focus+'\n\nRead the ENTIRE /home/hoskinson/omarchy-windows-parity/docs/elm-roadmap/audits/review-packet.md in manageable chunks; it is 311106 bytes. Read /home/hoskinson/omarchy-windows-parity/docs/elm-roadmap/audits/draft-manifest.json and frozen draft-packet/ files if needed. Canonical requirements.json contains 181 requirements with scenarios and verification; review all. Current live docs may be revised after audit begins, so report against the frozen packet. You may inspect reference/mutter and reference/kwin primary sources read-only to verify architecture statements. Produce the final report in stdout; do not write files.')
 cmd=['grok','--model','grok-4.7','--no-subagents','--disable-web-search','--permission-mode','plan','--max-turns','60','--prompt-file',str(prompt),'--output-format','plain']
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (AUDIT/(name+'.md')).open('w') as stdout,(AUDIT/(name+'.stderr.txt')).open('w') as stderr:
  p=subprocess.run(cmd,cwd=REPO,stdout=stdout,stderr=stderr,timeout=900)
 result={'modelRequested':'grok-4.7','inputSHA256':sha,'startedUTC':started,'finishedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'command':cmd,'report':str((AUDIT/(name+'.md')).relative_to(REPO)),'reportBytes':(AUDIT/(name+'.md')).stat().st_size,'reportSHA256':hashlib.sha256((AUDIT/(name+'.md')).read_bytes()).hexdigest()}
 (AUDIT/(name+'-execution.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
 results=list(executor.map(lambda item:run(*item),focuses.items()))
raise SystemExit(any(r['exitCode'] or not r['reportBytes'] for r in results))
