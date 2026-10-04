"""Identity-checked /proc process-tree calibration; never infer unavailable PSS."""
import os,time,math
from pathlib import Path
HZ=os.sysconf('SC_CLK_TCK')
def stat(pid):
 raw=Path(f'/proc/{pid}/stat').read_text();name=raw[raw.index('(')+1:raw.rindex(')')];fields=raw[raw.rindex(')')+2:].split()
 return {'pid':pid,'name':name,'ppid':int(fields[1]),'start':fields[19],'cpuTicks':int(fields[11])+int(fields[12])}
def sample_tree(pid,expected_start):
 parent=stat(pid);assert parent['start']==expected_start
 rows={}
 for entry in Path('/proc').iterdir():
  if not entry.name.isdecimal():continue
  try:rows[int(entry.name)]=stat(int(entry.name))
  except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 owned={pid};changed=True
 while changed:
  prior=len(owned);owned|={key for key,row in rows.items() if row['ppid'] in owned};changed=len(owned)!=prior
 processes=[]
 for key in sorted(owned):
  try:
   before=rows[key];status=Path(f'/proc/{key}/status').read_text().splitlines();values={line.split(':')[0]:line.split(':',1)[1].strip() for line in status if ':' in line}
   row={**before,'rssKiB':int(values.get('VmRSS','0 kB').split()[0]),'threads':int(values['Threads']),'voluntarySwitches':int(values['voluntary_ctxt_switches']),'involuntarySwitches':int(values['nonvoluntary_ctxt_switches'])}
   try:
    rollup=Path(f'/proc/{key}/smaps_rollup').read_text().splitlines();memory={line.split(':')[0]:int(line.split(':',1)[1].split()[0]) for line in rollup if ':' in line}
    row['pssKiB']=memory['Pss'];row['privateKiB']=memory['Private_Clean']+memory['Private_Dirty']
   except (PermissionError,FileNotFoundError,ProcessLookupError) as error:row['privateMemoryUnavailable']=type(error).__name__
   assert stat(key)['start']==before['start'];processes.append(row)
  except (FileNotFoundError,ProcessLookupError):continue
 assert stat(pid)['start']==expected_start
 return {'monotonicNs':time.monotonic_ns(),'host':{'pid':pid,'start':expected_start},'processes':processes,'processCount':len(processes),'rssKiB':sum(row['rssKiB'] for row in processes),'cpuTicks':sum(row['cpuTicks'] for row in processes),'hz':HZ,'pssComplete':all('pssKiB' in row for row in processes),'pssKiB':sum(row.get('pssKiB',0) for row in processes)}
def quantiles(values):
 ordered=sorted(values)
 return {'count':len(values),**{name:ordered[max(0,math.ceil(fraction*len(ordered))-1)] for name,fraction in [('p50',.5),('p95',.95),('p99',.99)]}}
def summary(samples):
 first,last=samples[0],samples[-1];elapsed=(last['monotonicNs']-first['monotonicNs'])/1e9
 # Aggregate CPU deltas only for identities that survive the interval.
 a={(p['pid'],p['start']):p for p in first['processes']};b={(p['pid'],p['start']):p for p in last['processes']};common=set(a)&set(b)
 ticks=sum(b[key]['cpuTicks']-a[key]['cpuTicks'] for key in common)
 return {'elapsedSeconds':elapsed,'survivingIdentityCpuPercentOneCore':100*ticks/HZ/elapsed,'cpuIdentityCoverageComplete':set(a)==set(b),'rssKiB':quantiles([s['rssKiB'] for s in samples]),'processCount':quantiles([s['processCount'] for s in samples]),'rssGrowthKiB':last['rssKiB']-first['rssKiB'],'pssComplete':all(s['pssComplete'] for s in samples)}
