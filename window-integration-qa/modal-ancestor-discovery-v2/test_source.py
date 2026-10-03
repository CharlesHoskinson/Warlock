from pathlib import Path
import json,unittest
B=Path(__file__).resolve().parent;C=B/'native-candidate';V18=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/cross-output-design/native-atlas-v18')
class SourceTests(unittest.TestCase):
 def test_exact_upstream_geometric_winner_except_modal_shadow(self):
  upstream=(B/'primary/ViewHitTester.cpp').read_text();start=upstream.index('PHLWINDOW CViewHitTester::windowAt(');end=upstream.index('SP<CWLSurfaceResource> CViewHitTester::windowSurfaceAt',start);body=upstream[start:end]
  body=body.replace('PHLWINDOW CViewHitTester::windowAt(const Vector2D& pos, uint16_t properties, PHLWINDOW ignoreWindow) const {','PHLWINDOW modalGeometricWindowAt(const Vector2D& pos, uint16_t properties, PHLWINDOW ignoreWindow) {').replace('m_tracker.windows()','Desktop::viewState()->windows()')
  body=body.replace('    static auto PMODALPARENTBLOCKING  = CConfigValue<Config::INTEGER>("general:modal_parent_blocking");\n','').replace('    const auto  isShadowedByModal = [](PHLWINDOW w) -> bool {\n        return *PMODALPARENTBLOCKING && w->m_xdgSurface && w->m_xdgSurface->m_toplevel && w->m_xdgSurface->m_toplevel->anyChildModal();\n    };\n','').replace(' && !isShadowedByModal(w)','')
  actual=(C/'ancestorHit.cpp').read_text();self.assertEqual(actual[actual.index('PHLWINDOW modalGeometricWindowAt('):],body)
 def test_global_hit_hook_and_focus_target_unchanged(self):
  old=(V18/'familyBridge.cpp').read_text();new=(C/'familyBridge.cpp').read_text()
  for start,end in [('PHLWINDOW modalTarget','void syncPinnedFamilies'),('PHLWINDOW hookedHit','void hookedRaise')]:
   original=old[old.index(start):old.index(end)];current=new[new.index(start):new.index(end)]
   if start=='PHLWINDOW modalTarget':current=current[:current.index('bool modalPointHasAuthority')]
   self.assertEqual(original,current)
 def test_all_existing_input_guards_precede_discovery(self):
  source=(C/'familyBridge.cpp').read_text();listener=source[source.index('modalButtonListener ='):];discovery=listener.index('modalGeometricWindowAt(')
  for token in ('info.cancelled ||','isSessionLocked()', 'm_exclusiveLSes', 'CLICKMODE_DEFAULT','isConstrained()','hasHeldButtons()','m_seatGrab','isCaptured()','dndActive()','dragController()->target()'):
   self.assertLess(listener.index(token),discovery)
 def test_actual_input_region_and_decoration_separation(self):
  source=(C/'familyBridge.cpp').read_text();helper=source[source.index('bool modalPointHasAuthority'):source.index('void syncPinnedFamilies')]
  self.assertIn('surfaceBox->containsPoint(position)',helper);self.assertIn('windowSurfaceAt(position, owner, local)',helper);self.assertIn('getWindowBoxUnified(Desktop::View::RESERVED_EXTENTS)',helper)
  self.assertIn('!modalPointHasAuthority(owner, position)',source)
 def test_pointer_authority_revalidated_and_foreign_surface_refuses(self):
  source=(C/'familyBridge.cpp').read_text();self.assertIn('if (pointerSurface && !pointerOwner)\n                return;',source)
  self.assertIn('pointerOwner == filteredOwner',source);self.assertIn('modalGeometricWindowAt(position, properties) != owner',source);self.assertIn('pointerOwner != Desktop::viewState()->hitTest().windowAt(position, properties)',source)
 def test_protocol_branch_uses_shared_selector_and_core_x11_coordinates(self):
  source=(C/'familyBridge.cpp').read_text();helper=source[source.index('bool modalPointHasAuthority'):source.index('void syncPinnedFamilies')]
  self.assertIn('ModalRegionAuthority::bodyInput(owner->m_isX11, owner->m_X11SurfaceScaledBy',helper)
  self.assertIn('owner->wlSurface()->resource()',helper);self.assertIn('position - owner->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT)',helper);self.assertIn('resource->at(local, true).first',helper)
  selector=(C/'modalRegionAuthority.hpp').read_text();self.assertLess(selector.index('if (!x11)'),selector.index('xresource)(x11Scale)'))
  primary=(B/'primary/InputManager.cpp').read_text();self.assertIn('surfaceLocal = surfaceLocal * pFoundWindow->m_X11SurfaceScaledBy',primary)
 def test_other_native_sources_unchanged(self):
  for p in V18.iterdir():
   if p.suffix in ('.cpp','.hpp') and p.name!='familyBridge.cpp':self.assertEqual(p.read_bytes(),(C/p.name).read_bytes())
 def test_retained_actual_failure_not_a_coordinate_or_guard_failure(self):
  q=json.loads((B.parent/'qt-modal-private-v8/attempt-1/qt/report.json').read_text());self.assertTrue(q['checks'][0]['ownerBaselineCallback']['passed']);self.assertTrue(q['checks'][1]['passed']);self.assertTrue(q['checks'][2]['passed']);self.assertFalse(q['checks'][3]['passed'])
  click=q['actualQtNativeSnapshots'][-1];self.assertEqual(click['point'],[116,400]);before=q['pointerCoordinateTrace'][-1]['nativeReadOnlyBeforeButtons'];after=click['nativeReadOnlyAfterButtons']
  for snapshot in (before,after):
   self.assertIsNone(snapshot['hitOwner']);self.assertIsNone(snapshot['pointerOwner']);self.assertIsNone(snapshot['modalTarget'])
   for key in ('sessionLocked','exclusiveLayers','clickMode','constrained','heldButtons','seatGrab','captured','dnd','dragTarget'):self.assertFalse(snapshot[key])
if __name__=='__main__':unittest.main()
