"""One exact pidfd pause; every replaced path gets a rollback attempt on write failure."""
import os,signal
class WriteFailure(RuntimeError):
 def __init__(self,cause,replaced,rollback_errors):
  super().__init__(repr(cause));self.replaced=replaced;self.rollback_errors=rollback_errors

def replace_while_stopped(handle,changes,signal_fn=signal.pidfd_send_signal):
 signal_fn(handle,signal.SIGSTOP);replaced=[]
 try:
  try:
   for row in changes:os.replace(row['staged'],row['live']);replaced.append(row)
  except Exception as error:
   failures=[]
   for row in reversed(replaced):
    try:os.replace(row['rollback'],row['live'])
    except Exception as rollback_error:failures.append({'path':row['path'],'error':repr(rollback_error)})
   raise WriteFailure(error,[row['path'] for row in replaced],failures) from error
 finally:
  signal_fn(handle,signal.SIGCONT)
 return [row['path'] for row in replaced]
