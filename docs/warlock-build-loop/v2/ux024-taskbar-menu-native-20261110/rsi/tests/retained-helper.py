#!/usr/bin/env python3
"""Root-only conditional runner-only proc-image mixed diagnostic V8b metadata after actual native51 closure and source-bound protected regression passes."""
from pathlib import Path
import argparse,ast,copy,hashlib,importlib.util,json,os,re,signal,stat,sys
ROOT=Path('/home/hoskinson/Projects/Warlock')
HERE=Path(__file__).resolve().parent
OUT=HERE/'prepared'
PREFIX='.warlock-contributor/evidence/nextloop-20261106/ux024-original-menu-focus-v9-clean'
RECORD='.warlock-contributor/ux024-menu-tab-focus-root-20261109.json'
CORE='plugins/warlock-contributor/scripts/warlock.py'
CORE_SHA='6835bb428154d23d7e89e85b17c971c2db30c293a2a8ee1f5b3ddf9ef721ff78'
IDENTITY='60fc89b0b68fd5f48614e08c0b203a765442483ac57d5e2c59a1771ace553fa4'
CANDIDATE='175d86dd14f5d127aa83a93ca6d6d51b40e8f1f0a6bb0a20c4386e19476668d2'
DOC_CANDIDATE='eddabeba52077e1b750e506b16ff5fc5567c70104b11a79fb208f5f9a29290f8'
WEBKIT='implementation/warlock/haskell/runtime/ui/Warlock/Ui/WebKit.hs'
MVP='implementation/warlock/haskell/runtime/ui/Warlock/Ui/Mvp.hsc'
MAIN='implementation/warlock/haskell/runtime/test-ui-webkit/Main.hs'
RUNNER='tools/run_current_arm_ux024_foreign_toplevel_observer.py'
INPUTS_SHA='c2c812eab9da345b40ae84084a32b1786a2352b06b9866620508eb621efdcd1d'
ROLES=('sourceAndImages','providerAndABI','nestedInput')
TUPLE_KEYS=('recordPath','recordIdentitySha256','selectionGeneration','sourceHashes','guardHashes','assets','assetSources','input','binding','foundationPacket','foundationReport','reuse','buildReport','documentBuildReport','keyboardBuildReport','abi','contract','processInventory','documentFixtureOnly','authorization','producerMode','journey')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def read(path, expected=None, cap=64*1024*1024):
    path = Path(path)
    require(path.is_absolute() and path.resolve() == path, 'canonical nonsymlink path required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_size <= cap, 'bounded regular input required')
        body = stream.read(before.st_size + 1)
        after = os.fstat(stream.fileno())
    fields = ('st_dev','st_ino','st_size','st_mode','st_mtime_ns','st_ctime_ns')
    require(len(body) == before.st_size and all(getattr(before,k)==getattr(after,k) for k in fields), 'input changed during read')
    require((path.lstat().st_dev,path.lstat().st_ino)==(before.st_dev,before.st_ino), 'input pathname replaced')
    digest = hashlib.sha256(body).hexdigest()
    require(expected is None or expected == digest, 'input hash differs: '+str(path))
    return body

def ref(path):
    path=Path(path)
    return {'path':str(path),'sha256':hashlib.sha256(read(path)).hexdigest()}

def document(reference):
    return json.loads(read(reference['path'],reference['sha256']))

def put(directory,name,value):
    path=directory/name
    with path.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(value,indent=2)+'\n')
    path.chmod(0o600)
    return ref(path)

def load(name,path,expected):
    read(path,expected)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def physical(path,pin):
    path=Path(path);read(path,pin,256*1024*1024);s=path.lstat()
    return dict(path=str(path),sha256=pin,device=s.st_dev,inode=s.st_ino,size=s.st_size,mode=stat.S_IMODE(s.st_mode))




def validate_admitted_rsi(core,record,history,expected_event):
    require(expected_event.get('kind')=='rsi' and expected_event.get('disposition')=='deferred-blocker','actual bounded deferred-blocker RSI event disposition required')
    require(expected_event.get('candidateSha256')==history['candidateSha256'] and expected_event.get('integrationRevision')==history['integrated']['revision'],'RSI candidate/integration binding differs')
    admitted=[row for row in record['delivery']['events']if all(row.get(k)==v for k,v in expected_event.items())]
    require(len(admitted)==1,'exactly one matching admitted RSI event required')
    evidence=json.loads(core.delivery_ref(ROOT,expected_event['evidence']))
    require(history['rsi']==evidence and evidence.get('disposition')==expected_event['disposition'] and evidence.get('candidateSha256')==history['candidateSha256'] and evidence.get('integrationRevision')==history['integrated']['revision'] and evidence.get('authorizationExpiresUTC')==core.effective_delivery_authorization(record),'validated RSI evidence binding differs')
    return evidence


def check_state(core,inputs):
    before=read(ROOT/RECORD);record=json.loads(before);record['_recordPath']=RECORD
    reqs,state=core.context(ROOT);core.current_selection(record,state,31);history=core.delivery_state(ROOT,record,reqs)
    require(core.record_identity(record,RECORD)==IDENTITY and len(record['slice']['paths'])==32,'same participant/current declaration required')
    require(history['candidateSha256']==CANDIDATE and history['terminal'] and history['terminal']['classification']=='pass' and history['job']['consumed'] is True,'actual clean CPU53 pass and consumption required')
    require(canonical(document(inputs['cleanCpuCandidate']))==CANDIDATE,'actual clean CPU53 candidate differs')
    require(history['terminal'].get('rawReport')=={'path':str(Path(inputs['haskellReport']['path']).relative_to(ROOT)),'sha256':inputs['haskellReport']['sha256']},'canonical CPU53 report differs')
    integrated=history['integrated'];require(integrated and integrated.get('sliceCompleted') is True and integrated.get('revision')=='a8e4781a0b9c2002aa60f815b47eedfde7e8a728','actual clean source integration required')
    validate_admitted_rsi(core,record,history,document(inputs['rsiEvent']))
    require(canonical(document(inputs['cpuCandidate']))==DOC_CANDIDATE,'retained CPU50 candidate differs')
    result_review=document(inputs['cpuResultReview'])
    require(result_review.get('reviewer')=='build_audit' and result_review.get('disposition','').startswith('accepted') and result_review.get('candidateSha256')==DOC_CANDIDATE and result_review.get('report')==inputs['documentReport'],'retained CPU50 actual result peer differs')
    native52=document(inputs['failedTerminal'])
    require(native52.get('classification')=='pass' and native52.get('candidateSha256')=='2720c360fc0c629da388db78a600d8eb31d6420725638f6fe70d1cd0f1ba1400','retained actual diagnostic native52 pass differs')
    native_ref={'path':str(Path(inputs['failedTerminal']['path']).relative_to(ROOT)),'sha256':inputs['failedTerminal']['sha256']}
    require(any(e.get('kind')=='execution-finished' and e.get('candidateSha256')==native52['candidateSha256'] and e.get('outerHandleConsumed') is True and e.get('report')==native_ref for e in record['delivery']['events']),'actual native52 canonical consumption required')
    require(core.effective_delivery_authorization(record)=='2026-11-10T14:40:00Z' and not any(e['kind']=='authorization-renewed'for e in record['delivery']['events']),'same initial human authorization required')
    return before,record,history,integrated['revision']

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare',nargs=2,metavar=('ACTUAL_GOAL_PATH','SHA256'));g.add_argument('--finalize',nargs=2,metavar=('ACCEPTED_TUPLE_REVIEW_PATH','SHA256'));args=p.parse_args();sys.dont_write_bytecode=True
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('120-second metadata bound')));signal.alarm(120)
    inputs=json.loads(read(HERE/'inputs.json',INPUTS_SHA))
    for value in inputs.values():read(value['path'],value['sha256'])
    inputs['rawGoal']=({'path':str(Path(args.prepare[0]).resolve()),'sha256':args.prepare[1]} if args.prepare else json.loads(read(OUT/'preparation.json'))['rawGoal'])
    document(inputs['rawGoal'])
    core=load('diagnostic_native_metadata_core',ROOT/CORE,CORE_SHA)
    with core.delivery_edit_lock(ROOT,RECORD):
        before,record,history,product_revision=check_state(core,inputs)
        if args.prepare:
            require(not OUT.exists(),'immutable output already exists')
            packet=document(inputs['baselinePacket']);baseline=copy.deepcopy(packet);source=document(inputs['captureManifest'])
            rows={x['path']:x for x in source['posts']}
            require(len(source['posts'])==2 and set(rows)=={WEBKIT,RUNNER},'exact clean WebKit and guard-preserving runner scope required')
            require(rows[WEBKIT]['beforeSha256']==baseline['sourceHashes'][WEBKIT]=='f1af886d0e6278aefc488d818faadcdfccec55f1f2ee3a12ab063484ac984915' and rows[WEBKIT]['sha256']=='dde4680e8d984c6231d23a2092828127111f818b6e544decb4c6b51e95928846','exact clean WebKit restoration required')
            row=rows[RUNNER]
            require(row['beforeSha256']==baseline['sourceHashes'][RUNNER]=='1c0192f26cd3d5fb1f79b922e0f75e98c1046e6859ecb6ec368c39e9e57493b0' and row['sha256']=='daffaa93eb4afb08bc3f1e6b8faa7e86cfc4e4e14e5f6d0d3359121920650d71','exact guard-preserving clean runner transition required')
            review=document(inputs['captureReview']);require(review.get('reviewer')=='build_audit' and review.get('disposition')=='accepted' and review.get('manifestSha256')==inputs['captureManifest']['sha256'],'actual cleanup source review required')
            for item in rows.values():read(item['postimage'],item['sha256']);read(ROOT/item['path'],item['sha256'])
            require(read(ROOT/RUNNER).decode().count(PREFIX+'/packet.json')==1,'exact append-only V9 namespace required')
            proc_source=document(inputs['procManifest']);proc_row=proc_source['posts'][0]
            read(proc_row['postimage'],proc_row['sha256']);proc_peer=document(inputs['procReview'])
            require(proc_peer.get('manifestSha256')==inputs['procManifest']['sha256'] and proc_peer.get('disposition')=='accepted','retained proc source review required')
            old_tree=ast.parse(read(proc_row['postimage']).decode());clean_tree=ast.parse(read(row['postimage']).decode())
            def node(tree,name):
                if '.' in name:
                    owner,method=name.split('.',1);found=[m for c in tree.body if isinstance(c,ast.ClassDef) and c.name==owner for m in c.body if isinstance(m,ast.FunctionDef) and m.name==method]
                else:found=[x for x in ast.walk(tree)if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==name]
                require(len(found)==1,'unique retained guard AST required');return ast.dump(found[0],include_attributes=False)
            for name in ('attest_process_image','same_window','consume','_HeldKeyboard.attest','_ObserverCloseSnapshots.attest'):
                require(node(old_tree,name)==node(clean_tree,name),'clean runner changed retained proc/input guard '+name)
            regressions=document(inputs['regressionReceipt']);require(regressions.get('sourceManifestSha256')==inputs['procManifest']['sha256'] and len(regressions.get('results',[]))==3,'actual retained R3 regressions required')
            expected=[('test_proc_executable_attestation',inputs['newTest0'],1),('test_fresh_input_attestation_order',inputs['newTest1'],1),('original30',inputs['originalRegressionSource'],30)]
            prefix=['/usr/bin/python3','-B',str(ROOT/'window-integration-qa/qa_run.py'),'--','/usr/bin/python3','-B']
            for actual,(label,test,count) in zip(regressions['results'],expected):
                argv=prefix+[test['path'],'--module',proc_row['postimage']]
                if label=='original30':argv+=['--phase-fixture',inputs['phaseFixture']['path'],'--capture-failure',inputs['captureFailure']['path']]
                argv+=['-q'];stderr=actual.get('stderr','')
                require(actual.get('label')==label and actual.get('exit')==0 and actual.get('argv')==argv and isinstance(stderr,str) and re.search(r'Ran '+str(count)+r' tests? in ',stderr) and re.search(r'^OK\s*$',stderr,re.M),'retained protected1+1+30 regression receipt differs')
            build=document(inputs['haskellReport']);build_peer=document(inputs['haskellResultReview'])
            require(build.get('passed') is True and len(build['sourceHashes'])==271 and len(build['haskellFiles'])==260,'actual clean CPU53 Haskell report required')
            require(build_peer.get('reviewer')=='build_audit' and build_peer.get('disposition')=='accepted-actual-clean-cpu-pass' and build_peer.get('report')==inputs['haskellReport'],'actual clean CPU53 result review required')
            for name,pin in build['sourceHashes'].items():read(ROOT/name,pin)
            for role,name in [('owner','warlock-ui-owner'),('controls','ui-webkit-controls')]:
                image=build['compiledImages'][name];actual=physical(image['path'],image['sha256'])
                require(all(actual[k]==int(image[k])for k in ('device','inode','size')) and actual['mode']==0o755,'actual clean CPU53 image changed')
                previous=packet['assets'][role];require(packet['processInventory'].get(previous['path'])==previous['sha256'],'previous active image mapping missing')
                packet['processInventory'].pop(previous['path']);packet['processInventory'][image['path']]=image['sha256']
                packet['assets'][role]={'path':image['path'],'sha256':image['sha256']};packet['assetSources'][role]={'report':inputs['haskellReport'],'selector':['compiledImages',name],'mode':actual['mode']}
            packet['buildReport']=inputs['haskellReport']
            docs=document(inputs['documentReport']);olddocs=document(baseline['documentBuildReport'])
            require(docs.get('passed') is True and docs.get('candidateOnly') is False and docs.get('liveSourcesAdopted') is True and docs.get('currentDocumentProvenance')=='installed-current-source' and len(docs['sources'])==123 and len(docs['currentDocumentSourceHashes'])==109,'actual installed-current three-document qualification required')
            require(set(docs['sources'])==set(olddocs['sources']) and docs['sources']==olddocs['sources'],'retained exact CPU50 document inputs required')
            for name,pin in docs['sources'].items():read(ROOT/name,pin)
            for name,pin in docs['currentDocumentSourceHashes'].items():read(ROOT/'implementation/warlock/src'/name,pin)
            provider=document(inputs['providerReport']);proof=document(inputs['acceptedProviderProof'])
            require(len(provider['sourceHashes'])==4255 and len(provider['sourceInputs'])==32 and proof.get('buildReport')==inputs['providerReport'],'exact retained provider inventory/proof required')
            require(all(n not in provider['sourceHashes'] and n not in provider['sourceInputs']for n in {WEBKIT,RUNNER}),'changed input belongs to retained provider build; no reuse inferred')
            require(inputs['acceptedProviderProof']['sha256']==baseline['reuse']['providerSourceCorrespondence']['sha256'],'accepted provider proof changed')
            green=document(inputs['escapeGreen']);execution=document(inputs['escapeExecution'])
            require(green.get('passed') is True and green.get('failures')==[] and len(green.get('cases',[]))==21 and all(x.get('passed') is True for x in green['cases']) and green.get('checks') and all(x.get('passed') is True for x in green['checks']),'actual 21-case Escape GREEN required')
            require(green.get('artifactHashes',{}).get('harness')==inputs['escapeFixture']['sha256'] and green['artifactHashes'].get('image')==docs['currentHttpDocuments']['popup']['sha256'],'Escape GREEN must use exact fixed fixture and fresh Popup image')
            seeds=green.get('seeded',{});require(seeds.get('seeds')==list(range(32)) and [x.get('seed')for x in seeds.get('samples',[])]==list(range(32)) and seeds.get('positiveWitnesses')==4 and seeds.get('negativeWitnesses')==28,'actual reproducible Escape matrix required')
            prior_execution=document(inputs['baselineEscapeExecution']);expected_argv=prior_execution['argv'][:5]+[inputs['escapeFixture']['path'],docs['currentHttpDocuments']['popup']['path'],inputs['escapeGreen']['path']]
            require(execution.get('exit')==0 and execution.get('argv')==expected_argv and expected_argv[:4]==['/usr/bin/python3','-B',str(ROOT/'window-integration-qa/qa_run.py'),'--'],'actual protected Escape GREEN execution required')
            contrast=document(inputs['contrastGreen']);contrast_execution=document(inputs['contrastExecution'])
            require(contrast.get('passed') is True and contrast.get('failures')==[] and len(contrast.get('cases',[]))==25 and all(x.get('passed') is True for x in contrast['cases']) and contrast.get('checks') and all(x.get('passed') is True for x in contrast['checks']),'actual unchanged 25-case R4 contrast GREEN required')
            require(contrast.get('artifactHashes',{}).get('harness')==inputs['contrastFixture']['sha256'] and contrast['artifactHashes'].get('image')==docs['currentHttpDocuments']['popup']['sha256'],'contrast GREEN must use exact frozen R4 fixture and fresh Popup image')
            contrast_seeds=contrast.get('seeded',{});require(contrast_seeds.get('seeds')==list(range(32)) and [x.get('seed')for x in contrast_seeds.get('samples',[])]==list(range(32)) and contrast_seeds.get('positiveWitnesses')==4 and contrast_seeds.get('negativeWitnesses')==28,'actual reproducible contrast matrix required')
            contrast_argv=prior_execution['argv'][:5]+[inputs['contrastFixture']['path'],docs['currentHttpDocuments']['popup']['path'],inputs['contrastGreen']['path']]
            require(contrast_execution.get('exit')==0 and contrast_execution.get('argv')==contrast_argv,'actual protected contrast GREEN execution required')
            allowed={n:rows[n]['sha256']for n in rows}
            for name,pin in baseline['sourceHashes'].items():read(ROOT/name,allowed.get(name,pin))
            require(len(baseline['sourceHashes'])==411,'retained complete source membership differs')
            packet['sourceHashes'].update(allowed);require(len(packet['sourceHashes'])==411,'source membership expanded')
            require(all(packet['sourceHashes'].get(n)==v for n,v in build['sourceHashes'].items()),'actual compiled source closure differs')
            require(all(packet['sourceHashes'].get(n)==hashlib.sha256(read(ROOT/n)).hexdigest()for n in record['slice']['paths']),'current32 owned sources differ')
            require(packet['guardHashes']==core.effective_delivery_guards(record),'original guards changed')
            for name,pin in packet['guardHashes'].items():read(ROOT/name,pin)
            packet['selectionGeneration']=31;packet['documentBuildReport']=inputs['documentReport']
            for role in ('controller','bar','popup'):
                row=docs['currentHttpDocuments'][role];actual=physical(row['path'],row['sha256']);require(all(actual[k]==int(row[k])for k in ('device','inode','size')) and actual['mode']==0o644,'actual fresh document identity changed')
                previous=packet['assets'][role];require(packet['processInventory'].get(previous['path'])==previous['sha256'],'previous active document mapping missing')
                packet['processInventory'].pop(previous['path']);packet['processInventory'][row['path']]=row['sha256'];packet['assets'][role]={'path':row['path'],'sha256':row['sha256']};packet['assetSources'][role]={'report':inputs['documentReport'],'selector':['currentHttpDocuments',role],'mode':actual['mode']}
            packet['processInventory']=dict(sorted(packet['processInventory'].items()));require(len(packet['processInventory'])==14732,'mapping inventory count expanded')
            for role in ('controller','bar','popup'):read(packet['assets'][role]['path'],packet['assets'][role]['sha256'])
            document(packet['documentBuildReport']);document(packet['reuse']['providerSourceCorrespondence'])
            OUT.mkdir(mode=0o700)
            # Same initial authority with an exact fresh Root tool-result envelope.
            rawgoal=document(inputs['rawGoal']);response=rawgoal.get('result');goal=response.get('goal') if isinstance(response,dict) else None
            require(rawgoal.get('tool')=='get_goal' and goal and goal.get('status')=='active','actual full active goal receipt required')
            goalref=put(OUT,'goal-observation.json',{'schema':1,'observedUTC':rawgoal['observedUTC'],'actualToolResponse':response,'actualTool':'get_goal','rawToolReceipt':inputs['rawGoal'],'normalization':'Envelope key correspondence only; exact timestamp/result/rawclock preserved.'})
            auth=document(baseline['authorization']);auth['goalObservation']=goalref
            auth['goalDefinition']={'threadId':goal['threadId'],'createdAt':goal['createdAt'],'objectiveSha256':hashlib.sha256(goal['objective'].encode()).hexdigest()}
            authref=put(OUT,'current-attempt-authorization.json',auth)
            auth_module=load('product_native_authorization',ROOT/'tools/ux024_foreign_toplevel_attempt_authorization.py',packet['sourceHashes']['tools/ux024_foreign_toplevel_attempt_authorization.py'])
            auth_module.resolve_authorization(authref,record,IDENTITY,31,core)
            packet['authorization']={'path':str(ROOT/PREFIX/'current-attempt-authorization.json'),'sha256':authref['sha256']}
            packet['reviews']={role:{'path':str(ROOT/PREFIX/(role+'.json')),'sha256':None}for role in ROLES}
            allowed_fields={'sourceHashes','assets','assetSources','buildReport','processInventory','authorization','reviews'};require(all(packet[k]==baseline[k]for k in baseline if k not in allowed_fields),'unrelated packet field changed')
            put(OUT,'packet.TUPLE.json',packet)
            put(OUT,'preparation.json',{'schema':1,'tupleSha256':canonical({k:packet[k]for k in TUPLE_KEYS}),'recordSha256':hashlib.sha256(before).hexdigest(),'baselinePacket':inputs['baselinePacket'],'failedNative':inputs['failedTerminal'],'actualSourceRegressions':inputs['regressionReceipt'],'captureSource':inputs['captureManifest'],'captureReview':inputs['captureReview'],'actualCpuCandidate':CANDIDATE,'retainedDiagnosticNative52':inputs['failedTerminal'],'actualCleanCpuTerminal':history['terminal'],'actualNewDocuments':inputs['documentReport'],'retainedHaskellBuild':inputs['haskellReport'],'escapeGreen':inputs['escapeGreen'],'escapeExecution':inputs['escapeExecution'],'contrastGreen':inputs['contrastGreen'],'contrastExecution':inputs['contrastExecution'],'decoderSource':inputs['decoderManifest'],'decoderReview':inputs['decoderReview'],'retainedCpu49':inputs['retainedCpu49Terminal'],'retainedFailures':{k:inputs[k]for k in ('retainedFailed21','retainedFailedR3','retainedFailedR4')},'productSource':inputs['productManifest'],'supportSource':inputs['supportManifest'],'sameProviderProof':inputs['acceptedProviderProof'],'actualCleanIntegration':product_revision,'actualRsi':history['rsi'],'retainedProductHistory':inputs['retainedProductHistory'],'cleanIntegrationRequired':True,'rsiRequired':True,'cpuResultReview':inputs['cpuResultReview'],'diagnosticWip':False,'sourceDeltas':allowed,'sourceCount':411,'ownedSources':32,'selectionGeneration':31,'rawGoal':inputs['rawGoal'],'normalizedGoal':goalref,'currentDocumentReport':packet['documentBuildReport'],'mappingCount':14732,'nativeReady':False,'originalAcceptance':False,'clockNote':'Existing product integration, RSI and sourceclock retained. Clean CPU53 pass/consumed, actual sourcea8e4781a integration and bounded deferred-blocker RSI are required. No original acceptance is inferred.'})
            print(json.dumps({'output':str(OUT),'tupleSha256':canonical({k:packet[k]for k in TUPLE_KEYS}),'nativeExecuted':False}))
        else:
            final=OUT/'final';require(not final.exists(),'immutable final output already exists')
            packet=json.loads(read(OUT/'packet.TUPLE.json'));basis=json.loads(read(OUT/'preparation.json'));require(hashlib.sha256(before).hexdigest()==basis['recordSha256'],'record changed after tuple preparation')
            reviewref={'path':str(Path(args.finalize[0]).resolve()),'sha256':args.finalize[1]};decision=document(reviewref)
            require(decision.get('reviewer')=='build_audit' and decision.get('disposition')=='accepted' and decision.get('tupleSha256')==basis['tupleSha256'] and decision.get('roles')==list(ROLES),'actual independent existing-role tuple acceptance required')
            require(canonical({k:packet[k]for k in TUPLE_KEYS})==basis['tupleSha256'],'reviewed tuple changed')
            for name,pin in {**packet['sourceHashes'],**packet['guardHashes']}.items():read(ROOT/name,pin)
            final.mkdir(mode=0o700)
            for role in ROLES:
                value={k:packet[k]for k in TUPLE_KEYS};value.update(schema=1,disposition='accepted',scope='ux024-connected-foreign-toplevel-observer',role=role,componentOnly=True,independentReview=reviewref,reviewer=decision['reviewer']);item=put(final,role+'.json',value);packet['reviews'][role]={'path':str(ROOT/PREFIX/(role+'.json')),'sha256':item['sha256']}
            packetref=put(final,'packet.json',packet);previous=document(inputs['baselineCandidate']);fixtures=previous['manifest']['fixtures']
            for name,pin in fixtures.items():read(ROOT/name,pin)
            declared={n:hashlib.sha256(read(ROOT/n)).hexdigest()for n in record['slice']['paths']};runners={n:hashlib.sha256(read(ROOT/n)).hexdigest()for n in (RUNNER,'window-integration-qa/qa_run.py')};profiles={n:v for n,v in packet['sourceHashes'].items()if n not in declared and n not in fixtures and n not in runners};profiles[PREFIX+'/packet.json']=packetref['sha256']
            candidate={'id':'ux024-original-clean-v9-selection31-'+CANDIDATE[:12],'scope':'native','manifest':{'sources':declared,'fixtures':fixtures,'runners':runners,'profiles':profiles},'argv':['/usr/bin/python3','-B',str(ROOT/'window-integration-qa/qa_run.py'),'--','/usr/bin/python3','-B',str(ROOT/RUNNER),'--sha256',packetref['sha256']],'expectedObservation':'Original ELM-UX-024 ux-024 clean-source native recording: genuine current taskbar group and menu, documented Close/Refresh Tab order and forward/reverse containment, Escape dismissal, fresh exact eligible original-group return, second opening/dismissal/return and normal owned close. Exact original nine keys/no pointer/28+2/16frames/phasecap and all current ownership/input/process/proc-image guards remain. Actual clean CPU53 images, actual CPU50 documents and21/25 proofs, unchanged provider/ABI/SDK. Actual a8e4781a source integration and bounded deferred-blocker RSI must already be admitted. A pass is evidence for independent original adjudication; raw flags never grant EARS credit.','nativePrerequisites':[{'path':str(Path(v['path']).relative_to(ROOT)),'sha256':v['sha256']}for v in packet['reviews'].values()]}
            put(final,'candidate.json',candidate);put(final,'candidate-event.json',{'eventId':'ux024-original-clean-v9-candidate-'+CANDIDATE[:12],'kind':'candidate','candidate':candidate})
            copies=[]
            for source,name in [(OUT/'current-attempt-authorization.json','current-attempt-authorization.json')]+[(final/n,n)for n in [role+'.json'for role in ROLES]+['packet.json','candidate.json','candidate-event.json']]:
                item=ref(source);destination=ROOT/PREFIX/name;require(not destination.exists(),'append-only metadata destination exists');copies.append({'source':item['path'],'destination':str(destination),'sha256':item['sha256'],'expectedPreimage':None,'mode':384})
            put(final,'root-copy-plan.json',{'schema':1,'rootOnly':True,'copies':copies,'preconditions':['Fresh exact Root claims/editprecheck under existing global+participant lock for all newpaths.','All prior packets/roles/pixels/failureflags, including native51, remain immutable. Actual clean CPU53 pass/consumed, sourcea8e4781a integrated and one deferred-blocker RSI already admitted; CPU50 documents/21+25 proof retained. Native52 mixed diagnostic pass remains historical. No EARS credit inferred.','Normal candidate/independentreview/preflight before temporary diagnostic recording; freshACTIVEgoal/stops at launch. Original9keys/28+2/16frames/phasecap unchanged.']})
            put(final,'assembly.json',{'schema':1,'candidateSha256':canonical(candidate),'packetSha256':packetref['sha256'],'tupleSha256':basis['tupleSha256'],'copies':len(copies),'selectionGeneration':31,'ownedSources':32,'diagnosticWip':False,'nativeExecuted':False,'originalAcceptance':False})
            print(json.dumps({'output':str(final),'candidateSha256':canonical(candidate),'packetSha256':packetref['sha256'],'nativeExecuted':False}))
        require(read(ROOT/RECORD)==before,'record changed during metadata preparation')
    signal.alarm(0)

if __name__=='__main__':main()
