"""Timestamp-only diagnostic; never retries, qualifies or changes a deadline."""
import time,math
class BudgetTiming:
 def __init__(self,record):
  self.record=record;record['budgetTimings']=[];record['timingCallCounts']={};record['timingOverflow']=0;record['timingComplete']=True;record['nativePerformanceAccepted']=False
 def label(self,call):
  code=getattr(call,'__code__',None);return getattr(call,'__name__','call')+(':'+str(code.co_firstlineno) if code is not None else '')
 def clock(self):
  try:
   value=time.monotonic()
   if type(value) is not float or not math.isfinite(value):raise ValueError('invalid diagnostic clock')
   return value
  except Exception as error:
   self.record['timingComplete']=False
   errors=self.record.setdefault('timingClockErrors',[])
   if len(errors)<8:errors.append(type(error).__name__)
   return None
 def call(self,name,deadline,call):
  begin=self.clock();outcome='returned'
  try:return call()
  except BaseException:
   outcome='raised';raise
  finally:
   end=self.clock();counts=self.record['timingCallCounts'];counts[name]=counts.get(name,0)+1
   row={'name':name,'begin':begin,'end':end,'wallSeconds':None if begin is None or end is None else end-begin,'deadline':deadline,'remainingBefore':None if deadline is None or begin is None else deadline-begin,'remainingAfter':None if deadline is None or end is None else deadline-end,'outcome':outcome}
   if len(self.record['budgetTimings'])<1024:self.record['budgetTimings'].append(row)
   else:self.record['timingOverflow']+=1;self.record['timingComplete']=False
 def context(self,name,deadline,context):
  timing=self
  class MeasuredContext:
   def __enter__(self):return timing.call(name+':enter',deadline,context.__enter__)
   def __exit__(self,*args):return timing.call(name+':exit',deadline,lambda:context.__exit__(*args))
  return MeasuredContext()
