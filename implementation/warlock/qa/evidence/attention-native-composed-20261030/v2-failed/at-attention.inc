    def current_attention_view(body):
     import re
     rows={}
     for line in text().splitlines():
      match=re.match(r'^view-report: id=(\d+) x=(-?\d+) y=(-?\d+) (\{.*\})$',line)
      if match:
       frame=json.loads(match.group(4));rows[match.group(1)]={'id':match.group(1),'x':int(match.group(2)),'y':int(match.group(3)),'body':frame.get('body')}
     matches=[v for v in rows.values() if v['x']==0 and v['y']==0 and v['body']==body]
     return matches[0] if len(matches)==1 else None
    def attention_binding(body,p,facts,label,state,identity):
     if not body or not p or p.get('phase')!='Coherent' or body.get('publication')!=p.get('publication') or body.get('lease') is None:return None
     windows=facts['facts']['windows'];matches=[w for w in windows if w['incarnation']==identity and w['owner'] is None]
     if len(matches)!=1:return None
     window=matches[0];application=window['application'];key='application:'+application if application else 'window:'+identity
     if len([w for w in windows if w['owner'] is None and w['application']==application])!=1:return None
     groups=[g for g in p['groups'] if g['key']==key]
     if len(groups)!=1:return None
     group=groups[0];active=state=='Active'
     if bool(group['active'])!=active:return None
     if active:
      if facts['facts']['focused']!=identity or window['attention']:return None
     elif not window['attention'] or facts['facts']['focused']==identity:return None
     rows=[row for row in body['buttons'] if row.get('identity')=='bar:group:'+key and row.get('id')==group['domId'] and row['accessibleName'].startswith(('Activate '+label+';','Minimize '+label+';')) and state in row['accessibleName'] and not row.get('disabled')]
     view=current_attention_view(body)
     if len(rows)!=1 or view is None:return None
     return {'button':rows[0],'group':group,'window':window,'view':view,'active':active}
    def capture_attention_at(stage,label,state,identity):
     def sample():
      body=bar_body();p=projection();before=attention_facts();binding=attention_binding(body,p,before,label,state,identity)
      if binding is None:return None
      button=binding['button'];host_start=start_time(web.pid);obs=at_observe()
      nodes=[node for node in obs.get('nodes',[]) if node.get('pid')==web.pid and node.get('identity') and node.get('role') in ['button','push button','toggle button'] and node.get('name')==button['accessibleName'] and (node.get('attributes') or {}).get('id')==button['id'] and any(a.get('role')=='document web' for a in node.get('ancestors',[])) and any(a.get('role')=='tool bar' and a.get('name')=='Warlock taskbar' for a in node.get('ancestors',[])) and {'enabled','sensitive','visible','showing'}<=set(node.get('states',[])) and bool({'pressed','checked'}&set(node.get('states',[])))==binding['active']]
      current=bar_body();after_projection=projection();after=attention_facts();after_binding=attention_binding(current,after_projection,after,label,state,identity)
      valid=len(nodes)==1 and not obs.get('errors') and start_time(web.pid)==host_start and after_binding==binding and current is not None and current.get('publication')==body.get('publication') and current.get('lease')==body.get('lease') and before['facts']['focused']==after['facts']['focused']
      candidate={'stage':stage,'hostPID':web.pid,'hostStart':host_start,'nativeIncarnation':identity,'publication':body['publication'],'lease':body['lease'],'binding':binding,'nodes':nodes,'snapshot':obs,'factsBefore':before,'factsAfter':after,'afterBinding':after_binding,'association':'current coherent projection group, DOM ID, unique authority root/application and actual exported AT role/name/toggle state; AT-SPI has no publication field'}
      report.setdefault('attentionATLastSamples',{})[stage]=candidate
      return candidate if valid else None
     captured=wait(sample)
     check(stage+'ActualATUniqueCurrentAndNativeBound',len(captured['nodes'])==1 and captured['binding']==captured['afterBinding'],**captured)
     report.setdefault('attentionATSnapshots',[]).append(captured)
