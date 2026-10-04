"""Closed owning Lua fixture placement; all readbacks share original stage deadline."""
import json,re,time
from actor import remaining
from journal import Refused

def place(session,binding,x,y,width,height,deadline):
 native=binding['native'];address=native['address'];pid=native['pid'];title=native['title']
 if type(address)!=str or re.fullmatch(r'0x[0-9a-f]+',address) is None or type(pid)!=int or pid<=0 or type(title)!=str:raise Refused('exact live native fixture identity')
 if any(type(v)!=int for v in (x,y,width,height)) or not 0<=x<800 or not 0<=y<600 or not 1<=width<=800-x or not 1<=height<=600-y:raise Refused('bounded exact placement')
 selector=json.dumps('address:'+address)
 def live():
  remaining(deadline);rows=session.data('clients');remaining(deadline)
  matches=[r for r in rows if r.get('address')==address and r.get('pid')==pid and r.get('title')==title]
  if len(matches)!=1:raise Refused('same unique actual native fixture')
  return matches[0]
 def dispatch(expression,predicate):
  live();remaining(deadline)
  code='local r=hl.dispatch('+expression+'); if type(r)~="table" or r.ok~=true then error("placement refused") end'
  if session.ctl('eval',code).strip()!='ok':raise Refused('owning structured placement refusal')
  while True:
   current=live()
   if predicate(current):return current
   time.sleep(min(.02,remaining(deadline)))
 floated=dispatch('hl.dsp.window.float({action="enable",window='+selector+'})',lambda r:r['floating'] is True)
 resized=dispatch('hl.dsp.window.resize({x='+str(width)+',y='+str(height)+',relative=false,window='+selector+'})',lambda r:r['size']==[width,height])
 moved=dispatch('hl.dsp.window.move({x='+str(x)+',y='+str(y)+',relative=false,window='+selector+'})',lambda r:r['at']==[x,y] and r['size']==[width,height] and r['floating'] is True)
 remaining(deadline);return {'identity':{'address':address,'pid':pid,'title':title},'floated':floated,'resized':resized,'moved':moved,'deadline':deadline}
