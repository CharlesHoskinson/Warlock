from phase_trace import span, measured_lock, measured_call, observed_event, observed_command
"""Explicit persistent renderer transport. Does not launch anything on import."""
import json
import queue
import subprocess
import threading
import time

class PipeTransport:

    def __init__(self, executable, *, env, failure, pass_fds=(), launch_record=None, keeper=None, actor=None):
        self.owned_launch = None
        if keeper is not None:
            from owned_launch import OwnedLaunch
            match = __import__('re').fullmatch('/proc/self/fd/([0-9]+)', str(executable))
            if match is None or int(match[1]) not in pass_fds:
                raise ValueError('selected sealed renderer descriptor required')
            self.owned_launch = OwnedLaunch([str(executable)], env=env, keeper=keeper, kind='renderer', actor=actor, executable_fd=int(match[1]), record=launch_record, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, pass_fds=pass_fds)
            self.process = self.owned_launch.process
        elif launch_record is None:
            self.process = subprocess.Popen([str(executable)], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, pass_fds=pass_fds)
        else:
            raise ValueError('durable native renderer launch requires exact descriptor keeper')
        self.failure = failure
        self.callback = lambda event: None
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.messages = queue.Queue(maxsize=256)
        self.callbacks = queue.Queue(maxsize=256)
        self.failure_thread = None
        self.output_snapshot = []
        self.events = []
        self.errors = []
        self.closed = False
        self.closing = False
        self.failed = False
        self.close_error = None
        self.threads = [threading.Thread(target=fn, daemon=True) for fn in (self.write, self.read, self.read_errors, self.dispatch_callbacks)]
        for thread in self.threads:
            thread.start()

    def set_callback(self, callback):
        self.callback = callback

    def outputs(self):
        with self.lock:
            return [dict(o) for o in self.output_snapshot]

    def ensure_outputs(self, force=False, timeout=2):
        with self.condition:
            previous = {o['name']: o['generation'] for o in self.output_snapshot}
            if previous and (not force):
                return [dict(o) for o in self.output_snapshot]
        self.send({'command': 'prepareOutputs'})
        end = time.monotonic() + timeout
        with self.condition:
            while True:
                current = {o['name']: o['generation'] for o in self.output_snapshot}
                if current and (not previous or current != previous):
                    return [dict(o) for o in self.output_snapshot]
                if self.failed or self.closed:
                    raise BrokenPipeError('renderer failed output preparation')
                remaining = end - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('renderer output generations did not become ready')
                self.condition.wait(remaining)

    def send(self, message):
        observed_command(message)
        encoded = json.dumps(message, ensure_ascii=True, separators=(',', ':'), allow_nan=False) + '\n'
        if len(encoded) > 1048576:
            raise ValueError('renderer command exceeds bound')
        if self.closed or self.failed:
            raise BrokenPipeError('renderer transport closed')
        try:
            self.messages.put_nowait(encoded)
        except queue.Full:
            self.fail('renderer command queue exhausted')
            raise BrokenPipeError('renderer transport queue exhausted')

    def fail(self, reason):
        with self.lock:
            if self.failed or self.closed or self.closing:
                return
            self.failed = True
            self.condition.notify_all()
        if self.process.poll() is None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
        self.failure_thread = threading.Thread(target=self.failure, args=(reason,), daemon=True)
        self.failure_thread.start()

    def dispatch_callbacks(self):
        try:
            while True:
                if self.failed:
                    return
                event = self.callbacks.get()
                if event is None:
                    return
                try:
                    if not self.failed:
                        self.callback(event)
                finally:
                    self.callbacks.task_done()
        except Exception as error:
            self.fail('native callback dispatch: ' + str(error))

    def queue_callback(self, event):
        if self.failed:
            return
        try:
            self.callbacks.put_nowait(event)
        except queue.Full:
            self.fail('native callback queue exhausted')

    def write(self):
        try:
            while True:
                encoded = self.messages.get()
                if encoded is None:
                    return
                self.process.stdin.write(encoded)
                self.process.stdin.flush()
        except Exception as error:
            self.fail('command pipe: ' + str(error))

    def read(self):
        try:
            while True:
                line = self.process.stdout.readline(1048577)
                if not line:
                    break
                if len(line) > 1048576 or not line.endswith('\n'):
                    raise ValueError('unbounded/partial renderer event')
                event = json.loads(line)
                observed_event(event)
                if not isinstance(event, dict):
                    raise ValueError('invalid renderer event object')
                with self.lock:
                    self.events.append(event)
                    self.events = self.events[-1024:]
                    if event.get('event') == 'outputs':
                        self.output_snapshot = event['outputs']
                        self.condition.notify_all()
                    elif event.get('event') == 'cancelled':
                        self.output_snapshot = []
                        self.condition.notify_all()
                if event.get('event') in ('ready', 'endpoint', 'cancelled'):
                    self.queue_callback(event)
                elif event.get('event') in ('fatal', 'rejected'):
                    self.fail('renderer ' + str(event))
            self.fail('renderer event pipe closed')
        except Exception as error:
            self.fail('event pipe: ' + str(error))

    def read_errors(self):
        for line in self.process.stderr:
            with self.lock:
                self.errors.append(line)
                self.errors = self.errors[-128:]

    def close(self, timeout=3):
        if self.closed:
            if self.close_error:
                raise RuntimeError(self.close_error)
            return self.process.returncode
        deadline = time.monotonic() + timeout
        self.closing = True
        problems = []
        if not self.failed:
            try:
                self.send({'command': 'stop'})
            except Exception as error:
                problems.append('stop command: ' + str(error))
        try:
            code = self.process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
            code = self.process.returncode
            problems.append('renderer required forced shutdown')
        for thread in self.threads[1:3]:
            thread.join(timeout=max(0, deadline - time.monotonic()))
        if any((t.is_alive() for t in self.threads[1:3])):
            problems.append('renderer drain remained active after exit')
        try:
            self.messages.put_nowait(None)
        except queue.Full:
            problems.append('command queue remained full during shutdown')
        try:
            self.callbacks.put_nowait(None)
        except queue.Full:
            problems.append('callback queue remained full during shutdown')
        self.threads[-1].join(timeout=max(0, deadline - time.monotonic()))
        if self.threads[-1].is_alive():
            problems.append('native callback dispatch remained active after renderer exit')
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()
        self.threads[0].join(timeout=0.2)
        if code != 0:
            problems.append('renderer failed normal shutdown: ' + str(code))
        if self.failed:
            problems.append('renderer transport had already failed')
        if self.owned_launch:
            try:
                self.owned_launch.complete()
            except Exception as error:
                problems.append('exact renderer group completion: ' + str(error))
        self.closed = True
        if problems:
            self.failed = True
            self.close_error = '; '.join(problems)
            raise RuntimeError(self.close_error)
        return code
