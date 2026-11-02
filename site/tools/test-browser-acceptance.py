#!/usr/bin/env python3
import importlib.util, itertools, random, re, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('acceptance',Path(__file__).with_name('browser-acceptance.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Acceptance(unittest.TestCase):
 def test_negative_results(self):
  self.assertTrue(m.evaluate_result('settings','operation unsupported',None,False))
  self.assertTrue(m.evaluate_result('settings','scenario timed out',None,False))
  self.assertTrue(m.evaluate_result('settings','', 'system',False))
  self.assertTrue(m.evaluate_result('transfer','',None,False))
  self.assertTrue(m.evaluate_result('settings','','settings',True,False))
 def test_every_scenario_has_a_specific_entry_probe(self):
  self.assertEqual(set(m.SCENARIOS),set(m.ACTIONS))
  self.assertEqual(m.ACTIONS['transfer'],('popup','overview:destination:2'))
  self.assertEqual(m.ACTIONS['launcher'],('field','control:search'))
 def test_browser_gate_requires_every_engine(self):
  self.assertFalse(m.browser_failed([{'result':'PASS'}]))
  self.assertTrue(m.browser_failed([{'result':'PASS'},{'result':'NOT RUN'}]))
  self.assertTrue(m.browser_failed([{'result':'FAIL'}]))
 def test_good_mode(self):self.assertIsNone(m.evaluate_result('settings','','settings',True))
 def test_jump_and_behavior(self):
  self.assertEqual(m.MODES['application-actions'], 'jump')
  self.assertTrue(m.evaluate_result('application-actions','','jump',False))
  self.assertIsNone(m.evaluate_result('application-actions','','jump',True))
 def test_architecture_probe_exhaustive_contract(self):
  keys=('hasProductionBoundary','mentionsElmAndHaskell','mentionsNoPythonShip','tocLinksBoundary')
  for bits in itertools.product((False,True),repeat=len(keys)):
   probe=dict(zip(keys,bits))
   res=m.evaluate_architecture_probe(probe)
   if all(bits): self.assertIsNone(res)
   else: self.assertIsInstance(res,str); self.assertTrue(len(res)>0)
 def test_homepage_probe_exhaustive_and_seeded_fuzz(self):
  bool_keys=(
   'honestCounts','walkthroughPresent','tierExplorerOk','mvpQuickstartOk','workbenchKeyboardOk',
   'mobileEscapeReturnOk','elmThreeThemeCycleOk','getStartedStatusOk',
   'componentsSpecimenOk','architectureBoundaryOk','routeSearchOk','offlineOk'
  )
  for bits in itertools.product((False,True),repeat=len(bool_keys)):
   probe={'inlineStyles':0,'styleAttrs':0,**dict(zip(bool_keys,bits))}
   res=m.evaluate_homepage_probe(probe)
   if all(bits): self.assertIsNone(res)
   else: self.assertIsInstance(res,str); self.assertTrue(len(res)>0)
  rng=random.Random(20261102)
  for _ in range(500):
   inline_n=rng.choice([-1,0,1,2,17])
   attr_n=rng.choice([-1,0,1,3,42])
   bits=[rng.choice([False,True]) for _ in bool_keys]
   probe={'inlineStyles':inline_n,'styleAttrs':attr_n,**dict(zip(bool_keys,bits))}
   res=m.evaluate_homepage_probe(probe)
   if inline_n==0 and attr_n==0 and all(bits): self.assertIsNone(res)
   elif inline_n!=0 or attr_n!=0: self.assertEqual(res,'homepage DOM is not CSS-free')
   else: self.assertIsInstance(res,str)
 def test_site_beta_status_elm_partition_invariants(self):
  site_root=Path(__file__).resolve().parents[1]
  elm_src=site_root/'src'/'SiteBetaStatus.elm'
  if not elm_src.is_file(): return
  raw=elm_src.read_text(encoding='utf-8')
  code=re.sub(r'\{-.*?\-\}|"(?:\\.|[^"\\])*"|--[^\n]*',lambda x:x.group(0) if x.group(0).startswith('"') else '',raw,flags=re.S)
  self.assertRegex(code,r'\bmodule\s+SiteBetaStatus\s+exposing\b')
  self.assertNotRegex(code,r'\bModel\s*\(\.\.\)')
  self.assertNotIn('Debug.',code)
  self.assertNotIn('Html.node "style"',code)
  self.assertNotIn('Attr.style',code)
  self.assertIn('selectedOperationSucceeded',code)
  for payload_trigger in ('test-drive/runtime/','test-drive/bootstrap.js','desktop-stage.js','elm.js'):
   self.assertNotIn(payload_trigger,code)
  mvp_tracks=re.findall(r'track\s*=\s*(TrackBrowserStage|TrackProtectedCpu|TrackOmarchyTrial)\b',code)
  self.assertEqual(mvp_tracks,['TrackBrowserStage','TrackProtectedCpu','TrackOmarchyTrial'])
  self.assertIn('qa_cpu.py --review',code)
  self.assertIn('10 focused ui-origin suites',code)
  self.assertIn('--custody',code)
  self.assertIn('--backend',code)
  self.assertIn('6e6ad828c',code)
  self.assertIn('retained failed batch',code)
  self.assertIn('ELM-TEA-004',code)
  self.assertIn('separate historical source-bound reports',code)
  self.assertEqual(len(re.findall(r'focusSeq\s*=\s*nextSeq',code)),6)
  gs_html=(site_root/'get-started'/'index.html').read_text(encoding='utf-8')
  self.assertIn('id="mvp-repro"',gs_html)
  self.assertIn('href="#mvp-repro"',gs_html)
  self.assertIn('qa_cpu.py --review',gs_html)
  self.assertIn('10 focused <code>ui-origin</code> suites',gs_html)
  self.assertIn('--backend',gs_html)
  self.assertIn('6e6ad828c',gs_html)
  self.assertIn('retained failed batch',gs_html)
  self.assertIn('ELM-TEA-004',gs_html)
  self.assertIn('separate historical source-bound reports',gs_html)
  row_ids=re.findall(r'rowId\s*=\s*"([^"]+)"',code)
  tiers=re.findall(r'tier\s*=\s*(TierWholeAccepted|TierRuntimeComponent|TierOpenNativeGate)\b',code)
  hrefs=re.findall(r'\bhref\s*=\s*"([^"]+)"',code)
  self.assertEqual(len(row_ids),6)
  self.assertEqual(len(set(row_ids)),6)
  self.assertEqual(len(tiers),6)
  self.assertEqual(len(hrefs),6)
  for expected_tier in ('TierWholeAccepted','TierRuntimeComponent','TierOpenNativeGate'):
   self.assertGreaterEqual(tiers.count(expected_tier),2)
  for href in hrefs:
   rel_part=href.removeprefix('./').split('#')[0].split('?')[0]
   self.assertTrue((site_root/rel_part).is_file(),f'missing boundary link target: {href}')
if __name__=='__main__':unittest.main()
