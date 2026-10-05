from pathlib import Path
import json,subprocess,hashlib,datetime
r=Path(__file__).resolve().parent;cli=Path('/home/hoskinson/.local/share/mise/installs/claude/latest/claude');prompt=r/'prompt.txt'
cmd=[str(cli),'--print','--model','claude-opus-5-5','--effort','high','--output-format','stream-json','--verbose','--safe-mode','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--permission-mode','dontAsk','--permission-prompts','none','--tools','Read,Glob,Grep','--allowedTools','Read,Glob,Grep','--no-chrome']
row={'modelRequested':'claude-opus-5-5','effort':'high','freshContext':True,'command':cmd,'promptSHA256':hashlib.sha256(prompt.read_bytes()).hexdigest(),'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'}
with (r/'stream.jsonl').open('wb') as out,(r/'stderr').open('wb') as err:
 p=subprocess.Popen(cmd,cwd=r,stdin=subprocess.PIPE,stdout=out,stderr=err);row['pid']=p.pid;(r/'execution.json').write_text(json.dumps(row,indent=2)+'\n');p.communicate(prompt.read_bytes())
messages=[]
for line in (r/'stream.jsonl').read_text().splitlines():
 try:messages.append(json.loads(line))
 except json.JSONDecodeError:pass
initial=[m for m in messages if m.get('type')=='system' and m.get('subtype')=='init'];results=[m for m in messages if m.get('type')=='result']
row.update(status='terminal',exitCode=p.returncode,modelObserved=initial[-1].get('model') if initial else None,finishedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
if results:
 result=results[-1];(r/'result.json').write_text(json.dumps(result,indent=2)+'\n');(r/'report.md').write_text(result.get('result','')+'\n');row['isError']=result.get('is_error');row['sessionId']=result.get('session_id')
row['passed']=p.returncode==0 and row['modelObserved']=='claude-opus-5-5' and bool(results) and not results[-1].get('is_error',True);(r/'execution.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));raise SystemExit(not row['passed'])
