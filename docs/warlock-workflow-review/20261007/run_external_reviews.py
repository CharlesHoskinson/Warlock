"""Run one read-only reviewer at a time per requested external model family."""
import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,time
O=pathlib.Path(__file__).parent;parser=argparse.ArgumentParser();parser.add_argument('family',choices=['grok','opus']);a=parser.parse_args()
request=json.loads((O/'request.json').read_text());model=request['models'][a.family];cli=shutil.which('grok' if a.family=='grok' else 'claude');assert cli
manifest=json.loads((O/'source-manifest.json').read_text())
def verify():
 for name,row in manifest['files'].items():assert hashlib.sha256((O/'inputs'/name).read_bytes()).hexdigest()==row['sha256'],name
rows=[]
def persist():
 data={'family':a.family,'modelRequested':model,'cli':cli,'cliSHA256':hashlib.sha256(pathlib.Path(cli).resolve().read_bytes()).hexdigest(),'reviewers':rows,'allTerminal':len(rows)==3 and all(x['status']=='terminal' for x in rows),'inputsVerified':True}
 p=O/(a.family+'-execution.json');tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)
verify()
for name in request['reviewers']:
 if not name.startswith(a.family+'_'):continue
 if a.family=='opus':
  command=[cli,'--print','--model',model,'--effort','high','--output-format','stream-json','--verbose','--no-session-persistence','--safe-mode','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--permission-mode','dontAsk','--permission-prompts','none','--tools','Read,Glob,Grep','--allowedTools','Read,Glob,Grep','--no-chrome','--max-turns','45']
 else:
  command=[cli,'--model',model,'--reasoning-effort','high','--prompt-file',str(O/(name+'.prompt.txt')),'--output-format','streaming-messages-json','--tools','Read,Glob,Grep','--permission-mode','dontAsk','--no-subagents','--disable-web-search','--no-alt-screen','--max-turns','25']
 stdout=O/(name+'.stream.jsonl');stderr=O/(name+'.stderr');assert not stdout.exists()
 with stdout.open('wb') as out,stderr.open('wb') as err:
  p=subprocess.Popen(command,cwd=O,stdin=subprocess.PIPE if a.family=='opus' else subprocess.DEVNULL,stdout=out,stderr=err)
  row={'id':name,'pid':p.pid,'startTicks':pathlib.Path(f'/proc/{p.pid}/stat').read_text().rsplit(')',1)[1].split()[19],'status':'running','modelRequested':model,'command':command,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};rows.append(row);persist();print(name,'launched',p.pid,flush=True)
  if a.family=='opus':p.stdin.write((O/(name+'.prompt.txt')).read_bytes());p.stdin.close()
  code=p.wait();row.update(status='terminal',exitCode=code,finishedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
 messages=[]
 for line in stdout.read_text().splitlines():
  try:messages.append(json.loads(line))
  except json.JSONDecodeError:pass
 if a.family=='opus':
  init=[m for m in messages if m.get('type')=='system' and m.get('subtype')=='init'];results=[m for m in messages if m.get('type')=='result'];row['modelObserved']=init[-1].get('model') if init else None
  if results:
   result=results[-1];(O/(name+'.result.json')).write_text(json.dumps(result,indent=2)+'\n');(O/(name+'.md')).write_text(result.get('result','')+'\n');row['modelUsage']=result.get('modelUsage',{});row['isError']=result.get('is_error');row['passed']=code==0 and row['modelObserved']==model and not row['isError'] and bool(result.get('result'))
 else:
  # Keep the raw model-labelled wire stream authoritative; extract text after inspecting its schema.
  texts=[];models=set()
  for m in messages:
   for value in [m,m.get('message',{})]:
    if value.get('model'):models.add(value['model'])
    if value.get('role')=='assistant':texts.extend(c['text'] for c in value.get('content',[]) if c.get('type')=='text')
  row['modelsObserved']=sorted(models);row['passed']=code==0 and bool(texts)
  if texts:(O/(name+'.md')).write_text('\n\n'.join(texts)+'\n')
 verify();persist();print(name,'terminal',code,'passed',row.get('passed',False),flush=True)
 if not row.get('passed'):raise SystemExit('Reviewer failed; retain raw output and diagnose without model substitution')
raise SystemExit(not all(x.get('passed') for x in rows))
