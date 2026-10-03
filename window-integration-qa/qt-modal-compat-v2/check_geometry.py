#!/usr/bin/env python3
"""Pure fixture coordinate preflight; never connects to compositor or starts input."""
import json
from logical_geometry import logical_output
base={'name':'eDP-2','width':2560,'height':1600,'scale':1.6,'transform':0,'x':0,'y':0};checks=[]
actual=logical_output([base]);checks.append({'name':'physical2560x1600/scale1.6 yields exact logical1600x1000','passed':(actual['logicalWidth'],actual['logicalHeight'])==(1600,1000)})
rectangles=[(100,250,460,300),(1000,300,460,300),(260,310,320,180),(330,350,240,140)]
checks.append({'name':'all four actual planned native rectangles fit logical output','passed':all(x>=0 and y>=0 and x+w<=actual['logicalWidth'] and y+h<=actual['logicalHeight'] for x,y,w,h in rectangles)})
for name,monitors in [('fractional noninteger logical extent',[dict(base,width=2559)]),('rotated output',[dict(base,transform=1)]),('nonorigin output',[dict(base,x=10)]),('multiple outputs',[base,dict(base,name='second')]),('nonpositive scale',[dict(base,scale=0)])]:
 refused=False
 try:logical_output(monitors)
 except AssertionError:refused=True
 checks.append({'name':name+' refused before native launch','passed':refused})
assert all(row['passed'] for row in checks)
print(json.dumps({'result':'pass','scope':'Pure logical-coordinate fixture preflight, no native/input/Qt run','checks':checks},indent=2))
