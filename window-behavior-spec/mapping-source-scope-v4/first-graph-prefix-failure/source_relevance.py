"""Pure frozen-reference graph analysis, no runtime filesystem observation."""
from collections import deque

def resolve_expected(path,links):
 if not isinstance(path,str)or not path.startswith('/'):raise ValueError('absolute frozen source spelling required')
 todo=deque(path.split('/'));parts=[];visited=[]
 while todo:
  item=todo.popleft()
  if item in ('','.'):continue
  if item=='..':
   if not parts:raise ValueError('frozen reference escapes root')
   parts.pop();continue
  selected='/'+'/'.join(parts+[item])
  if selected in links:
   if selected in visited or len(visited)>=40:raise ValueError('frozen reference cycle/limit')
   visited.append(selected);target=links[selected]
   if not isinstance(target,str)or not target:raise ValueError('literal frozen link target required')
   if target.startswith('/'):parts=[]
   todo.extendleft(reversed(target.split('/')))
  else:parts.append(item)
 return '/'+'/'.join(parts),tuple(visited)

def selected_aliases(images,launchers,links):
 selected=set();unresolved=[]
 for spelling in launchers:
  _,chain=resolve_expected(spelling,links);selected.update(chain)
 for alias in links:
  try:target,chain=resolve_expected(alias,links)
  except ValueError as error:unresolved.append((alias,str(error)));continue
  if target in images:selected.update(chain)
 for image in images:
  resolved,chain=resolve_expected(image,links)
  if resolved!=image:raise ValueError('selected named image is not canonical in frozen reference')
  selected.update(chain)
 return sorted(selected),unresolved
