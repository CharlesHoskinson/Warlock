"""Keyboard Settings help on the unchanged protected native session/authority.

Replace only the original nine-surface journey with a bounded help journey.
Keep its actual keyboard, six-second waits, ABI and owned cleanup.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
path=pathlib.Path(__file__).with_name('native-window-feedback.py')
original=path.read_text()
start=original.index('     # Establish the original attached, observed surface before user input.\n')
end=original.index('    elif DENSE:\n',start)
branch=r'''     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     before_writes=len(requests('shell-settings-write'))
     before_motion=len(requests('motion-preferences-write'))
     before_window=len(journal())
     def settings_body():return body_for('settings')
     def help_button(label):
      body=settings_body()
      return next((b for b in body['buttons'] if b['accessibleName']==label and not b['disabled']),None) if body else None
     bar_route('Open settings')
     body=wait(lambda:settings_body() if help_button('Dismiss help') else None)
     check('HelpOfferedInActualNativeSettings',all(label in body['text'] for label in ['Keyboard navigation','Keeping your preferences','When an action is not confirmed']),body=body)
     keyboard_button('Dawn theme',28)
     wait(lambda:next((b for b in settings_body()['buttons'] if b['accessibleName']=='Save settings' and not b['disabled']),None))
     keyboard_button('Dismiss help',28)
     wait(lambda:help_button('Show help'))
     check('NativeHelpDismissalPreservesUnsavedEdit',any(b['accessibleName']=='Save settings' and not b['disabled'] for b in settings_body()['buttons']) and 'Keyboard navigation' not in settings_body()['text'],body=settings_body())
     key(1);wait(closed)
     bar_route('Open settings');wait(lambda:help_button('Show help'))
     check('SettingsReopenKeepsHelpDismissedForSession','Keyboard navigation' not in settings_body()['text'],body=settings_body())
     keyboard_button('Show help',28);wait(lambda:help_button('Dismiss help'))
     body=settings_body()
     check('NativeKeyboardReopensHelpWithSameFocusedControl',body['focus']==help_button('Dismiss help')['id'] and all(label in body['text'] for label in ['Keyboard navigation','Keeping your preferences','When an action is not confirmed']),body=body)
     popup_capture('keyboard-settings-help')
     key(107)
     wait(lambda:settings_body() if settings_body() and any(b['accessibleName']=='Refresh settings' and b['id']==settings_body()['focus'] for b in settings_body()['buttons']) else None)
     check('HelpDoesNotTrapNativeKeyboardNavigation',True,body=settings_body())
     key(1);wait(closed)
     check('HelpNeverWritesPreferencesOrReplaysWindowActions',len(requests('shell-settings-write'))==before_writes and len(requests('motion-preferences-write'))==before_motion and len(journal())==before_window)
     event_path=control.with_suffix('.events.jsonl')
     pointer_events=[json.loads(line) for line in event_path.read_text().splitlines() if json.loads(line)['kind'] in ['pressed','released']]
     check('HelpJourneyUsesZeroPointerEvents',not pointer_events and not any(str(POINTER) in row['command'] for row in report['helpers']),events=pointer_events)
     report['pointerEventsInjected']=0
     report['nativeSettingsHelpObserved']=True
'''
adapted=original[:start]+branch+original[end:]
adapted=adapted.replace("'native-keyboard-shell-' if KEYBOARD", "'native-settings-help-' if KEYBOARD")
needle='try:\n with host.PrivateHyprSession';assert adapted.count(needle)==1
packet={'originalPath':str(path),'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'change':'Replace only original KEYBOARD journey after its persistent real-input helpers; original timing, native authority, exact ABI/private sessions and cleanup preserved.'}
adapted=adapted.replace(needle,"report.update(requirements=['ELM-UI-020','ELM-UX-023'],scenarios=['first-use','keyboard-settings'],scope='Native keyboard open/dismiss/reopen Settings help with unchanged effect counts and actual focus/pixels. Shortcut mapping/conflict persistence, offline rollback, native AT and independent acceptance remain open.',nativeSettingsHelpRunner="+repr(packet)+")\n"+needle)
sys.argv=[str(path),'--keyboard-shell']
exec(compile(adapted,str(path),'exec'),globals())
