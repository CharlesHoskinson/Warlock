"""Actual retained Warlock predecessor recovery in the protected private session.

Preserve the original six-second observations, physical keyboard, native pair,
application fixtures and cleanup. This is not an accepted Omarchy deployment.
"""
import hashlib
import pathlib
import sys

assert not sys.argv[1:]
path = pathlib.Path(__file__).with_name('native-window-feedback.py')
original = path.read_text()
launch_start = original.index("   web=s.host.launch('warlock',")
launch_end = original.index('   def text():\n', launch_start)
launch = r'''   from recovery_profile import Profile,descriptor
   from shell_preferences import Store as RecoverySettings
   from shortcut_preferences import Store as RecoveryShortcuts
   from motion_preferences import Store as RecoveryMotion
   from taskbar_preferences import Store as RecoveryPins
   recovery_source=pathlib.Path(env['XDG_STATE_HOME'])
   saved_store=RecoverySettings(str(recovery_source));old=saved_store.read()
   saved_status,saved_settings=saved_store.save({**old,'values':{**old['values'],'theme':'dawn','effectsOff':True}})
   check('RecoverySourceAppearanceValidated',saved_status=='Saved')
   shortcut_store=RecoveryShortcuts(str(recovery_source));old=shortcut_store.read()
   shortcut_status,saved_shortcuts=shortcut_store.save({**old,'choices':{'applications':'alternate','system':'keep','notifications':'keep'}})
   check('RecoverySourceShortcutChoicesValidated',shortcut_status=='Saved')
   motion_store=RecoveryMotion(str(recovery_source));old=motion_store.read()
   check('RecoverySourceMotionValidated',motion_store.save({**old,'override':'reduced'})[0]=='Saved')
   pins_store=RecoveryPins(str(recovery_source));old=pins_store.read()
   check('RecoverySourcePinsValidated',pins_store.save({**old,'identities':['warlock-editor']})[0]=='Saved')
   recovery_baseline={name:(recovery_source/'warlock'/name).read_bytes() for name in ['taskbar.json','settings.json','shortcuts.json','motion.json']}
   prior_manifest=json.loads((ROOT/'qa/evidence/popup-reflow-current/manifest.json').read_text())
   prior_build=pathlib.Path(prior_manifest['nativeHost']['heldBuild'])
   check('RetainedPredecessorBuildUnchanged',sha(prior_build)==prior_manifest['nativeHost']['heldBuildSHA256'])
   prior_report=json.loads(prior_build.read_text());check('RetainedPredecessorBuildPassed',prior_report['passed'])
   prior_inputs=prior_build.parent/'inputs';prior_assets=prior_inputs/'assets'
   check('RetainedPredecessorCompiledAssetsUnchanged',all(sha(prior_assets/name)==value for name,value in prior_manifest['compiledAssets'].items()))
   check('PredecessorAndCandidateAreDifferentElmRevisions',sha(prior_assets/'elm.js')!=sha(assets/'elm.js'))
   prior_backend=OUTPUT/'predecessor-backend.py'
   prior_backend.write_text('import os,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nos.execv("/usr/bin/python3",["/usr/bin/python3","-B",'+repr(str(prior_inputs/'adapter/daemon.py'))+','+repr(str(broker_config))+'])\n')
   candidate_args=[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture),'--qa-exit-after-render','--qa-stay-open','--surface-experiment']
   prior_args=[prior_manifest['nativeHost']['path'],'--assets',str(prior_assets),'--authority-config',str(config_path),'--backend',str(prior_backend),'--qa-exit-after-render','--qa-stay-open','--surface-experiment']
   def recovery_descriptor(argv,resource_root,adapter_root,backend):
    files={str(p):sha(p) for p in [pathlib.Path(argv[0]),pathlib.Path('/usr/bin/python3'),backend,config_path,broker_config]}
    for folder in [resource_root,adapter_root]:
     for resource in folder.rglob('*'):
      if resource.is_file():files[str(resource)]=sha(resource)
    for row in pair.values():files[row['path']]=row['sha256']
    return descriptor({'schema':1,'argv':argv,'cwd':str(OUTPUT),'files':files})
   recovery_profile=Profile(OUTPUT/'recovery-profile')
   prepared=recovery_profile.prepare(recovery_descriptor(prior_args,prior_assets,prior_inputs/'adapter',prior_backend),recovery_descriptor(candidate_args,assets,ROOT/'adapter',backend_fixture),str(recovery_source))
   check('OfflineProfilePreparedBeforeHost',prepared['route']=='predecessor')
   check('CandidateRouteExplicitlySelected',recovery_profile.activate()['route']=='candidate')
   recovery_command=['/usr/bin/python3','-B',str(ROOT/'adapter/recovery_profile.py'),'--profile',str(recovery_profile.path)]
   report['recoveryProfile']={'path':str(recovery_profile.path),'manifestSHA256':sha(recovery_profile.path/'profile.json'),'baselineHashes':{name:hashlib.sha256(body).hexdigest() for name,body in recovery_baseline.items()},'predecessorBuild':str(prior_build),'predecessorBuildSHA256':sha(prior_build),'predecessorAssets':prior_manifest['compiledAssets'],'candidateAssets':current['compiledAssets'],'acceptedOmarchyPredecessor':False}
   web=s.host.launch('warlock',recovery_command+['run'],env=env);apps.append(web);recovery_managers=[web];log=OUTPUT/'warlock.log';collector=Collector()
   def stop_recovery_manager(manager):
    children=pathlib.Path('/proc',str(manager.pid),'task',str(manager.pid),'children').read_text().split()
    matches=[int(pid) for pid in children if sha(pathlib.Path('/proc',pid,'exe'))==sha(binary)]
    assert len(matches)==1,children
    os.kill(matches[0],signal.SIGTERM);manager.wait(timeout=5)
'''
adapted = original[:launch_start] + launch + original[launch_end:]
start = adapted.index('     # Establish the original attached, observed surface before user input.\n')
end = adapted.index('    elif DENSE:\n', start)
branch = r'''     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     def recovery_settings():return body_for('settings')
     def help_button(label):
      body=recovery_settings()
      return next((b for b in body['buttons'] if b['accessibleName']==label and not b['disabled']),None) if body else None
     bar_route('Open settings');wait(lambda:help_button('Dismiss help'))
     keyboard_button('Dismiss help',28);wait(lambda:help_button('Show help'))
     check('GuidanceDismissedBeforeActualHostLoss','Keyboard navigation' not in recovery_settings()['text'])
     key(1);wait(closed)
     native_before=facts()['facts'];windows_before=[w['incarnation'] for w in native_before['windows']]
     requests_before=len(journal())
     candidate_home=recovery_profile.path/'candidate-state'
     candidate_settings=RecoverySettings(str(candidate_home));old=candidate_settings.read()
     check('CandidateEditSavedSeparately',candidate_settings.save({**old,'values':{**old['values'],'theme':'high-contrast'}})[0]=='Saved')
     def managed_host_pid(manager):
      children=pathlib.Path('/proc',str(manager.pid),'task',str(manager.pid),'children').read_text().split()
      matches=[int(pid) for pid in children if sha(pathlib.Path('/proc',pid,'exe'))==sha(binary)]
      check('OneExactOwnedHostBelowRecoveryManager',len(matches)==1,children=children)
      return matches[0]
     candidate_host_pid=managed_host_pid(web)
     os.kill(candidate_host_pid,signal.SIGTERM)
     wait(lambda:web.poll() is not None)
     check('UnexpectedCandidateHostExitObserved',web.returncode==0 and not pathlib.Path('/proc',str(candidate_host_pid)).exists(),hostPid=candidate_host_pid,managerPid=web.pid,exitCode=web.returncode)
     check('ApplicationsSurviveHostLoss',[w['incarnation'] for w in facts()['facts']['windows']]==windows_before and fixture.poll() is None)
     broken_state=candidate_home/'warlock/settings.json';broken_state.write_text('{"schema":999,"preserved":"candidate failed"}')
     broken_bytes=broken_state.read_bytes()
     helper(recovery_command+['rollback'])
     rollback_result=json.loads((OUTPUT/('feedback-helper-'+str(sequence)+'.log')).read_text().splitlines()[-1])
     check('DocumentedOfflineRollbackSucceededWithoutHost',rollback_result['status']=='Recovered' and web.poll()==0,result=rollback_result)
     helper(recovery_command+['status'])
     status_result=json.loads((OUTPUT/('feedback-helper-'+str(sequence)+'.log')).read_text().splitlines()[-1])
     restored_home=recovery_profile.path/status_result['stateHome']
     check('CompatiblePreferenceBytesRecovered',all((restored_home/'warlock'/name).read_bytes()==body for name,body in recovery_baseline.items()))
     check('DamagedCandidatePreferencesPreserved',broken_state.read_bytes()==broken_bytes)
     web=s.host.launch('warlock-predecessor-recovered',recovery_command+['run'],env=env);apps.append(web);recovery_managers.append(web);log=OUTPUT/'warlock-predecessor-recovered.log';collector=Collector()
     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     check('NativePredecessorRecoversWithoutWindowEffectReplay',not journal() and [w['incarnation'] for w in facts()['facts']['windows']]==windows_before)
     bar_route('Open settings');wait(lambda:recovery_settings() and frames('shell-settings') and frames('shortcut-preferences') and frames('motion-preferences'))
     check('PredecessorObservedCompatibleSettings',frames('shell-settings')[-1]['snapshot']==saved_settings)
     check('PredecessorObservedExplicitShortcutChoices',frames('shortcut-preferences')[-1]['snapshot']==saved_shortcuts)
     check('PredecessorObservedCompatibleMotion',frames('motion-preferences')[-1]['snapshot']['override']=='reduced')
     keyboard_button('Dismiss help',28);wait(lambda:help_button('Show help'))
     popup_capture('offline-recovered-predecessor-settings')
     capture=report['popupCaptures'][-1]
     check('RecoveredPredecessorHasPaintedNativeControls',bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     key(1);wait(closed)
     wait(lambda:facts()['facts']['focused']==native_before['focused'])
     check('RecoveredPredecessorAcceptsPhysicalKeyboardDismissal',closed() and facts()['facts']['focused']==native_before['focused'],expected=native_before['focused'],facts=facts())
     helper(recovery_command+['rollback'])
     # Active predecessor owns the profile, so a second rollback must refuse.
'''
# Refusal helper is a deliberate negative; do not weaken the original helper's
# normal-exit oracle. Exercise it directly and retain its exact nonzero outcome.
branch = branch[:branch.index("     helper(recovery_command+['rollback'])\n     # Active predecessor")]
branch += r'''     locked_result=subprocess.run(recovery_command+['rollback'],env=env,text=True,capture_output=True,timeout=5)
     report['activePredecessorRollback']={'exitCode':locked_result.returncode,'stdout':locked_result.stdout,'stderr':locked_result.stderr}
     check('ActivePredecessorPreventsCompetingRecovery',locked_result.returncode==2 and json.loads(locked_result.stdout)['status']=='Refused')
     predecessor_pid=managed_host_pid(web);os.kill(predecessor_pid,signal.SIGTERM);wait(lambda:web.poll() is not None)
     check('RecoveredPredecessorNormalOwnedExit',web.returncode==0)
     check('ApplicationDraftsRemainConnectedAfterDrill',[w['incarnation'] for w in facts()['facts']['windows']]==windows_before and fixture.poll() is None)
     report['nativeOfflineRecoveryObserved']=True
     report['missingObservations']=['Accepted Omarchy predecessor and full release package/dependency completeness.','Main-session reversible deployment with existing user drafts.','Applicable native AT and independent original-scenario acceptance.']
'''
adapted = adapted[:start] + branch + adapted[end:]
cleanup = "     else:owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5)"
assert adapted.count(cleanup) == 1
adapted = adapted.replace(cleanup, "     elif proc in globals().get('recovery_managers',[]):stop_recovery_manager(proc)\n" + cleanup)
adapted = adapted.replace("'native-keyboard-shell-' if KEYBOARD", "'native-offline-recovery-' if KEYBOARD")
needle = '\ntry:\n'
assert adapted.count(needle) == 1
packet = {'originalPath': str(path), 'originalSHA256': hashlib.sha256(original.encode()).hexdigest(),
    'change': 'Use production recovery profiles for current/retained host launches; replace only the keyboard journey with original offline-recovery. Exact private native pair, clocks and normal cleanup retained.'}
adapted = adapted.replace(needle, "\nreport.update(requirements=['ELM-UI-020'],scenarios=['offline-recovery'],scope='Actual private native host loss after dismissed help, standalone CLI rollback, distinct retained Warlock predecessor, compatible preference readback, native controls/physical keyboard and surviving applications. Accepted Omarchy deployment, AT and independent acceptance remain open.',nativeOfflineRecoveryObserved=False,recoveryRunner=" + repr(packet) + ")\n" + needle)
sys.argv = [str(path), '--keyboard-shell']
exec(compile(adapted, str(path), 'exec'), globals())
