"""Explicit persistent renderer transport. Does not launch anything on import."""
import json
import queue
import subprocess
import threading
import time

class PipeTransport:
    def __init__(self, executable, *, env, failure):
        self.process=subprocess.Popen([str(executable)],env=env,stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.failure=failure
        self.callback=lambda event:None
        self.lock=threading.Lock()
        self.condition=threading.Condition(self.lock)
        self.messages=queue.Queue(maxsize=256)
        self.output_snapshot=[]
        self.events=[]
        self.errors=[]
        self.closed=False
        self.closing=False
        self.failed=False
        self.threads=[threading.Thread(target=fn,daemon=True) for fn in (self.write,self.read,self.read_errors)]
        for thread in self.threads:thread.start()
    def set_callback(self,callback):self.callback=callback
    def outputs(self):
        with self.lock:return [dict(o) for o in self.output_snapshot]
    def ensure_outputs(self,force=False,timeout=2):
        with self.condition:
            previous={o['name']:o['generation'] for o in self.output_snapshot}
            if previous and not force:return [dict(o) for o in self.output_snapshot]
        self.send({'command':'prepareOutputs'})
        end=time.monotonic()+timeout
        with self.condition:
            while True:
                current={o['name']:o['generation'] for o in self.output_snapshot}
                if current and (not previous or current!=previous):return [dict(o) for o in self.output_snapshot]
                if self.failed or self.closed:raise BrokenPipeError('renderer failed output preparation')
                remaining=end-time.monotonic()
                if remaining<=0:raise TimeoutError('renderer output generations did not become ready')
                self.condition.wait(remaining)
    def send(self,message):
        encoded=json.dumps(message,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n'
        if len(encoded)>1048576:raise ValueError('renderer command exceeds bound')
        if self.closed or self.failed:raise BrokenPipeError('renderer transport closed')
        try:self.messages.put_nowait(encoded)
        except queue.Full:raise BrokenPipeError('renderer transport queue exhausted')
    def fail(self,reason):
        with self.lock:
            if self.failed or self.closed or self.closing:return
            self.failed=True
        self.failure(reason)
    def write(self):
        try:
            while True:
                encoded=self.messages.get()
                if encoded is None:return
                self.process.stdin.write(encoded);self.process.stdin.flush()
        except Exception as error:self.fail('command pipe: '+str(error))
    def read(self):
        try:
            while True:
                line=self.process.stdout.readline(1048577)
                if not line:break
                if len(line)>1048576 or not line.endswith('\n'):raise ValueError('unbounded/partial renderer event')
                event=json.loads(line)
                if not isinstance(event,dict):raise ValueError('invalid renderer event object')
                with self.lock:
                    self.events.append(event);self.events=self.events[-1024:]
                    if event.get('event')=='outputs':self.output_snapshot=event['outputs'];self.condition.notify_all()
                    elif event.get('event')=='cancelled':self.output_snapshot=[];self.condition.notify_all()
                # Presentation logs are drained continuously; only transaction
                # events acquire the native controller callback lock.
                if event.get('event') in ('ready','endpoint','cancelled'):self.callback(event)
                elif event.get('event') in ('fatal','rejected'):self.fail('renderer '+str(event))
            self.fail('renderer event pipe closed')
        except Exception as error:self.fail('event pipe: '+str(error))
    def read_errors(self):
        for line in self.process.stderr:
            with self.lock:self.errors.append(line);self.errors=self.errors[-128:]
    def close(self,timeout=3):
        if self.closed:return self.process.returncode
        self.closing=True
        if not self.failed:self.send({'command':'stop'})
        try:code=self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill();self.process.wait()
            code=self.process.returncode
        self.closed=True
        try:self.messages.put_nowait(None)
        except queue.Full:pass
        for stream in (self.process.stdin,self.process.stdout,self.process.stderr):stream.close()
        for thread in self.threads:thread.join(timeout=.2)
        if code!=0:raise RuntimeError('renderer failed normal shutdown: '+str(code))
        return code
