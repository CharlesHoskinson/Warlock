"""Actual current inspection/DOM correspondence. Returns gesture geometry only."""
import json,math,re
from join import Refused,pairs,constant

def counter(value,zero=False):
 if type(value) is not str or not re.fullmatch('0|[1-9][0-9]{0,19}',value) or int(value)>2**64-1 or (not zero and value=='0'):raise Refused('canonical publication/lease')
 return value

def select(raw):
 if type(raw) is not str or len(raw.encode('utf8'))>16*1024*1024:raise Refused('owned host log bound')
 inspections=[];reports=[]
 for line in raw.split('\n')[:-1]:
  prefix='surface-inspection: ' if line.startswith('surface-inspection: ') else 'surface-report: origin=bar ' if line.startswith('surface-report: origin=bar ') else None
  if prefix is None:continue
  try:o=json.loads(line[len(prefix):],object_pairs_hook=pairs,parse_constant=constant)
  except (ValueError,UnicodeError,RecursionError) as e:raise Refused('strict actual host frame') from e
  if prefix=='surface-inspection: ':inspections.append(o)
  else:reports.append(o)
 if not inspections or not reports:return None
 current=inspections[-1];report=reports[-1]
 if type(current) is not dict or type(current.get('surfaceProtocol')) is not int or current['surfaceProtocol']!=2 or current.get('kind')!='surface-inspection' or type(current.get('body')) is not dict:raise Refused('current inspection shape')
 body=current['body'];publication=counter(current.get('publication'));lease=counter(current.get('lease'),True)
 if type(report) is not dict or report.get('kind')!='surface-report' or type(report.get('body')) is not dict:raise Refused('actual bar report shape')
 rendered=report['body']
 # Initial DOM reports may have no published shell yet.
 if rendered.get('publication') is None and rendered.get('lease') is None:return None
 counter(rendered.get('publication'));counter(rendered.get('lease'),True)
 if rendered['publication']!=publication or rendered['lease']!=lease:return None
 if body.get('phase')!='Coherent' or body.get('transaction')!='Idle' or body.get('mode')!='closed' or body.get('menu') is not None or body.get('picker') is not None:return None
 for key in ('outstanding','registry'):
  if type(body.get(key)) is not int or body[key]<0:raise Refused('typed original ledger count')
  if body[key]!=0:return None
 groups=body.get('groups')
 if type(groups) is not list or len(groups)>256:raise Refused('bounded groups')
 if not groups:return None
 if len(groups)!=1:raise Refused('ambiguous current group')
 group=groups[0]
 if type(group) is not dict or type(group.get('domId')) is not str or not group['domId'] or len(group['domId'])>2048:raise Refused('exact current group DOM identity')
 buttons=rendered.get('buttons')
 if type(buttons) is not list or len(buttons)>512:raise Refused('bounded rendered controls')
 matching=[b for b in buttons if type(b) is dict and b.get('id')==group['domId']]
 if not matching:return None
 if len(matching)!=1:raise Refused('ambiguous exact rendered control')
 button=matching[0]
 if type(button.get('disabled')) is not bool:raise Refused('typed disabled control')
 if button['disabled']:return None
 coordinates=[]
 for key in ('x','y','width','height'):
  value=button.get(key)
  if type(value) not in (int,float):raise Refused('numeric actual control geometry')
  try:finite=math.isfinite(value)
  except OverflowError:finite=False
  if not finite:raise Refused('finite actual control geometry')
  coordinates.append(value)
 x,y,w,h=coordinates
 if w<=0 or h<=0 or x<0 or y<0 or x+w>800 or y+h>600:raise Refused('qualified viewport control geometry')
 point=[round(x+w/2),round(y+h/2)]
 if not 0<point[0]<800 or not 0<point[1]<600:raise Refused('qualified gesture point')
 return point
