from pathlib import Path
import unittest
B=Path(__file__).resolve().parent;C=B/'native-candidate';OLD=B.parent/'toolkit-interruption-v5/native-candidate'

class FocusSource(unittest.TestCase):
 def test_only_exact_reviewed_delta_changes_native_sources(self):
  for path in OLD.iterdir():
   if path.suffix not in ('.cpp','.hpp','.lua'):continue
   actual=(C/path.name).read_text();original=path.read_text()
   if path.name=='familyBridge.cpp':actual=actual.replace('#include "dragBridge.hpp"\n','').replace('    if (preserveCapturedGestureFocus(window, state->window(), reason))\n        return;\n','')
   if path.name=='dragBridge.hpp':actual=actual.replace('#include <hyprland/src/desktop/state/FocusState.hpp>\n','').replace('\nbool preserveCapturedGestureFocus(const PHLWINDOW& owner, const PHLWINDOW& independentlyFocused, Desktop::eFocusReason reason);\n','')
   if path.name=='dragBridge.cpp':
    start=actual.index('bool preserveCapturedGestureFocus(');end=actual.index('void initDragBridge()',start);actual=actual[:start]+actual[end:]
   self.assertEqual(actual,original,path.name)
 def test_guard_precedes_modal_redirection_and_ordinary_delegation(self):
  text=(C/'familyBridge.cpp').read_text();body=text[text.index('void hookedFocus('):text.index('PHLWINDOW hookedHit(')]
  self.assertLess(body.index('preserveCapturedGestureFocus('),body.index('modalTarget(window)'));self.assertLess(body.index('modalTarget(window)'),body.index('reinterpret_cast<FocusFn>'))
 def test_no_focus_input_controller_or_geometry_mutation_in_guard(self):
  text=(C/'dragBridge.cpp').read_text();body=text[text.index('bool preserveCapturedGestureFocus('):text.index('void initDragBridge()')]
  for token in ('FOCUS_REASON_FFM','validMapped(owner)','validMapped(independentlyFocused)','independentlyFocused == owner','sameGesture(target)','target->window() == owner','mode() == gesture->mode','!enabled->value()','owner->isHidden()','!owner->m_isFloating'):self.assertIn(token,body)
  for token in ('fullWindowFocus(','rawWindowFocus(','endDragTarget(','gesture.reset(', 'setPosition','sendPointer','setPointerFocus(','.lock()'):self.assertNotIn(token,body)

if __name__=='__main__':unittest.main(verbosity=2)
