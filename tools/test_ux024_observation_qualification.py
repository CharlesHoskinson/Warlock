"""Source-first fixed private overlay contracts; no compositor or compiler."""
import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

class Controls(unittest.TestCase):
    def test_exact_variants_only(self):
        for variant in ('baseline','candidate'):
            q.require_variant(variant)
        for value in ('',None,'native','candidate-extra',True):
            with self.assertRaises(ValueError): q.require_variant(value)
    def test_baseline_selects_only_four_fixtures(self):
        rows=[{'kind':'fixture','path':'qa/test'}, {'kind':'production','path':'src/model'}]
        self.assertEqual(q.selected_rows({'variant':'baseline','rows':rows}),rows[:1])
        self.assertEqual(q.selected_rows({'variant':'candidate','rows':rows}),rows)
    def test_private_stage_rejects_existing_wrong_preimage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage=root/'stage';stage.mkdir();(stage/'a.hs').write_text('wrong')
            post=root/'post';post.write_text('next')
            row={'path':'haskell/a.hs','beforeSha256':q.sha_bytes(b'old'),'postPath':str(post),'postSha256':q.sha_bytes(b'next'),'kind':'production'}
            with self.assertRaises(ValueError): q.stage_rows({'variant':'candidate','rows':[row]},stage,'haskell/')
            self.assertEqual((stage/'a.hs').read_text(),'wrong')
    def test_private_stage_exact_body_and_membership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage=root/'stage';stage.mkdir();post=root/'post';post.write_text('next')
            row={'path':'haskell/New.hs','beforeSha256':None,'postPath':str(post),'postSha256':q.sha_bytes(b'next'),'kind':'production'}
            expected=q.stage_rows({'variant':'candidate','rows':[row]},stage,'haskell/')
            self.assertEqual((stage/'New.hs').read_bytes(),b'next')
            self.assertEqual(expected,{'New.hs':q.sha_bytes(b'next')})
    def test_changed_post_refuses_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage=root/'stage';stage.mkdir();post=root/'post';post.write_text('changed')
            row={'path':'haskell/New.hs','beforeSha256':None,'postPath':str(post),'postSha256':q.sha_bytes(b'next'),'kind':'production'}
            with self.assertRaises(ValueError):q.stage_rows({'variant':'candidate','rows':[row]},stage,'haskell/')
            self.assertFalse((stage/'New.hs').exists())
    def test_stage_rejects_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target=root/'body';target.write_text('x');alias=root/'alias';alias.symlink_to(target)
            with self.assertRaises(ValueError):q.read_regular(alias)
    def test_projected_map_preserves_unselected_source(self):
        data={'variant':'baseline','rows':[{'path':'haskell/New.hs','kind':'production','postSha256':'a'*64},{'path':'haskell/test/Main.hs','kind':'fixture','postSha256':'b'*64}]}
        self.assertEqual(q.projected(data,{'Old.hs':'c'*64,'test/Main.hs':'d'*64},'haskell/'),{'Old.hs':'c'*64,'test/Main.hs':'b'*64})
    def test_report_requires_literal_success_and_actual_seed_inventory(self):
        value={'schema':1,'passed':True,'nativeAcceptance':False,'providerAcceptance':False,'classification':'component-pass','caseCount':30,'seedSampleCount':32,'failures':[],'seedFailures':[],'imageSha256':'a'*64,'fixtureSha256':'b'*64,'checks':[{'name':n,'passed':True} for n in q.ELM_NAMES],'observed':{'preconditions':dict.fromkeys(q.ELM_SETUP,True),'seeded':{'seeds':list(range(32)),'samples':[{'seed':n,'variant':n%8,'eligibleGroup':n%8==0,'noMutation':True,'noFocus':True,'nativeAvailable':False} for n in range(32)]}}}
        q.validate_elm_result(value,'a'*64,'b'*64)
        for key,bad in [('passed',False),('caseCount',0),('nativeAcceptance',True),('classification','semantic-red')]:
            wrong=dict(value);wrong[key]=bad
            with self.assertRaises(ValueError):q.validate_elm_result(wrong,'a'*64,'b'*64)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--module',required=True);a,rest=p.parse_known_args()
    spec=importlib.util.spec_from_file_location('fixed_observation_qualification',a.module);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    unittest.main(argv=[__file__,*rest])
