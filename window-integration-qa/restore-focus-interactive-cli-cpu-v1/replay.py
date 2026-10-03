"""Actual unchanged hyprctl interactive framing against an owned CPU Unix peer."""
import hashlib,json,os,select,socket,subprocess,sys,tempfile,threading,time
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(Q))
from qa_launch import require_qa_scope
O=Path(__file__).resolve().parent
scope=require_qa_scope();seen=[];errors=[];out=bytearray();err=bytearray();proc=None
with tempfile.TemporaryDirectory(prefix='focus-cli-cpu-',dir='/run/user/1000') as temp:
 runtime=Path(temp);os.chmod(runtime,0o700);session='owned-cpu-session';p=runtime/'hypr'/session;p.mkdir(parents=True,mode=0o700)
 sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.bind(str(p/'.socket.sock'));sock.listen(4);sock.settimeout(3)
 def peer():
  try:
   for i in range(3):
    c,_=sock.accept();data=c.recv(65536);seen.append(data.decode());c.sendall(json.dumps({'nonce':'0123456789abcdef0123456789abcdef','expected':6,'completed':2*(i+1),'ok':True},separators=(',',':')).encode());c.close()
  except BaseException as e:errors.append(repr(e))
 thread=threading.Thread(target=peer);thread.start();env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime),HYPRLAND_INSTANCE_SIGNATURE=session)
 proc=subprocess.Popen(['/usr/bin/hyprctl','repl'],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 commands=['local a='+json.dumps('x'*2500)+'; print(a)' for _ in range(3)]
 boundaries=[]
 for i,command in enumerate(commands):
  proc.stdin.write((command+'\n').encode());proc.stdin.flush();deadline=time.monotonic()+2;needle=('"completed":'+str((i+1)*2)).encode()
  while needle not in out:
   wait=deadline-time.monotonic()
   if wait<=0:raise TimeoutError('actual hyprctl did not publish pair result')
   ready,_,_=select.select([proc.stdout,proc.stderr],[],[],wait)
   for f in ready:
    data=os.read(f.fileno(),65536)
    if not data:raise EOFError('premature CLI EOF')
    (out if f is proc.stdout else err).extend(data)
  boundaries.append({'pair':i,'stdoutBytes':len(out),'stderrBytes':len(err)})
 proc.stdin.close();proc.stdin=None;tail,stderr=proc.communicate(timeout=2);out.extend(tail);err.extend(stderr);thread.join(timeout=3);sock.close()
 assert not thread.is_alive() and not errors and proc.returncode==0 and len(seen)==3
 assert seen==['/repl '+c for c in commands]
 (O/'stdout.bin').write_bytes(out);(O/'stderr.bin').write_bytes(err)
 report={'result':'pass','CPUProtocolOnly':True,'nativeLuaExecuted':False,'nativeAcceptance':False,'scope':scope,'actualCLI':'/usr/bin/hyprctl','actualCLISHA256':hashlib.sha256(Path('/usr/bin/hyprctl').read_bytes()).hexdigest(),'argv':['/usr/bin/hyprctl','repl'],'requests':seen,'boundaries':boundaries,'stdoutSHA256':hashlib.sha256(out).hexdigest(),'stdoutBytes':len(out),'stderrSHA256':hashlib.sha256(err).hexdigest(),'stderrBytes':len(err),'fullProcessEOF':True,'normalExit':proc.returncode,'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'stderr':err.decode(errors='replace'),'stdoutExcerpt':out[:300].decode(errors='replace')}
 with os.fdopen(os.open(O/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':'pass','stdoutBytes':len(out),'stderrBytes':len(err),'excerpt':out[:200].decode(errors='replace')}))
