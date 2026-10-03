"""Additive independent raw helper archive replay; no native commands."""
from pathlib import Path
import hashlib,json,os
from audit import read,js,digest,gone
B=Path('/home/hoskinson/window-integration-qa/toolkit-held-matrix-v2/attempt-1')
def main():
 variants=js(B/'report.json')['variants'];results=[]
 for variant in variants:
  folder=B/variant['variant']/'terminal-helpers';archive=js(folder/'archive.json');config=read(folder/'helper-config.json');log=read(folder/'helper-events.jsonl');events=[json.loads(row) for row in log.splitlines() if row.strip()]
  exact=hashlib.sha256(config).hexdigest()==archive['configSHA256'] and hashlib.sha256(log).hexdigest()==archive['logSHA256'] and events==archive['events'] and not archive['parseErrors'] and archive['completeEOF'] is True
  results.append(dict(variant=variant['variant'],rawHelperArchiveIntegrity=exact,eventCount=len(events),allArchivedOriginalIdentitiesGone=all(gone(row['identity']) for row in archive['processes']),configSHA256=hashlib.sha256(config).hexdigest(),logSHA256=hashlib.sha256(log).hexdigest(),normalFullHelperLifecycle=False,acceptanceNotInferredFromEmptyJournal=True))
 packet=dict(result='pass' if all(row['rawHelperArchiveIntegrity'] and row['allArchivedOriginalIdentitiesGone'] for row in results) else 'fail',scope='Raw archive integrity only; failed held52 and absent helper lifecycle remain false',variants=results,nativeCommands=False,sourceSHA256=digest(Path(__file__))[0])
 path=B/'root-held-archive-audit-v1.json';fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
 print(json.dumps(dict(result=packet['result'],output=str(path),nativeCommands=False)))
if __name__=='__main__':main()
