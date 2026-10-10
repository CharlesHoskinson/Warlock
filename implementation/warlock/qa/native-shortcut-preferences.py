"""Actual customized-shortcut conflict/choice journey on the protected host.

Keep the original physical keyboard, six-second observations, owning tuple,
private sessions and owned cleanup. F12 is a fixture's explicit user override,
not a product default or a workaround for focus restoration.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
path=pathlib.Path(__file__).with_name('native-window-feedback.py');original=path.read_text()
start=original.index('     # Establish the original attached, observed surface before user input.\n');end=original.index('    elif DENSE:\n',start)
branch=r'''     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     def settings_body():return body_for('settings')
     def button(label):
      body=settings_body()
      return next((b for b in body['buttons'] if b['accessibleName']==label),None) if body else None
     def existing():return [r for r in s.data('binds') if r.get('description') in ['Existing Apps shortcut','User Apps shortcut']]
     old_bindings=existing();check('ExplicitCustomizedNativeBindingsExist',len(old_bindings)==2,bindings=old_bindings)
     state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/shortcuts.json'
     def stored():return json.loads(state_file.read_text()) if state_file.exists() else None
     before=len(requests('shortcut-preferences-write'));before_windows=len(journal())
     bar_route('Open settings');wait(lambda:button('Use Apps menu default'))
     body=wait(lambda:settings_body() if button('Use Apps menu alternative') and not button('Use Apps menu alternative')['disabled'] else None)
     check('LiveConflictIsVisibleAndDefaultDisabled',button('Use Apps menu default')['disabled'] and 'Unavailable: existing binding' in body['text'],body=body)
     keyboard_button('Dismiss help',28);wait(lambda:button('Show help'))
     keyboard_button('Use Apps menu alternative',28)
     keyboard_button('Use System menu default',28)
     keyboard_button('Keep existing shortcut for Notification history',28)
     check('UnsavedChoicesDoNotWriteOrMutateBindings',not stored() and len(requests('shortcut-preferences-write'))==before and existing()==old_bindings)
     keyboard_button('Save shortcut choices',28)
     saved=wait(lambda:stored() if stored() and stored()['choices']=={'applications':'alternate','system':'default','notifications':'keep'} else None)
     wait(lambda:settings_body() if 'Shortcut choices saved and active' in settings_body()['text'] else None)
     check('SavedChoiceHasOneCorrelatedNativeWrite',len(requests('shortcut-preferences-write'))==before+1,requests=requests('shortcut-preferences-write'),stored=saved)
     check('ForeignCustomizedBindingsPreservedExactly',existing()==old_bindings,bindings=existing())
     check('HelpRemainsReachableAfterChoice',button('Show help') and not button('Show help')['disabled'])
     keyboard_button('Show help',28);wait(lambda:button('Dismiss help'));popup_capture('shortcut-choices-saved');key(1);wait(closed)
     chord([125,29,56],57);wait(lambda:(body:=body_for('applications')) and body['focus']=='launcher-search' and any(b['accessibleName']=='Actions for A Warlock Editor' and not b['disabled'] for b in body['buttons']));check('ChosenAlternativeOpensActualAppsMenu',True,body=body_for('applications'));key(1);wait(closed)
     key(88);wait(lambda:(body:=body_for('applications')) and body['focus']=='launcher-search' and any(b['accessibleName']=='Actions for A Warlock Editor' and not b['disabled'] for b in body['buttons']));check('ExistingUserOverrideStillOpensActualAppsMenu',True,body=body_for('applications'));key(1);wait(closed)
     check('ReopenedAppsEscapeClosesAndRestoresBarFocus',bool(wait(bar_focus)),body=bar_body())
     for cycle in range(3):
      open_apps();key(15)
      body=wait(lambda:(body:=body_for('applications')) and any(b['id']==body['focus'] and not b['disabled'] for b in body['buttons']) and body)
      check('RepeatedAppsKeyboardTraversal'+str(cycle),body['focus']!='launcher-search',body=body)
      key(1);wait(closed)
      check('RepeatedAppsReleaseRestoresCurrentBarFocus'+str(cycle),bool(wait(bar_focus)),body=bar_body())
     primary=next(w['incarnation'] for w in client.snapshot('29000')['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')
     peer=next(w['incarnation'] for w in client.snapshot('29001')['windows'] if w['label']=='ELM-ACTIVATION-PEER')
     chord([125,56],57);wait(lambda:facts()['facts']['focused']==peer)
     check('ConflictingOriginalShortcutKeepsItsNativeMeaning',closed() and facts()['facts']['focused']==peer)
     bar_route('Open settings');wait(lambda:button('Dismiss help'))
     check('SavedDecisionsReopenWithoutAnotherWrite',stored()==saved and len(requests('shortcut-preferences-write'))==before+1,stored=stored())
     keyboard_button('Refresh shortcut choices',28)
     wait(lambda:settings_body() if 'Shortcut choices loaded' in settings_body()['text'] else None)
     check('RefreshDoesNotRepeatNativeApplication',len(requests('shortcut-preferences-write'))==before+1 and stored()==saved)
     key(1);wait(closed)
     rejected=client.shortcut_bindings('31000',saved['choices'],'0'*64)
     duplicate=client.shortcut_bindings('31000',saved['choices'],'0'*64)
     check('StaleFingerprintAndDuplicateCannotChangeNativeMappings',rejected['status']=='Refused' and duplicate==rejected and rejected['inventory']['applications']['active']=='alternate' and existing()==old_bindings)
     event_path=control.with_suffix('.events.jsonl')
     pointer_events=[json.loads(line) for line in event_path.read_text().splitlines() if json.loads(line)['kind'] in ['pressed','released']]
     check('OriginalSettingsJourneyUsesZeroPointerEvents',not pointer_events and not any(str(POINTER) in row['command'] for row in report['helpers']),events=pointer_events)
     check('PreferenceJourneyNeverEmitsWindowMutation',len(journal())==before_windows)
     report['pointerEventsInjected']=0;report['nativeShortcutChoicesObserved']=True
'''
adapted=original[:start]+branch+original[end:]
needle="      chord([125,56],57)\n      return wait(lambda:(body:=body_for('applications'))";assert adapted.count(needle)==1
adapted=adapted.replace(needle,"      key(88)\n      return wait(lambda:(body:=body_for('applications'))")
needle="if KEYBOARD or DRAG:LUA+=(ROOT/'native/shell-bindings.lua').read_bytes()";assert adapted.count(needle)==1
fixture=r'''if KEYBOARD:
 LUA+=b'\nhl.bind("SUPER + ALT + SPACE", function() hl.dsp.window.focus({window="title:ELM-ACTIVATION-PEER"}) end, {description="Existing Apps shortcut"})\nhl.bind("F12", function() hl.plugin.warlock.apps_menu() end, {description="User Apps shortcut"})\n'
'''
adapted=adapted.replace(needle,needle+'\n'+fixture)
adapted=adapted.replace("'native-keyboard-shell-' if KEYBOARD","'native-shortcut-choices-' if KEYBOARD")
needle='try:\n with host.PrivateHyprSession';assert adapted.count(needle)==1
packet={'originalPath':str(path),'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'change':'Explicit user F12 override and conflicting default Apps focus route, then only bounded original KEYBOARD journey replaced. Native ABI/authority, six-second waits, private sessions and cleanup unchanged.'}
adapted=adapted.replace(needle,"report.update(requirements=['ELM-UI-020','ELM-UX-023'],scenarios=['first-use','keyboard-settings','keyboard-launcher'],scope='Actual live conflict, explicit keyboard preference choices, exact private save and native default/alternate/user-override recipients, repeated Apps traversal/dismissal/focus, no refresh/repeated-stale mutation. Whole host restart, offline recovery, complete Omarchy inventory, full launcher operation, AT and independent acceptance separate.',nativeShortcutChoicesRunner="+repr(packet)+")\n"+needle)
sys.argv=[str(path),'--keyboard-shell'];exec(compile(adapted,str(path),'exec'),globals())
