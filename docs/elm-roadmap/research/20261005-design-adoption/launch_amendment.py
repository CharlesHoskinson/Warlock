"""Run five explicitly requested, tool-restricted Opus reviews and retain provenance."""
import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--round',choices=['research','consensus','ratification','amendment'],default='research');args=parser.parse_args()
req=json.loads((ROOT/'request.json').read_text());manifest=json.loads((ROOT/'source-manifest.json').read_text());cli=shutil.which('claude');assert cli
outdir=ROOT/args.round;outdir.mkdir(exist_ok=True)
def verify():
 for rel,row in manifest['files'].items():assert hashlib.sha256((ROOT/'inputs'/rel).read_bytes()).hexdigest()==row['sha256'],rel
verify();rows=[];children=[]
def persist():
 report={'schema':1,'round':args.round,'modelRequested':'claude-opus-5-5','effortRequested':'high','cli':cli,'cliSHA256':hashlib.sha256(pathlib.Path(cli).resolve().read_bytes()).hexdigest(),'sourceManifestSHA256':hashlib.sha256((ROOT/'source-manifest.json').read_bytes()).hexdigest(),'reviewers':rows,'allTerminal':len(rows)==5 and all(r['status']=='terminal' for r in rows),'inputBytesVerified':True}
 tmp=outdir/'opus-execution.json.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(outdir/'opus-execution.json')
for reviewer in req['reviewers']:
 if reviewer['family']!='opus':continue
 name=reviewer['id'];prompt=ROOT/(name+'.prompt.txt') if args.round=='research' else outdir/(name+'.prompt.txt')
 assert prompt.is_file()
 cmd=[cli,'--print','--model','claude-opus-5-5','--effort','high','--output-format','stream-json','--verbose','--safe-mode','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--permission-mode','dontAsk','--permission-prompts','none','--tools','Read,Glob,Grep,WebFetch,WebSearch','--allowedTools','Read,Glob,Grep,WebFetch,WebSearch','--no-chrome']
 cmd+=['--session-id',reviewer['sessionId']] if args.round=='research' else ['--resume',reviewer['sessionId']]
 out=open(outdir/(name+'.stream.jsonl'),'wb');err=open(outdir/(name+'.stderr'),'wb')
 proc=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.PIPE,stdout=out,stderr=err)
 row={'id':name,'sessionIdRequested':reviewer['sessionId'],'pid':proc.pid,'startTimeTicks':pathlib.Path(f'/proc/{proc.pid}/stat').read_text().rsplit(')',1)[1].split()[19],'status':'running','command':cmd,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 rows.append(row);children.append((proc,out,err,row));proc.stdin.write(prompt.read_bytes());proc.stdin.close();persist();print(name,'launched',proc.pid,flush=True)
while any(r['status']=='running' for r in rows):
 for proc,out,err,row in children:
  if row['status']=='terminal':continue
  code=proc.poll()
  if code is None:continue
  out.close();err.close();row.update(status='terminal',exitCode=code,finishedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
  messages=[]
  for line in (outdir/(row['id']+'.stream.jsonl')).read_text().splitlines():
   try:messages.append(json.loads(line))
   except json.JSONDecodeError:pass
  initial=[m for m in messages if m.get('type')=='system' and m.get('subtype')=='init'];results=[m for m in messages if m.get('type')=='result']
  row['modelObserved']=initial[-1].get('model') if initial else None
  if results:
   result=results[-1];row.update(resultSubtype=result.get('subtype'),isError=result.get('is_error'),modelUsage=result.get('modelUsage',{}),sessionIdObserved=result.get('session_id'),permissionDenials=result.get('permission_denials',[]))
   (outdir/(row['id']+'.result.json')).write_text(json.dumps(result,indent=2)+'\n');(outdir/(row['id']+'.md')).write_text(result.get('result','')+'\n')
  row['passed']=code==0 and row['modelObserved']=='claude-opus-5-5' and bool(results) and not results[-1].get('is_error',True)
  verify();persist();print(row['id'],'terminal',code,'model',row['modelObserved'],'passed',row['passed'],flush=True)
 time.sleep(1)
verify();persist();raise SystemExit(not all(r.get('passed') for r in rows))
