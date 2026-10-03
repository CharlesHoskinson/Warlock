"""Additive terminal retirement replay; no producer imports or native commands."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,stat,time
BASE=Path(__file__).resolve().parent.parent/'toolkit-held-terminal-audit-v2/audit.py'
spec=importlib.util.spec_from_file_location('exact_terminal_reader',BASE);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)

def replay(folder,case,expected):
 path=folder/'retirement-observation.json';trace=case['trace']
 before=reader.one(trace,'label','before actual nonrelease interruption')
 after=reader.one(trace,'label','after actual nonrelease interruption')
 row=reader.js(path)
 integrity=(stat.S_IMODE(path.stat().st_mode)==0o600 and not row['errors'] and row['before']==before['native'] and row['publicBefore']==before['public'] and row['after']==after['native'] and row['publicAfter']==after['public'] and row['nativeClientsAfter']==after['nativeClients'] and row['interruptionACK']==after['interruptionACK'] and row['timeNs']==after['timeNs'] and row['timeNs']>=before['timeNs'] and after['observationErrors']==[] and after['observationPath']==str(path) and row['pointerKnownDown']==[expected['button']] and row['after']['signalDownButtonIds']==row['before']['signalDownButtonIds']==[expected['button']])
 focus=reader.one(trace,'label','separate WM focus intervention')['native']
 target=reader.one(trace,'label','actual press')['target'];peer=focus['nativeFocus']
 integrity=bool(integrity and reader.eq(row['target'],target) and reader.eq(row['peer'],peer))
 return dict(evidenceIntegrity=integrity,artifact=str(path),artifactSHA256=reader.digest(path)[0],independentFocusBefore=reader.eq(row['before']['nativeFocus'],peer),independentFocusAfter=reader.eq(row['after']['nativeFocus'],peer),coreRetired=row['after']['coreDragTarget'] is None,groupsPreserved=reader.groups(row['before'])==reader.groups(row['after']),actualRawHoldPreserved=row['after']['signalDownButtonIds']==row['before']['signalDownButtonIds'],producerCaseResult=case['result'],escapeSpecificTheftObserved=reader.eq(row['before']['nativeFocus'],peer) and not reader.eq(row['after']['nativeFocus'],peer) and (expected.get('end')=='escape' or expected.get('name','').endswith('escape')))

def audit(stage,attempt):
 matrix=reader.js(stage/'matrix.json');report=reader.js(attempt/'report.json');frozen=reader.js(stage/'frozen-inputs.json');rows=[]
 closure=all(reader.digest(p)==(h,frozen['inputModes'][p]) for p,h in frozen['inputs'].items()) and all(Path(p).is_symlink() and os.readlink(p)==t for p,t in frozen['symlinks'].items())
 for variant in report['variants']:
  for index,case in enumerate(variant['cases']):
   expected=matrix['casesPerVariant'][index]
   row=dict(variant=variant['variant'],case=case['case'],producerCaseResult=case['result'])
   if case['case']!=expected['name']:raise ValueError('Actual case order mismatch')
   if expected['name']=='genuine-group-release-positive':row['retirementExpected']=False
   elif any(t.get('label')=='after actual nonrelease interruption' for t in case['trace']):
    row['retirementExpected']=True
    try:row.update(replay(attempt/variant['variant']/('case-'+str(index+1)),case,expected))
    except Exception as error:row.update(evidenceIntegrity=False,error=repr(error))
   else:row.update(retirementExpected=True,evidenceIntegrity=False,retirementEvidenceMissing=True)
   rows.append(row)
 actual=[r for r in rows if r.get('artifact')]
 return dict(result='pass' if closure and actual and all(r.get('evidenceIntegrity') is True for r in rows if r['retirementExpected']) else 'fail',fullFrozenBytesModesLinks=closure,sourceManifestSHA256=reader.digest(stage/'frozen-inputs.json')[0],producerResult=report['result'],rows=rows,retainedRetirementCount=len(actual),allReplayedIndependentFocusPreserved=bool(actual) and all(r['independentFocusBefore'] and r['independentFocusAfter'] for r in actual),fullHeld52Accepted=False,nativeCommands=False,mainWrites=False,boundary='Retained retirement evidence and focus attribution only; full workload/genuine input/lifecycle remain independently required',auditorSHA256=reader.digest(Path(__file__))[0],readerSHA256=reader.digest(BASE)[0])

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();attempt=a.attempt.resolve();output=a.output.absolute()
 if attempt.parent!=stage or not attempt.name.startswith('attempt-') or output.parent!=attempt:raise ValueError('Exact owned additive terminal artifact required')
 result=audit(stage,attempt);fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 print(json.dumps(dict(result=result['result'],artifact=str(output),retirements=result['retainedRetirementCount'])));return int(result['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
