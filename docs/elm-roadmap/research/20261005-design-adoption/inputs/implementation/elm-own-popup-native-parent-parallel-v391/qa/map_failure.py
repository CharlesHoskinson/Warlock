"""Archive exact guard exception bytes; no /proc read or causal attribution."""
import hashlib,json,pathlib,re
from join import Refused

def archive(error,directory,*,pid,start):
 evidence=getattr(error,'map_evidence',None)
 if evidence is None:return None
 if type(evidence) is not dict or set(evidence)!={'pid','start','mapsSHA256','raw'}:raise Refused('closed same-read maps diagnostic')
 if type(start) is str:
  if not re.fullmatch('[1-9][0-9]{0,19}',start) or int(start)>=2**64:raise Refused('canonical owned process start')
  start=int(start)
 if type(pid) is not int or type(start) is not int or not 1<=pid<2**31 or not 1<=start<2**64:raise Refused('expected private core PID/start')
 if type(evidence['pid']) is not int or type(evidence['start']) is not int or evidence['pid']!=pid or evidence['start']!=start:raise Refused('same-read requested owner mismatch')
 raw=evidence['raw'];digest=evidence['mapsSHA256']
 if type(raw) is not bytes or not 0<=len(raw)<=4*1024*1024+1 or type(digest) is not str or not re.fullmatch('[0-9a-f]{64}',digest) or hashlib.sha256(raw).hexdigest()!=digest:raise Refused('bounded hash-bound original maps bytes')
 directory=pathlib.Path(directory);directory.mkdir(mode=0o700,exist_ok=False)
 with (directory/'maps.raw').open('xb') as f:f.write(raw)
 metadata={'pid':pid,'start':start,'mapsSHA256':digest,'bytes':len(raw),'sameRead':True,'completeMapsProven':False,'extent':'exact inspected bytes; may be a bounded detection prefix','nativeAcceptance':False,'interpretation':'diagnostic bytes of failing read; no causal attribution'}
 with (directory/'record.json').open('x') as f:json.dump(metadata,f,indent=2);f.write('\n')
 return metadata
