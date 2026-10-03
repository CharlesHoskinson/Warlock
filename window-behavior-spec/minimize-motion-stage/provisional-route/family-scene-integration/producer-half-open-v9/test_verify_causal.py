import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from verify_causal import bind,compare_observation,read_image,COLORS
from raster_oracle import encode_png

EVIDENCE=Path('/home/hoskinson/window-integration-qa/family-raster-oracle-v6/attempt-private-1')
class BindingTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.directory=Path(self.t.name);self.directory.chmod(0o700)
        self.fixture=json.loads((EVIDENCE/'fixture-0-ORACLE-SECOND.json').read_text())
        self.presented=json.loads((EVIDENCE/'presented-0-ORACLE-SECOND.json').read_text())
        self.full=json.loads((EVIDENCE/'readback-0-ORACLE-SECOND.json').read_text())
        self.swap={**self.presented,'event':'swap','success':True}
        self.record={**self.full,'event':'ownedCausalReadback','kind':'member-prefix','prefixCount':3,'prefixMembers':copy.deepcopy(self.full['members']),'controls':[],
            'logicalOutput':{k:self.fixture['output'][k] for k in ('x','y','width','height')},'nativeFormat':self.full['glBuffer']['readFormat'],'nativeType':self.full['glBuffer']['readType'],
            'rgbaFilename':'causal-2-14-0-rgba.png','nativeRGBAFilename':'causal-2-14-0-native-rgba.png','rgbaSHA256':self.full['rawSHA256'],'nativeRGBASHA256':self.full['rawSHA256'],'allReadFormatBytesEqual':True}
        for field in ('rgbaFilename','nativeRGBAFilename'):
            target=self.directory/self.record[field];shutil.copyfile(EVIDENCE/'owned-readbacks'/self.full['filename'],target);target.chmod(0o600)
    def tearDown(self):self.t.cleanup()
    def call(self):return compare_observation(self.record,self.fixture,self.full,self.swap,self.presented,self.directory)
    def test_retained_actual_full_prefix_error_is_preserved(self):
        r=self.call();self.assertTrue(r['readFormatCompleteEquality']);self.assertFalse(r['RGBA']['passed']);self.assertEqual(r['RGBA']['maxChannelError'],2)
    def test_stale_sequence_refused_before_pixels(self):
        self.record['sequence']='1';self.assertRaises(ValueError,self.call)
    def test_equivalent_reordered_rectangle_keys_accepted(self):
        self.record['logicalOutput']=dict(reversed(list(self.record['logicalOutput'].items())));self.assertFalse(self.call()['RGBA']['passed'])
    def test_changed_prefix_digest_refused(self):
        self.record['prefixMembers'][0]['digest']='f'*64;self.assertRaises(ValueError,self.call)
    def test_changed_member_order_refused(self):
        self.record['members']=list(reversed(self.record['members']));self.assertRaises(ValueError,self.call)
    def test_native_read_pair_must_match_actual_query(self):
        self.record['nativeFormat']=0x1908;self.assertRaises(ValueError,self.call)
    def test_missing_swap_success_refused(self):
        self.swap['success']=False;self.assertRaises(ValueError,self.call)
    def test_prefix_does_not_substitute_for_actual_full_presentation(self):
        self.presented['accepted']=False;self.assertRaises(ValueError,self.call)
    def test_partial_or_out_of_range_prefix_refused(self):
        for n in (0,4,True):
            self.record['prefixCount']=n;self.assertRaises(ValueError,self.call)
    def test_changed_actual_full_raw_digest_refused(self):
        self.record['rgbaSHA256']='0'*64;self.assertRaises(ValueError,self.call)
    def test_symlink_evidence_refused(self):
        p=self.directory/self.record['rgbaFilename'];data=p.read_bytes();other=self.directory/'other.png';other.write_bytes(data);p.unlink();p.symlink_to(other);self.assertRaises(OSError,self.call)
    def test_false_declared_read_format_equality_refused(self):
        self.record['allReadFormatBytesEqual']=False;self.assertRaises(ValueError,self.call)
    def test_wrong_scene_token_suffix_refused(self):
        self.record['token']+='\n';self.assertRaises(ValueError,self.call)
    def test_predetermined_constant_controls_complete_exact_images(self):
        w,h=self.full['bufferWidth'],self.full['bufferHeight']
        for order,color in (((1,),(10,0,0,128)),((0,1),(60,25,12,255)),((0,1,2),(45,31,33,255))):
            r=self.record;r.update(kind='constant-control',prefixCount=0,prefixMembers=[],controls=[{'index':i,'premultipliedRGBA':list(COLORS[i])} for i in order])
            pixels=bytes(color)*(w*h);png=encode_png(w,h,pixels);digest=hashlib.sha256(pixels).hexdigest()
            for field in ('rgbaFilename','nativeRGBAFilename'):(self.directory/r[field]).write_bytes(png)
            r['rgbaSHA256']=digest;r['nativeRGBASHA256']=digest
            self.assertTrue(self.call()['RGBA']['passed'])

if __name__=='__main__':unittest.main()
