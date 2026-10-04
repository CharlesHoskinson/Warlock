"""Budget admission preflight only. Never grants performance/native acceptance."""
import argparse, datetime as dt, hashlib, json, math, re
from pathlib import Path
WORKLOADS=('cold-start','idle','catalog-refresh','switcher','minimized-preview','first-capture','reversible-motion','output-transfer','soak')
METRICS=('latency','cpu','wakeups','memory','frame-misses','power','copy-transfer')
def number(x):
    try: return type(x) in (int,float) and math.isfinite(x) and x>=0
    except OverflowError: return False
def stamp(x):
    try:
        d=dt.datetime.fromisoformat(x.replace('Z','+00:00')); return d if d.tzinfo else None
    except (ValueError,TypeError,AttributeError): return None
def validate(doc):
    issues=[]
    def need(ok,path,reason):
        if not ok: issues.append({'path':path,'reason':reason})
    def text(x): return type(x) is str and bool(x.strip())
    if type(doc) is not dict: return {'verdict':'invalid','schemaReady':False,'performanceAccepted':False,'issues':[{'path':'$','reason':'object required'}]}
    if doc.get('schema')!= 'elm-budget-preflight/1':
        legacy=doc.get('schema')==1 and 'candidateCalibration' in doc
        return {'verdict':'calibration-only' if legacy else 'invalid','completeness':'incomplete','schemaReady':False,'performanceAccepted':False,'issues':([{'path':'currentShellBaseline','reason':'missing comparative baseline'},{'path':'approvedThresholds','reason':'missing frozen numeric thresholds'},{'path':'candidateCalibration.instrumentationOverhead','reason':'missing measured instrumentation overhead'},{'path':'candidateCalibration.helperToDOMReceiptMs','reason':'helper-to-DOM is not native presentation latency'}] if legacy else [{'path':'$','reason':'unsupported schema'}])}
    def digest(x):return type(x) is str and re.fullmatch('[0-9a-f]{64}',x) is not None
    frozen=stamp(doc.get('frozenUTC')); need(frozen is not None,'frozenUTC','timezone-aware freeze timestamp required')
    need(text(doc.get('approvalReference')),'approvalReference','review/approval evidence reference required (not independently verified)')
    rows=doc.get('workloads'); need(type(rows) is list,'workloads','array required'); rows=rows if type(rows) is list else []
    ids=[r.get('id') for r in rows if type(r) is dict]
    need(len(rows)==len(WORKLOADS) and set(i for i in ids if type(i) is str)==set(WORKLOADS),'workloads','exact nine unique required workload identities required')
    for ri,row in enumerate(rows):
        path=f'workloads[{ri}]'
        if type(row) is not dict: need(False,path,'object required');continue
        need(digest(row.get('fixtureSHA256')),path+'.fixtureSHA256','workload fixture hash required')
        for k in ('warmCold','definition'):need(text(row.get(k)),path+'.'+k,'nonempty identity/definition required')
        metrics=row.get('metrics');need(type(metrics) is dict,path+'.metrics','metric map required');metrics=metrics if type(metrics) is dict else {}
        need(set(metrics)==set(METRICS),path+'.metrics','exact seven metric categories required; justified exclusions must be explicit')
        for kind,m in metrics.items():
            q=path+'.metrics.'+kind
            if type(m) is not dict:need(False,q,'object required');continue
            if 'excluded' in m:
                need(m.get('excluded') is True and text(m.get('reason')) and text(m.get('reviewReference')),q,'exclusion requires reason and review reference; applicability is not independently accepted');continue
            for k in ('unit','definition'):need(text(m.get(k)),q+'.'+k,'nonempty unit/definition required')
            limits=m.get('limits',{});need(type(limits) is dict,q+'.limits','object required');limits=limits if type(limits) is dict else {}
            for k in ('absoluteMax','regressionMaxPercent','overheadMax'):
                need(number(limits.get(k)),q+'.limits.'+k,'finite nonnegative numeric limit required; booleans rejected')
            minimum=m.get('minimumSamples');need(type(minimum) is int and minimum>0,q+'.minimumSamples','positive integer required')
            pair=[]
            for side in ('baseline','candidate'):
                obs=m.get(side);s=q+'.'+side
                if type(obs) is not dict:need(False,s,'observation object required');continue
                pair.append(obs)
                for k in ('sourceTuple','evidenceReference','clockDomain','startEvent','endEvent','backend','adapter','driver','engine'):
                    need(text(obs.get(k)),s+'.'+k,'explicit identity/clock/event/reference required')
                need(obs.get('measurementKind')=='native-input-to-present' if kind=='latency' else text(obs.get('measurementKind')),s+'.measurementKind','latency needs actual native input-to-presentation; helper-to-DOM is calibration only')
                need(obs.get('clockMapping')=='same-domain' or digest(obs.get('clockMapping')),s+'.clockMapping','same-domain declaration or measured mapping hash required')
                need(digest(obs.get('evidenceSHA256')),s+'.evidenceSHA256','evidence hash required')
                need(obs.get('wholeProcessGroupComplete') is True,s+'.wholeProcessGroupComplete','complete lifetime accounting required')
                output=obs.get('output');need(type(output) is dict,s+'.output','output identity required');output=output if type(output) is dict else {}
                for k in ('width','height','refreshHz','scale'):need(number(output.get(k)) and output.get(k)>0,s+'.output.'+k,'finite positive value required')
                need(text(output.get('id')) and text(output.get('transform')),s+'.output','id/transform required')
                need(obs.get('unit')==m.get('unit') and obs.get('definition')==m.get('definition'),s,'observation units/definition must match budget')
                samples=obs.get('samples');need(type(samples) is list and len(samples)>0 and all(number(v) for v in samples),s+'.samples','nonempty finite nonnegative samples required');samples=samples if type(samples) is list else []
                need(type(obs.get('count')) is int and obs.get('count')==len(samples) and type(minimum) is int and len(samples)>=minimum,s+'.count','count must match samples and meet frozen minimum')
                need(number(obs.get('instrumentationOverhead')) and number(limits.get('overheadMax')) and obs.get('instrumentationOverhead')<=limits.get('overheadMax'),s+'.instrumentationOverhead','measured finite overhead within frozen maximum required')
                for k in ('p50','p95','p99'):need(number(obs.get(k)),s+'.'+k,'finite percentile required')
                if samples and all(number(v) for v in samples):
                    ordered=sorted(samples)
                    for key,pct in [('p50',.5),('p95',.95),('p99',.99)]:need(obs.get(key)==ordered[math.ceil(pct*len(ordered))-1],s+'.'+key,'nearest-rank percentile must agree with samples')
                measured=stamp(obs.get('measuredUTC'));need(measured is not None,s+'.measuredUTC','timezone-aware timestamp required')
                if side=='candidate':need(frozen is not None and measured is not None and measured>=frozen,s+'.measuredUTC','candidate measurement must follow budget freeze')
            if len(pair)==2:
                for key in ('adapter','driver','backend','engine','output','clockDomain','startEvent','endEvent','measurementKind'):
                    need(pair[0].get(key)==pair[1].get(key),q+'.'+key,'baseline/candidate comparable identity/event definition required')
    return {'verdict':'ready-for-evaluation' if not issues else 'incomplete','schemaReady':not issues,'performanceAccepted':False,'issues':issues,'scope':'Structural/comparability preflight only; thresholds, evidence authenticity, applicability, measured budget pass and native acceptance require separate review.'}
def load(path):
    def constant(value):raise ValueError('non-JSON numeric constant '+value)
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON field '+k)
            out[k]=v
        return out
    return json.loads(Path(path).read_text(),parse_constant=constant,object_pairs_hook=unique)
def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--out');a=p.parse_args()
    try: result=validate(load(a.input))
    except (ValueError,OSError) as e:result={'verdict':'invalid','schemaReady':False,'performanceAccepted':False,'issues':[{'path':'$','reason':str(e)}]}
    result['inputSHA256']=hashlib.sha256(Path(a.input).read_bytes()).hexdigest() if Path(a.input).is_file() else None
    output=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if a.out:Path(a.out).write_text(output)
    print(output,end='');return 0 if result['schemaReady'] else 2
if __name__=='__main__':raise SystemExit(main())
