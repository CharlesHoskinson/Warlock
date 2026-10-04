"""Controlled XDG native diagnostics. Source-only until root's serialized launch."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

SLICE = Path(__file__).resolve().parents[1]
REPO = SLICE.parents[1]
RUNTIME = REPO / 'implementation/elm-shared-keyboard-runtime-v435'
FIXTURE = REPO / 'implementation/elm-geometry-xdg-hint-choice-fixture-v197'
ADAPTER = REPO / 'implementation/elm-geometry-numeric-refusal-prototype-v183/candidate/adapter'
JOURNAL = REPO / 'implementation/elm-geometry-client-journal-v194'
LUA = b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
PROFILES = [(f'{kind}-scale{scale}', [x,y,pad_x,pad_y,scale], maximum)
    for scale in (1,2) for kind,x,y,pad_x,pad_y,maximum in (
        ('zero',0,0,0,0,[0,0]), ('origin',16,24,16,24,[0,0]),
        ('finite',0,0,0,0,[400,300]), ('fixed',0,0,0,0,[320,180]))]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def preflight():
    origin=json.loads((SLICE/'origin.json').read_text())
    ancestor=Path(origin['parent'])
    assert sha(ancestor/'component-manifest.json')==origin['manifestSHA256']
    assert sha(ancestor/'qa/native.py')==origin['sourceSHA256']
    for name,row in json.loads((ancestor/'component-manifest.json').read_text())['files'].items():
        assert sha(ancestor/name)==row['sha256'],name
    assert sha(origin['requirementsPlan'])==origin['requirementsPlanSHA256']
    pointer_pin=json.loads((SLICE/'pointer-pin.json').read_text())
    for path,digest in pointer_pin['files'].items():assert sha(path)==digest,path
    for base,expected in pointer_pin['manifests'].items():
        base=Path(base);assert sha(base/'component-manifest.json')==expected
        for name,row in json.loads((base/'component-manifest.json').read_text())['files'].items():
            assert sha(base/name)==(row if type(row) is str else row['sha256']),name
    pins=json.loads((SLICE/'pins.json').read_text()); files={}
    assert (SLICE/'profiles.json').read_bytes()==(REPO/'implementation/elm-geometry-feasible-bounds-profiles-v201/profiles.json').read_bytes()
    def verify(path,digest):
        path=Path(path);assert sha(path)==digest,str(path);files[str(path)]=digest
    for path,digest in pins['files'].items():verify(path,digest)
    for relative,manifest_path in pins['manifests'].items():
        base=REPO/relative;manifest=json.loads(Path(manifest_path).read_text())
        entries=manifest['files']
        if type(entries) is dict:
            for name,row in entries.items():verify(base/name,row if type(row) is str else row['sha256'])
        elif type(entries) is list:
            for row in entries:verify(base/row['path'],row['sha256'])
        else:raise AssertionError('Unknown manifest file schema')
    meta=json.loads((RUNTIME/'native-build-report.json').read_text())
    for key in ('pluginBuildReport','linkClosureReport','coreComponentManifest','buildReport'):
        verify(meta[key],meta[key+'SHA256'])
    build=json.loads(Path(meta['pluginBuildReport']).read_text())
    assert build['passed'] and not build['missingSymbols']
    assert build['core']=={'path':meta['binary'],'sha256':meta['sha256']} or (
        build['core']['path']==meta['binary'] and build['core']['sha256']==meta['sha256'])
    verify(meta['binary'],meta['sha256']);verify(meta['plugin']['path'],meta['plugin']['sha256'])
    for section in ('inputs','dependencies','tools','linkedLibraries'):
        for path,digest in build[section].items():
            verify(Path(path) if Path(path).is_absolute() else REPO/'implementation/elm-geometry-coordinate-authority-v409'/path,digest)
    for name,digest in build['owningHeaders'].items():verify(Path(meta['pluginBuildReport']).parent/'owning-headers'/name,digest)
    for name,digest in build['artifacts'].items():verify(Path(meta['pluginBuildReport']).parent/name,digest)
    closure=json.loads(Path(meta['linkClosureReport']).read_text())
    assert closure['passed'] and not closure['missingSymbols'] and closure['plugin']==meta['plugin']
    client=json.loads((FIXTURE/'client-build-report.json').read_text())['client']
    verify(client['path'],client['sha256']);verify(client['buildReport'],client['buildReportSHA256'])
    client_build=json.loads(Path(client['buildReport']).read_text());assert client_build['passed']
    for section in ('inputs','dependencies','tools','linkedLibraries'):
        for path,digest in client_build[section].items():verify(path,digest)
    for name,digest in client_build['artifacts'].items():verify(Path(client['buildReport']).parent/name,digest)
    host=load('origin_private_host',RUNTIME/'candidate_host.py')
    host.original.qa.require_qa_scope();host.verify_inputs();host.aq_tuple()
    sys.path.insert(0,str(ADAPTER))
    from geometry_endpoint import GeometryEndpoint
    from endpoint import start_time
    journal=load('origin_client_journal',JOURNAL/'journal.py')
    return host,meta,client,GeometryEndpoint,start_time,journal,files

def run(preflight_only=False, group=None):
    out=SLICE/'qa'/('preflight-' if preflight_only else 'native-')
    out=Path(str(out)+str(time.time_ns()));out.mkdir()
    report={'passed':False,'nativeAcceptance':False,'mainDesktopActions':False,'checks':[],
        'scope':'Zero-origin buffer1/2 ordinary/MAX/restore actual pixels and synthetic parent-seat pointer recipient alignment; no physical hardware, GTK, nonzero or full-menu acceptance',
        'physicalHardwareAccepted':False,'nonzeroCapabilityAccepted':False,'gtkCompatibilityAccepted':False,
        'openGates':['full22 rendered qualification','physical pointer admission','GTK conformance','GEOMETRY-MENU-08/09/10']}
    session=None;client=None;loaded=False;output=None
    def check(name,value,**data):
        report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name
    try:
        host,meta,fixture,Endpoint,start_time,journal,inputs=preflight()
        pixels=load('presented_capture',SLICE/'qa/pixels.py')
        oracle=pixels.held_oracle(REPO)
        pointer=load('parent_pointer_helper',SLICE/'qa/pointer.py')
        pointer_oracle=load('held_pointer_oracle',REPO/'implementation/elm-xdg-pointer-journal-oracle-v213/oracle.py')
        probe_pin=json.loads((RUNTIME/'parent-probe-build.json').read_text())
        probe_build=json.loads(Path(probe_pin['buildReport']).read_text())
        assert probe_build['passed'] and sha(probe_pin['buildReport'])==probe_pin['buildReportSHA256']
        for field in ('client','module'):assert sha(probe_build[field])==probe_build[field+'SHA256']
        inputs.update(json.loads((SLICE/'pointer-pin.json').read_text())['files'])
        for path in (SLICE/'qa/pointer.py',SLICE/'origin.json',SLICE/'pointer-pin.json',Path(probe_build['client']),Path(probe_build['module'])):inputs[str(path)]=sha(path)
        for path in (SLICE/'qa/pixels.py',Path('/usr/bin/grim'),Path('/usr/bin/magick')):inputs[str(path)]=sha(path)
        inputs.update(pixels.oracle_inputs(REPO))
        report['inputs']=inputs
        report['inputs'][str(Path(__file__))]=sha(__file__)
        report['inputs'][str(SLICE/'pins.json')]=sha(SLICE/'pins.json')
        report['inputs'][str(SLICE/'REQUIREMENTS.md')]=sha(SLICE/'REQUIREMENTS.md')
        report['inputs'][str(SLICE/'profiles.json')]=sha(SLICE/'profiles.json')
        shutil.copy2(__file__,out/'native.py')
        (out/'inputs.json').write_text(json.dumps(report['inputs'],indent=2)+'\n')
        if preflight_only:
            check('actualPinnedInputsAndHostImportWithoutSession',True,files=len(inputs))
            report['passed']=True
            return report
        output=Path('/home/hoskinson/window-integration-qa')/('xdg-origin-'+str(time.time_ns()))
        def wait(predicate,deadline=None):
            deadline=time.monotonic()+6 if deadline is None else deadline
            while time.monotonic()<deadline:
                session.guard();value=predicate()
                if time.monotonic()>=deadline:raise RuntimeError('Original six-second deadline')
                if value:return value
                time.sleep(min(.04,max(0,deadline-time.monotonic())))
            raise RuntimeError('Original six-second deadline')
        request_number=0;effect_number=0;seen_incarnations=set();selected_colors={}
        def rid():
            nonlocal request_number
            request_number+=1;return str(request_number)
        plan=json.loads((SLICE/'profiles.json').read_text())['profiles']
        table={p['id']:p for p in plan}
        physical,monitor_scale=group or ((800,600),1)
        selected=[(p['id'],[*p['origin'],*p['pads'],p['bufferScale']],p['maximum']) for p in plan if p['id'] in ('zero-scale1','zero-scale2')]
        assert physical==(800,600) and monitor_scale==1
        report['full22Coverage']=False
        report['selectedProfiles']=[p[0] for p in selected]
        report['requestedOutput']={'physicalMode':physical,'monitorScale':monitor_scale}
        lua=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\n'+('hl.monitor({output="WAYLAND-1",mode="%dx%d@60",position="0x0",scale=%d})\n'%(*physical,monitor_scale)).encode()
        with host.PrivateHyprSession(output,dict(os.environ),*physical,lua,mesa_vendor=True) as session:
            try:
                parent=next(row for _,row in session.host.processes if row['name']=='weston')
                parent_socket=session.host.runtime/'weston-host'
                parent_socket_identity=host.original.socket_identity(parent_socket,session.host.runtime)
                parent_maps=host.original.mapped_files(parent['pid']);report['parentModuleMaps']=parent_maps
                check('exactParentProbeModuleMapped',parent_maps['files'].get(str(Path(probe_build['module']).resolve()))==probe_build['moduleSHA256'])
                check('exactCoreMapped',session.evidence['hyprlandMaps']['files'].get(str(Path(meta['binary']).resolve()))==meta['sha256'])
                check('exactAquamarineMapped',session.evidence['privateAquamarine']['mappedVerified'] is True)
                check('explicitPluginLoad',session.ctl('plugin','load',meta['plugin']['path']).strip()=='ok');loaded=True
                compositor=next(row for _,row in session.host.processes if row['name']=='hyprland')
                maps=host.original.mapped_files(compositor['pid']);report['pluginMaps']=maps
                check('exactPluginMapped',maps['files'].get(str(Path(meta['plugin']['path']).resolve()))==meta['plugin']['sha256'])
                endpoint=Endpoint(runtime=str(session.host.runtime),instance=session.env['HYPRLAND_INSTANCE_SIGNATURE'],
                    pid=compositor['pid'],expected_start=start_time(compositor['pid']),binary_sha256=meta['sha256'])
                endpoint.hello();attach=endpoint.geometry_attach(rid(),2)
                check('negotiatedActualObservation2',attach['geometryProtocol']==2 and attach['capabilities']['operations']==['maximize','restore-geometry'])
                for name,profile,maximum in selected:
                    x,y,right,bottom,scale=profile
                    requested=table[name]
                    command=[fixture['path'],*requested['arguments']]
                    log=output/(name+'.jsonl');stream=os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')
                    session.host.logs.append(stream)
                    client=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT,env=session.env,
                        cwd=session.host.runtime,start_new_session=True)
                    identity=host.original.process(client.pid);identity.update(name=name,command=command,log=str(log));session.host.processes.append((client,identity))
                    previous=[];address=None
                    def bounded_log():
                        with log.open('rb') as source:data=source.read(2*1024*1024+1)
                        if len(data)>2*1024*1024:raise RuntimeError('Journal byte bound')
                        return data
                    def rows():
                        nonlocal previous
                        data=bounded_log()
                        if len(data)>2*1024*1024:raise RuntimeError('Journal byte bound')
                        complete=data[:data.rfind(b'\n')+1]
                        # Poll only complete JSON records. Strong generation validation occurs after sync.
                        parsed=[json.loads(line) for line in complete.splitlines()]
                        if parsed[:len(previous)]!=previous:raise RuntimeError('Observed journal changed')
                        previous=parsed
                        refusals=[r for r in parsed if r.get('event')=='refused']
                        if refusals:raise RuntimeError('Actual fixture refused: '+repr(refusals[-1]))
                        return parsed
                    def native():
                        matching=[r for r in session.data('clients') if r.get('pid')==client.pid and r.get('title')==f'ELM-XDG-ORIGIN-PROBE-{client.pid}']
                        if len(matching)>1:raise RuntimeError('Ambiguous actual client')
                        if matching and address is not None and matching[0]['address']!=address:raise RuntimeError('Replaced address')
                        return matching[0] if matching else None
                    def send(command,deadline):
                        session.guard();assert client.poll() is None and host.original.same_process(identity)
                        before=len(rows());assert time.monotonic()<deadline
                        client.stdin.write((command+'\n').encode());client.stdin.flush()
                        request=wait(lambda:next((r for r in rows()[before:] if r.get('event')=='request' and r.get('command')==command),None),deadline)
                        barrier=wait(lambda:next((r for r in rows() if r.get('event')=='server-barrier' and r.get('requestSequence')==request['sequence']),None),deadline)
                        check(name+':'+command+':exactBarrier',barrier['command']==command and barrier['requestSerial']==request['serial'] and barrier['sequence']>request['sequence'])
                        return request
                    def snapshot(deadline):
                        send('sync',deadline)
                        def coherent_generation():
                            live=native();queued=next((r for r in reversed(rows()) if r['event']=='buffercommit'),None)
                            return live is not None and queued is not None and queued['geometry'][2:]==live['size'] and live['fullscreen']==live['fullscreenClient']==(1 if queued['maximized'] else 0)
                        wait(coherent_generation,deadline)
                        send('sync',deadline)
                        parsed=journal.parse(bounded_log(),client.pid,profile)
                        check(name+':completeConfigureAckCommitGeneration',parsed['ready'] and parsed['commits']>0)
                        buffer=next(r for r in reversed(parsed['events']) if r['event']=='buffercommit')
                        serial=buffer['ackedSerial'];argb=f'ff{0x28^(serial&63):02x}{0x71^((serial>>6)&63):02x}{0xc8^((serial>>12)&63):02x}'
                        check(name+':independentSerialColor',buffer['argb']==argb and (argb not in selected_colors or selected_colors[argb]==serial))
                        selected_colors[argb]=serial
                        facts=endpoint.geometry_facts(rid());assert time.monotonic()<deadline
                        all_rows=facts['facts']['windows'];assert len(all_rows)==1
                        fact=all_rows[0];projection=endpoint.snapshot(rid());raw=native();assert time.monotonic()<deadline
                        check(name+':actualNativeIncarnationIdentity',raw is not None and len(projection['windows'])==1 and
                            projection['windows'][0]['incarnation']==fact['incarnation'] and projection['windows'][0]['label']==raw['title'])
                        check(name+':actualNativeVisualAndOwnershipFacts',fact['visualGeometry']==[*raw['at'],*raw['size']] and
                            fact['workspace']==str(raw['workspace']['id']) and fact['monitor']==str(raw['monitor']) and fact['owner'] is None)
                        check(name+':actualNativeAndSelectedAckGeometryAgree',buffer['geometry'][2:]==raw['size'] and [buffer['width'],buffer['height']]==raw['size'],native=raw,buffer=buffer)
                        snapshot_policy=fact['sizePolicy']['inputs']
                        monitors=session.data('monitors')
                        assert time.monotonic()<deadline,'Original six-second deadline after final monitor read'
                        monitor=next(m for m in monitors if str(m['id'])==fact['monitor'])
                        check(name+':actualOutputScaleAndWorkareaBeforeIntent',monitor['width']==physical[0] and monitor['height']==physical[1] and monitor['scale']==monitor_scale and fact['workArea']==requested['expectedLogicalWorkarea'] and (snapshot_policy is None or snapshot_policy['monitorScale']==monitor_scale),monitor=monitor,workarea=fact['workArea'])
                        report.setdefault('profiles',[]).append({'requestedProfile':requested,'name':name,'profile':profile,'maximum':maximum,'native':raw,'facts':facts,'buffer':buffer,'journal':str(log)})
                        evidence=pixels.capture(session,host,output,name,parsed['events'],identity,fact,buffer,raw,monitor,deadline,oracle)
                        report.setdefault('pixelCaptures',[]).append(evidence)
                        if evidence['passed']:
                            try:
                                send('sync',deadline)
                                postjournal=journal.parse(bounded_log(),client.pid,profile)
                                postbuffer=next(r for r in reversed(postjournal['events']) if r['event']=='buffercommit')
                                postfacts=endpoint.geometry_facts(rid());postraw=native()
                                postmonitors=session.data('monitors')
                                assert time.monotonic()<deadline,'Original six-second postcapture deadline'
                                postmonitor=next(m for m in postmonitors if m['id']==monitor['id'])
                                evidence['postCapture']={'buffer':postbuffer,'facts':postfacts,'native':postraw,'monitor':postmonitor}
                                assert postbuffer==buffer,'Latest committed configure changed during capture'
                                assert postraw is not None and all(postraw[k]==raw[k] for k in ('address','pid','at','size','fullscreen','fullscreenClient','workspace','monitor')),'Actual target changed during capture'
                                assert postfacts['facts']==facts['facts'] and endpoint.geometry_context(postfacts)==endpoint.geometry_context(facts),'Native authority/context changed during capture'
                                assert all(postmonitor[k]==monitor[k] for k in ('id','name','x','y','width','height','scale')),'Output scope changed during capture'
                                assert host.original.same_process(identity),'Capture owner replaced after readback'
                                evidence['postCapturePassed']=True
                            except Exception as error:
                                evidence['passed']=False;evidence['postCaptureError']=repr(error)
                            Path(evidence['directory'],'measurement.json').write_text(json.dumps(evidence,indent=2)+'\n')
                        check(name+':actualPresentedLandmarks',evidence['passed'],capture=evidence)
                        # Independent native cursor readback establishes parent→child global mapping
                        # before target button callbacks. No callback calibrates coordinates.
                        pointer_stage={'profile':name,'bufferSequence':buffer['sequence'],'gestures':[],
                            'syntheticParentSeatInput':True,'physicalHardwareAccepted':False}
                        report.setdefault('pointerStages',[]).append(pointer_stage)
                        send('sync',deadline)
                        stage_baseline=journal.parse(bounded_log(),client.pid,profile)['events'][-1]['sequence']
                        pointer_stage['baselineSequence']=stage_baseline
                        for sample in evidence['samples']:
                            local=sample['surfaceLocal']
                            point=[fact['visualGeometry'][i]+local[i] for i in range(2)]
                            assert all(type(v) in (int,float) and v==int(v) and 0<int(v)<physical[i] for i,v in enumerate(point))
                            point=[int(v) for v in point]
                            assert point==sample['screenshotPixel'],'Pointer and observed screenshot global coordinates differ'
                            assert buffer['geometry'][:2]==[0,0] and monitor['scale']==1
                            gesture={'globalPoint':point,'expectedLocal':local};pointer_stage['gestures'].append(gesture)
                            gesture['motionAdmission']=pointer.send(session,host,parent,parent_socket_identity,probe_build['client'],[f'motion {point[0]} {point[1]}'],deadline)
                            cursor=session.data('cursorpos');pointer.deadline_guard(deadline)
                            gesture['independentCursorBeforeButtons']=cursor
                            pointer.cursor_point(cursor,point,pointer_oracle)
                            send('sync',deadline)
                            baseline_journal=journal.parse(bounded_log(),client.pid,profile)
                            baseline=baseline_journal['events'][-1]['sequence']
                            gesture['baselineSequence']=baseline
                            gesture['pairAdmission']=pointer.send(session,host,parent,parent_socket_identity,probe_build['client'],[f'motion {point[0]} {point[1]}','press 272','release 272'],deadline)
                            wait(lambda:len([r for r in rows() if r['sequence']>baseline and r['event']=='pointer-button'])>=2,deadline)
                            send('sync',deadline)
                            full=journal.parse(bounded_log(),client.pid,profile)
                            gesture['fullJournalThroughSequence']=full['events'][-1]['sequence']
                            gesture['interval']=[r for r in full['events'] if r['sequence']>baseline]
                            gesture['validatedPair']=pointer.complete_pair(full['events'],baseline,pid=client.pid,button=272,expected=local,oracle=pointer_oracle)
                            cursor=session.data('cursorpos');pointer.deadline_guard(deadline)
                            gesture['independentCursorAfterButtons']=cursor
                            pointer.cursor_point(cursor,point,pointer_oracle)
                            check(name+':completeOwnedPointerPair',True,gesture=gesture)
                        send('sync',deadline)
                        postjournal=journal.parse(bounded_log(),client.pid,profile)
                        postbuffer=next(r for r in reversed(postjournal['events']) if r['event']=='buffercommit')
                        postfacts=endpoint.geometry_facts(rid());postraw=native();postmonitors=session.data('monitors')
                        pointer.deadline_guard(deadline)
                        postmonitor=next(m for m in postmonitors if m['id']==monitor['id'])
                        assert postbuffer==buffer and postfacts['facts']['windows']==facts['facts']['windows']
                        assert postfacts['facts']['inputBlocked']==facts['facts']['inputBlocked']
                        assert host.original.same_process(identity) and all(postraw[k]==raw[k] for k in ('address','pid','at','size','fullscreen','fullscreenClient','workspace','monitor'))
                        assert all(postmonitor[k]==monitor[k] for k in ('id','name','x','y','width','height','scale'))
                        pointer_stage['postInput']={'buffer':postbuffer,'facts':postfacts,'native':postraw,'monitor':postmonitor,'beforeContext':endpoint.geometry_context(facts),'afterContext':endpoint.geometry_context(postfacts)}
                        postimage=pixels.capture(session,host,output,name+'-postpointer',postjournal['events'],identity,postfacts['facts']['windows'][0],postbuffer,postraw,postmonitor,deadline,oracle)
                        report['pixelCaptures'].append(postimage)
                        check(name+':postPointerActualPresentedLandmarks',postimage['passed'],capture=postimage)
                        send('sync',deadline)
                        finaljournal=journal.parse(bounded_log(),client.pid,profile)
                        finalbuffer=next(r for r in reversed(finaljournal['events']) if r['event']=='buffercommit')
                        finalfacts=endpoint.geometry_facts(rid());finalraw=native();finalmonitors=session.data('monitors')
                        pointer.deadline_guard(deadline)
                        finalmonitor=next(m for m in finalmonitors if m['id']==monitor['id'])
                        assert finalbuffer==buffer and finalfacts['facts']==postfacts['facts'] and endpoint.geometry_context(finalfacts)==endpoint.geometry_context(postfacts)
                        assert finalraw is not None and all(finalraw[k]==raw[k] for k in ('address','pid','at','size','fullscreen','fullscreenClient','workspace','monitor'))
                        assert all(finalmonitor[k]==monitor[k] for k in ('id','name','x','y','width','height','scale'))
                        pointer_stage['finalReadback']={'buffer':finalbuffer,'facts':finalfacts,'native':finalraw,'monitor':finalmonitor}
                        # Complete journal interval must remain exact after all post-input readbacks,
                        # including final capture; an extra late button cannot be hidden.
                        for gesture in pointer_stage['gestures']:
                            upper=gesture['fullJournalThroughSequence']
                            # Later owned gestures have disjoint baselines. End last at final readback.
                            next_baselines=[g['baselineSequence'] for g in pointer_stage['gestures'] if g['baselineSequence']>gesture['baselineSequence']]
                            limit=min(next_baselines) if next_baselines else finaljournal['events'][-1]['sequence']
                            interval=[r for r in finaljournal['events'] if r['sequence']<=limit]
                            pointer.complete_pair(interval,gesture['baselineSequence'],pid=client.pid,button=272,expected=gesture['expectedLocal'],oracle=pointer_oracle)
                        stage_buttons=[r for r in finaljournal['events'] if r['sequence']>stage_baseline and r['event']=='pointer-button']
                        assert len(stage_buttons)==10,'Extra or missing button in complete stage journal'
                        assert host.original.same_process(identity)
                        check(name+':pointerIntervalAndPostCaptureGenerationStable',True)
                        assert time.monotonic()<deadline,'Original six-second snapshot deadline'
                        return finalfacts['facts']['windows'][0],finalfacts,buffer,finalraw
                    primary=None
                    try:
                        deadline=time.monotonic()+6
                        wait(lambda:any(r.get('event')=='ready' for r in rows()),deadline);raw=wait(native,deadline);address=raw['address']
                        selector=json.dumps('address:'+address)
                        check(name+':exactAddressFloatingSetup',session.ctl('eval','local r=hl.dispatch(hl.dsp.window.float({action="enable",window='+selector+'})); if type(r)~="table" or r.ok~=true then error("float refused") end').strip()=='ok')
                        fact,facts,buffer,raw=snapshot(deadline)
                        supported=requested['expectedMAX']
                        check(name+':distinctNativeWindowIncarnation',fact['incarnation'] not in seen_incarnations)
                        seen_incarnations.add(fact['incarnation'])
                        policy=fact['sizePolicy']['inputs']
                        if name.startswith('fixed'):
                            check(name+':fixedConversionUnavailableTruthfully',fact['fixedSize'] is True and policy is None and fact['sizePolicy']['maximize'] is None and fact['sizePolicy']['restoreGeometry'] is None)
                        else:
                            check(name+':actualRawHintsAndGeometryOrigin',policy is not None and policy['rawMinimum']==requested['minimum'] and policy['rawMaximum']==maximum and policy['geometryOrigin']==[x,y],policy=policy)
                        ownership={k:fact[k] for k in ('incarnation','workspace','workspaceGeneration','monitor','outputOwnershipGeneration','workAreaRevision','workArea')}
                        check(name+':truthfulConversionAndLowerBoundSupport',fact['capabilities']['maximize'] is supported and
                            fact['nativeMode']==fact['clientMode']=='ordinary' and fact['minimized'] is False)
                        if name.startswith('origin'):
                            check(name+':nonzeroOriginNoProjection',fact['sizePolicy']['maximize'] is None and fact['geometryEligible'] is False)
                        if not name.startswith('origin'):
                            effect_number+=1
                            intent={'request':str(effect_number),'generation':str(effect_number),'incarnation':fact['incarnation'],'operation':'maximize','context':endpoint.geometry_context(facts)}
                            previous_at_intent=list(rows())
                            assert time.monotonic()<deadline,'Original six-second ordinary observation deadline'
                            prospective=fact['sizePolicy']['maximize']
                            deadline=time.monotonic()+6
                            receipt=endpoint.geometry_effect(intent);assert time.monotonic()<deadline
                            check(name+':exactGeometryReceipt',receipt['intent']==intent and receipt['effectProtocol']==2 and receipt['status']==('Committed' if supported else 'Refused'),receipt=receipt)
                            if not supported:
                                reason='geometry-ineligible' if name.startswith(('origin','fixed')) else 'geometry-size-infeasible'
                                check(name+':specificPolicyRefusalReason',receipt['reason']==reason,receipt=receipt)
                            if supported:
                                wait(lambda:native() and native()['fullscreen']==native()['fullscreenClient']==1 and any(r.get('event')=='buffercommit' and r['sequence']>buffer['sequence'] and r['maximized'] for r in rows()),deadline)
                                maxfact,maxfacts,maxbuffer,maxraw=snapshot(deadline)
                                check(name+':maxActualClientAndNativeMode',maxfact['nativeMode']==maxfact['clientMode']=='maximized' and maxbuffer['maximized'] is True and maxfact['capabilities']['restoreGeometry'] is True and maxfact['logicalGeometry']==maxfact['workArea'] and all(maxfact[k]==value for k,value in ownership.items()))
                                selected_configure=next(r for r in reversed(rows()) if r['event']=='configure' and r['serial']==maxbuffer['ackedSerial'] and r['sequence']<maxbuffer['sequence'])
                                check(name+':maxActualProjectionConfigureAndRealAgree',prospective is not None and [*maxraw['at'],*maxraw['size']]==prospective['real'] and maxbuffer['geometry'][2:]==prospective['configure'] and [selected_configure['configuredWidth'],selected_configure['configuredHeight']]==prospective['configure'],expectedProjection=prospective,native=maxraw,buffer=maxbuffer,configure=selected_configure)
                                assert time.monotonic()<deadline,'Original six-second MAX transition deadline'
                                effect_number+=1;intent={'request':str(effect_number),'generation':str(effect_number),'incarnation':fact['incarnation'],'operation':'restore-geometry','context':endpoint.geometry_context(maxfacts)}
                                deadline=time.monotonic()+6;receipt=endpoint.geometry_effect(intent);assert time.monotonic()<deadline
                                check(name+':exactRestoreReceipt',receipt['intent']==intent and receipt['status']=='Committed' and receipt['effectProtocol']==2)
                                wait(lambda:native() and native()['fullscreen']==native()['fullscreenClient']==0 and any(r.get('event')=='buffercommit' and r['sequence']>maxbuffer['sequence'] and not r['maximized'] for r in rows()),deadline)
                                restored,_,restorebuffer,restoreraw=snapshot(deadline)
                                check(name+':ordinaryPlacementRestored',restoreraw['at']==raw['at'] and restoreraw['size']==raw['size'] and restorebuffer['geometry']==buffer['geometry'] and restored['incarnation']==fact['incarnation'] and all(restored[k]==value for k,value in ownership.items()))
                                assert time.monotonic()<deadline,'Original six-second restore transition deadline'
                            else:
                                send('sync',deadline);current=native()
                                after=endpoint.geometry_facts(rid());assert time.monotonic()<deadline
                                after_row=after['facts']['windows'][0]
                                check(name+':refusalFactsAndConfigureCountUnchanged',after['facts']==facts['facts'] and all(after_row[k]==fact[k] for k in ('incarnation','logicalGeometry','visualGeometry','ordinaryPlacementKnown')) and len([r for r in rows() if r['event']=='configure'])==len([r for r in previous_at_intent if r['event']=='configure']))
                                check(name+':refusalNoMutation',all(current[k]==raw[k] for k in ('address','at','size','fullscreen','fullscreenClient')) and
                                    next(r for r in reversed(rows()) if r['event']=='buffercommit')==buffer)
                                assert time.monotonic()<deadline,'Original six-second refusal transition deadline'
                    except Exception as error:
                        primary=error
                        report['primaryError']=repr(error)
                        report['primaryTraceback']=traceback.format_exc()
                        report['primaryProfile']=name
                        raise
                    finally:
                        cleanup=[]
                        def cleanup_step(step,action):
                            try:action()
                            except Exception as error:
                                cleanup.append({'profile':name,'step':step,'error':repr(error),'traceback':traceback.format_exc()})
                        def quit_client():
                            if client.poll() is None:
                                client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
                        cleanup_step('quitOwnedClient',quit_client)
                        def validate_terminal():
                            terminal=journal.parse(bounded_log(),client.pid,profile,terminal=True)
                            check(name+':normalClientExit',client.returncode==0 and terminal['normalExit'])
                        cleanup_step('validateTerminalJournal',validate_terminal)
                        cleanup_step('nativeAddressRetired',lambda:wait(lambda:native() is None))
                        cleanup_step('actualClientsEmpty',lambda:wait(lambda:session.data('clients')==[]))
                        cleanup_step('nativeCensusOracle',lambda:check(name+':actualNativeClientCensusEmptyBeforeNextActor',session.data('clients')==[]))
                        report.setdefault('profileCleanupErrors',[]).extend(cleanup)
                        if client.poll() is not None:client=None
                        if primary is None and cleanup:
                            raise RuntimeError('Profile cleanup failed: '+repr(cleanup))
            finally:
                cleanup=[]
                def final_step(step,action):
                    try:action()
                    except Exception as error:
                        cleanup.append({'step':step,'error':repr(error),'traceback':traceback.format_exc()})
                if client is not None and client.poll() is None:
                    def final_quit():
                        client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
                    final_step('quitRemainingOwnedClient',final_quit)
                if loaded:
                    final_step('clientsEmptyBeforeUnload',lambda:wait(lambda:session.data('clients')==[]))
                    if session.data('clients')==[]:
                        final_step('emptyCensusOracle',lambda:check('actualClientsEmptyBeforePluginUnload',session.data('clients')==[]))
                        final_step('pluginUnload',lambda:check('normalPluginUnload',session.ctl('plugin','unload',meta['plugin']['path']).strip()=='ok'))
                        loaded=False
                    else:
                        cleanup.append({'step':'pluginUnload','error':'Refused unload while actual native clients remain'})
                report['finalCleanupErrors']=cleanup
                if sys.exc_info()[0] is None and cleanup:raise RuntimeError('Final cleanup failed: '+repr(cleanup))
        report['cleanup']=session.evidence
        check('normalPrivateCoreAndParentCleanup',not any(session.evidence.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and bool(session.evidence.get('runtimeGone')))
        for path,digest in report['inputs'].items():assert sha(path)==digest,path
        report['passed']=True
    except Exception as error:
        report['passed']=False
        report['error']=report.get('primaryError',repr(error))
        report['traceback']=report.get('primaryTraceback',traceback.format_exc())
        if report.get('primaryError') and repr(error)!=report['primaryError']:report['laterError']=repr(error)
        if session is not None:report['cleanup']=session.evidence
    finally:
        if output is not None and output.exists():shutil.copytree(output,out/'native-evidence',dirs_exist_ok=True)
        if session is not None:
            report['cleanupPassed']=not any(session.evidence.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and bool(session.evidence.get('runtimeGone'))
            report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('profileCleanupErrors') and not report.get('finalCleanupErrors')
        report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    if args.preflight:
        results=[run(True)]
    else:
        results=[]
        for group in (((800,600),1),):
            result=run(False,group);results.append(result)
            if not result['passed']:break
    sys.exit(0 if all(result['passed'] for result in results) else 1)
