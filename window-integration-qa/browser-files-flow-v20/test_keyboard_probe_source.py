"""Public ABI read-only source review; no compositor is loaded."""
from pathlib import Path
import hashlib,json,unittest
B=Path(__file__).resolve().parent;N=B/'native-keyboard-probe';OLD=B.parent/'qt-modal-private-v9/native-probe'
class Probe(unittest.TestCase):
 def test_original_probe_reconstructs_byte_exact(self):
  new=(N/'probe.cpp').read_text();new=new.replace('#include <hyprland/src/devices/IKeyboard.hpp>\n','',1)
  new=new.replace('CHyprSignalListener keyboardListener;\nstd::vector<std::string> keyboardEvents;\nuint64_t keyboardSequence=0;\n','',1)
  begin=new.index('std::string keyboardState(){');end=new.index('int luaState(',begin);new=new[:begin]+new[end:]
  new=new.replace('HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","keyboard_state",luaKeyboardState);HyprlandAPI::addLuaFunction(handle,"qt_modal_probe","keyboard_events",luaKeyboardEvents);observeKeyboard();','',1)
  new=new.replace('keyboardListener.reset();keyboardEvents.clear();keyboardSequence=0;','',1)
  self.assertEqual(new,(OLD/'probe.cpp').read_text())
 def test_exact_public_seat_surface_query_and_strong_keyboard_locks(self):
  s=(N/'probe.cpp').read_text();self.assertIn('m_state.keyboardFocus.lock()',s);self.assertIn('m_state.keyboardFocusResource.lock()',s)
  self.assertIn('query().type(Desktop::View::VIEW_TYPE_WINDOW).surface(surface).runWindow()',s);self.assertIn('g_pSeatManager->m_keyboard.lock()',s)
 def test_original_focus_and_keyboard_routes_separate(self):
  s=(N/'probe.cpp').read_text();self.assertIn('"keyboardOwner":{}',s);self.assertIn('"coreNativeFocus":{}',s);self.assertIn('bool(seatResource)',s)
 def test_new_keyboard_code_is_read_only(self):
  s=(N/'probe.cpp').read_text();part=s[s.index('std::string keyboardState(){'):s.index('int luaState(')]
  for forbidden in ('reinterpret_cast','setKeyboard(', 'sendKeyboard','info.cancelled=', 'info.cancelled =','hl.dispatch','m_state.keyboardFocus=','m_xkbState='):
   self.assertNotIn(forbidden,part)
 def test_bounded_event_observer_reset_and_symbol_observation_label(self):
  s=(N/'probe.cpp').read_text();self.assertIn('keyboardEvents.size()==512',s);self.assertIn('seatKeySymAtObservation',s)
  self.assertIn('keyboardListener.reset();keyboardEvents.clear();keyboardSequence=0;',s);self.assertNotIn('"delivered":true',s)
 def test_actual_compiled_abi_dependency_bytes_and_binary(self):
  report=json.loads((N/'build-final-report.json').read_text());self.assertEqual(report['exitCode'],0);self.assertFalse(report['nativeLoaded']);self.assertIn('-Werror',report['command'])
  self.assertEqual(hashlib.sha256((N/'libqt-modal-probe.so').read_bytes()).hexdigest(),report['binarySHA256'])
  for row in report['sourceDependencies']:self.assertEqual(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest(),row['sha256'],row['path'])
 def test_source_primary_event_observation_precedes_core_dispatch(self):
  source=(B/'continuation-primary-InputManager.cpp').read_text();part=source[source.index('void CInputManager::onKeyboardKey'):]
  self.assertLess(part.index('Event::bus()->m_events.input.keyboard.key.emit'),part.index('g_pSeatManager->sendKeyboardKey'))
 def test_private_authorization_and_original_description_unchanged(self):
  s=(N/'probe.cpp').read_text();old=(OLD/'probe.cpp').read_text()
  start=s.index('void authorize()');end=s.index('\n}',start);ostart=old.index('void authorize()');oend=old.index('\n}',ostart)
  self.assertEqual(s[start:end],old[ostart:oend]);self.assertIn('Private read-only Qt modal QA observation',s)
if __name__=='__main__':unittest.main()
