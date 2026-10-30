    def current_attention_view(body):
     import re
     rows={}
     for line in text().splitlines():
      match=re.match(r'^view-report: id=(\d+) x=(-?\d+) y=(-?\d+) (\{.*\})$',line)
      if match:
       frame=json.loads(match.group(4));rows[match.group(1)]={'id':match.group(1),'x':int(match.group(2)),'y':int(match.group(3)),'body':frame.get('body')}
     matches=[v for v in rows.values() if v['x']==0 and v['y']==0 and v['body']==body]
     return matches[0] if len(matches)==1 else None
    def capture_attention_at(stage,label,state,identity):
     body=bar_body();p=projection();facts_before=attention_facts()
     check(stage+'CoherentBefore',bool(body and p and p.get('phase')=='Coherent' and body.get('publication')==p.get('publication') and body.get('lease') is not None))
     rows=[b for b in body['buttons'] if b['accessibleName'].startswith(('Activate '+label+';','Minimize '+label+';')) and state in b['accessibleName'] and not b.get('disabled')]
     check(stage+'OneCurrentBarIdentity',len(rows)==1 and bool(rows[0].get('id')))
     button=rows[0];view=current_attention_view(body);check(stage+'OneOwningOutput',view is not None)
     host_start=start_time(web.pid);obs=at_observe()
     nodes=[n for n in obs.get('nodes',[]) if n.get('pid')==web.pid and n.get('identity') and n.get('name')==button['accessibleName'] and (n.get('attributes') or {}).get('id')==button['id'] and any(a.get('role')=='document web' for a in n.get('ancestors',[])) and {'enabled','sensitive','visible','showing'}<=set(n.get('states',[]))]
     current=bar_body();after_projection=projection();facts_after=attention_facts()
     before_windows=[w for w in facts_before['facts']['windows'] if w['incarnation']==identity];after_windows=[w for w in facts_after['facts']['windows'] if w['incarnation']==identity]
     still=[b for b in (current or {}).get('buttons',[]) if b.get('id')==button['id'] and b.get('accessibleName')==button['accessibleName'] and not b.get('disabled')]
     check(stage+'ActualATUniqueAndCurrent',len(nodes)==1 and not obs.get('errors') and start_time(web.pid)==host_start and current is not None and after_projection is not None and current.get('publication')==body.get('publication')==after_projection.get('publication') and current.get('lease')==body.get('lease') and current_attention_view(current)==view and len(still)==1 and len(before_windows)==len(after_windows)==1 and before_windows[0]==after_windows[0] and facts_before['facts']['focused']==facts_after['facts']['focused'],node=nodes,body=body,after=current,factsBefore=facts_before,factsAfter=facts_after)
     report.setdefault('attentionATSnapshots',[]).append({'stage':stage,'hostPID':web.pid,'hostStart':host_start,'nativeIncarnation':identity,'publication':body['publication'],'lease':body['lease'],'owningOutput':view,'node':nodes[0],'snapshot':obs,'association':'contemporaneous current bar identity and native authority facts; AT-SPI has no publication field'})
