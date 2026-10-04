#!/usr/bin/python3
import hashlib,json,pathlib,subprocess,time,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/f'mutations-{time.time_ns()}';out.mkdir(mode=0o700);journal=(ROOT/'inputs/journal.py').read_text();actor=(ROOT/'inputs/actor.py').read_text();suite=(ROOT/'qa/test.py').read_text()
 controls=[('skipped-event',journal.replace('seq!=last+1','seq<=last'),actor),('missing-map-binding',journal.replace("('mapGeneration',map_generation,2**63-1),",''),actor),('missing-raw-kind',journal.replace("if integer(row.get('rawEventType'),0,2**31-1)!=integer(event_types[event],0,2**31-1):","if False:"),actor),('filtered-negative-delivery',journal.replace("r['event'] in ('button-press','button-release')]","r['event'] in ('button-press','button-release') and r.get('role')==role]",1),actor),('local-normalexit-only',journal,actor.replace("if not terminal.endswith(b'\\n') or not self.rows or self.rows[-1]['event']!='normalexit' or sum(r['event']=='normalexit' for r in self.rows)!=1 or self.process.returncode!=0:","if self.process.returncode!=0 or not any(r['event']=='normalexit' for r in self.rows):"))]
 report={'passed':False,'nativeAcceptance':False,'sourceInputs':{'journal.py':sha(ROOT/'inputs/journal.py'),'actor.py':sha(ROOT/'inputs/actor.py'),'suite':sha(ROOT/'qa/test.py')},'controls':[]}
 try:
  for name,j,a in controls:
   assert (j,a)!=(journal,actor),name;directory=out/name;(directory/'inputs').mkdir(parents=True);(directory/'qa').mkdir();(directory/'inputs/journal.py').write_text(j);(directory/'inputs/actor.py').write_text(a);(directory/'qa/test.py').write_text(suite)
   p=subprocess.run(['/usr/bin/python3','-B',str(directory/'qa/test.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8);(directory/'stdout').write_bytes(p.stdout);(directory/'stderr').write_bytes(p.stderr)
   selected=sorted((directory/'qa').glob('characterization-*/report.json'))[-1];r=json.loads(selected.read_text());failed=[row for row in r['cases'] if not row['matched']]
   assert p.returncode!=0 and failed,name
   report['controls'].append({'name':name,'rejected':True,'exit':p.returncode,'report':str(selected),'reportSHA256':sha(selected),'failingOracle':failed[0]['name'],'actualClassification':failed[0]['classification']})
  report['passed']=True
 except Exception as e:report['error']=repr(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'controls':len(report['controls']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
