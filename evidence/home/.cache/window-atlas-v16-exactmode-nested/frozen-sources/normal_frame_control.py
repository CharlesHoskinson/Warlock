"""Require exact repeated full RGBA frames before testing renderer restoration."""
def settle_frames(observe,clock,sleep,*,timeout=5,consecutive=3):
 if consecutive<2 or timeout<=0:raise ValueError('invalid stability gate')
 deadline=clock()+timeout;previous=None;stable=0;index=0
 while clock()<deadline:
  current=observe(index);index+=1
  if not isinstance(current,bytes) or not current:raise ValueError('empty frame')
  stable=stable+1 if current==previous else 1;previous=current
  if stable>=consecutive:return True
  sleep(.1)
 return False
