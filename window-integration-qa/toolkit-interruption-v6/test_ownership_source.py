from pathlib import Path
import unittest
from run_retirement_ownership import block

B=Path(__file__).resolve().parent
C=B/'native-candidate'
OLD=B.parent/'toolkit-interruption-v4/native-candidate'

class OwnershipSource(unittest.TestCase):
    def test_only_exact_decoration_borrow_changed(self):
        before=(OLD/'dragBridge.cpp').read_text()
        change='''        // Decorations are uniquely owned by the compositor. This checked
        // synchronous borrow cannot promote their weak refs to shared owners.
        // retireCaptionIntent only resets local flags and invokes no callbacks.
        if (barRef.expired())
            continue;
        auto* const bar = barRef.get();'''
        current=(C/'dragBridge.cpp').read_text();start=current.index('bool preserveCapturedGestureFocus(');end=current.index('void initDragBridge()',start);current=current[:start]+current[end:]
        self.assertEqual(before.replace('        const auto bar = barRef.lock();',change),current)
        for path in OLD.iterdir():
            if path.suffix in ('.cpp','.hpp','.lua') and path.name!='dragBridge.cpp':
                actual=(C/path.name).read_text()
                if path.name=='familyBridge.cpp':
                    actual=actual.replace('#include "dragBridge.hpp"\n','').replace('    if (preserveCapturedGestureFocus(window, state->window(), reason))\n        return;\n','')
                if path.name=='dragBridge.hpp':
                    actual=actual.replace('#include <hyprland/src/desktop/state/FocusState.hpp>\n','').replace('\nbool preserveCapturedGestureFocus(const PHLWINDOW& owner, const PHLWINDOW& independentlyFocused, Desktop::eFocusReason reason);\n','')
                self.assertEqual(path.read_text(),actual)

    def test_unique_ownership_registration_stays_exact(self):
        text=(C/'main.cpp').read_text()
        for token in ('auto bar = makeUnique<CHyprBar>(window);','g_pGlobalState->bars.emplace_back(bar);','std::move(bar)'):
            self.assertIn(token,text)
        self.assertIn('std::vector<WP<CHyprBar>> bars;',(C/'globals.hpp').read_text())

    def test_no_borrow_across_reentrant_native_retirement(self):
        body=block((C/'dragBridge.cpp').read_text(),'int luaRetireGestureCurrent')
        self.assertLess(body.index('retireCapturedGesture(true)'),body.index('for (const auto& barRef'))
        self.assertLess(body.index('barRef.expired()'),body.index('barRef.get()'))
        self.assertNotIn('barRef.lock()',body)

    def test_borrowed_method_has_no_callback_or_ownership_operation(self):
        body=block((C/'barDeco.cpp').read_text(),'bool CHyprBar::retireCaptionIntent')
        statements=body[body.index('{')+1:body.rindex('}')]
        self.assertNotIn('(',statements)
        for token in ('m_bCancelledDown =','delete ','reset(','std::move','emit','spawn'):
            self.assertNotIn(token,statements)

if __name__=='__main__':unittest.main()
