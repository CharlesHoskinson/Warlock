import copy
from pathlib import Path
import unittest
from verify_quantized_over import verify,shader_digests,POLICY

class Gate(unittest.TestCase):
    def setUp(self):
        self.hashes=shader_digests(Path(__file__).with_name('QuantizedOver.hpp').read_text())
        self.sources=[{'digest':c*64,'pixels':[13+i*10,7+i*10]} for i,c in enumerate('abc')]
        self.readback={'token':'0123456789ab-1','sequence':'17','output':'private','generation':9,'bufferWidth':320,'bufferHeight':240,
            'members':[{'stableId':f'aa0{i+1}','pid':41+i,'digest':s['digest'],'rectangle':{'x':10+i,'y':20+i,'width':50,'height':40}} for i,s in enumerate(self.sources)]}
        self.events=[{'event':'quantizedOverExperiment','overProgram':8,'copyProgram':20,'policy':POLICY,'fragmentSHA256':self.hashes[0],'copyFragmentSHA256':self.hashes[1],'rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False},
            {'event':'samplingExperiment','policy':'four-nearest-centers-highp-bilinear-v1','fragmentSHA256':self.hashes[0],'rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False},
            {'event':'rasterPathSelected','path':'shader-per-layer-quantized-over','sampler':'four-nearest-centers-highp-bilinear','rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False}]
        uploads=[]
        for i,s in enumerate(self.sources):uploads.append(dict(sourceDigest=s['digest'],pixels=s['pixels'],controlIndex=-1,textureId=11+i))
        for i in range(3):uploads.append(dict(sourceDigest='',pixels=[1,1],controlIndex=i,textureId=21+i))
        for u in uploads:self.events.append(dict(u,event='samplingConfigured',policy='four-nearest-centers-highp-bilinear-v1',extentUniform=u['pixels'],minFilter=9728,magFilter=9728,wrapS=33071,wrapT=33071,inspectionError=0,nativeAuthority=False,pixelProof=False))
        self.uploads=uploads
        passes=[]
        for vector in ((4,),(3,4),(3,4,5),(0,1,2)):
            previous=101
            for index,number in enumerate(vector,1):
                write=102 if previous==101 else 101;fbo=202 if write==102 else 201;u=uploads[number]
                passes.append(dict(prefixCount=index,readTexture=previous,writeTexture=write,writeFramebuffer=fbo,readTextureBinding=previous,sourceTexture=u['textureId'],sourceTextureBinding=u['textureId'],shaderProgram=8,sourceDigest=u['sourceDigest'],pixels=u['pixels'],controlIndex=u['controlIndex'],attachedTexture=write,attachmentType=5890,blend=False,bits=[8,8,8,8],samples=0,minFilter=9728,magFilter=9728,wrapS=33071,wrapT=33071,sourceUnit=0,prefixUnit=1,extentUniform=[320,240],inspectionError=0,prefixCopy=self.copy_state(fbo,previous)))
                previous=write
        self.frame=dict(self.readback,event='quantizedOverFrameConfigured',policy=POLICY,passes=passes,finalCopy=self.copy_state(0,102),nativeAuthority=False,pixelProof=False)
        self.events.append(self.frame)
    def copy_state(self,fbo,texture):return dict(program=20,attachedTexture=102 if fbo==202 else 101 if fbo==201 else 0,attachmentType=5890 if fbo else 0,framebuffer=fbo,texture=texture,unit=1,extentUniform=[320,240],minFilter=9728,magFilter=9728,wrapS=33071,wrapT=33071,blend=False,inspectionError=0)
    def check(self):return verify(self.events,self.readback,self.sources,self.hashes)
    def test_complete_actual_configuration_never_claims_pixels(self):
        result=self.check();self.assertEqual(result['familyPassCount'],3);self.assertEqual(result['controlPassCount'],6);self.assertFalse(result['pixelProof'] or result['nativeAuthority'])
    def test_later_frame_without_controls_still_has_complete_family(self):
        self.frame['passes']=self.frame['passes'][-3:];self.assertEqual(self.check()['controlPassCount'],0)
    def test_wrong_compiled_shader_hash_rejects(self):
        self.events[0]['fragmentSHA256']='0'*64;self.assertRaises(ValueError,self.check)
    def test_hardware_linear_selection_cannot_masquerade_as_experiment(self):
        self.events[2]['sampler']='hardware-linear';self.assertRaises(ValueError,self.check)
    def test_same_attachment_read_write_rejects(self):
        p=self.frame['passes'][-1];p['writeTexture']=p['readTexture'];self.assertRaises(ValueError,self.check)
    def test_old_output_generation_rejects(self):
        self.frame['generation']=10;self.assertRaises(ValueError,self.check)
    def test_different_buffer_extent_rejects(self):
        self.frame['bufferWidth']=480;self.assertRaises(ValueError,self.check)
    def test_old_local_sequence_rejects(self):
        self.frame['sequence']='16';self.assertRaises(ValueError,self.check)
    def test_missing_or_duplicate_configuration_rejects(self):
        self.events.append(copy.deepcopy(self.frame));self.assertRaises(ValueError,self.check)
    def test_reordered_source_digests_rejects(self):
        self.frame['passes'][-1]['sourceDigest']='b'*64;self.assertRaises(ValueError,self.check)
    def test_same_bytes_unknown_source_texture_rejects(self):
        self.frame['passes'][-1]['sourceTexture']=90;self.frame['passes'][-1]['sourceTextureBinding']=90;self.assertRaises(ValueError,self.check)
    def test_partial_family_prefix_rejects(self):
        self.frame['passes'].pop();self.assertRaises(ValueError,self.check)
    def test_unquantized_or_multisampled_state_rejects(self):
        for field,value in (('bits',[5,6,5,0]),('samples',4),('blend',True),('inspectionError',1282)):
            with self.subTest(field=field):
                old=self.frame['passes'][-1][field];self.frame['passes'][-1][field]=value;self.assertRaises(ValueError,self.check);self.frame['passes'][-1][field]=old
    def test_copy_wrong_destination_rejects(self):
        self.frame['passes'][-1]['prefixCopy']['framebuffer']=201;self.assertRaises(ValueError,self.check)
    def test_different_final_pass_program_rejects(self):
        self.frame['passes'][-1]['shaderProgram']=909;self.assertRaises(ValueError,self.check)
    def test_all_over_programs_swapped_rejects(self):
        for p in self.frame['passes']:p['shaderProgram']=20
        self.assertRaises(ValueError,self.check)
    def test_final_copy_program_swapped_rejects(self):
        self.frame['finalCopy']['program']=8;self.assertRaises(ValueError,self.check)
    def test_prefix_copy_program_swapped_rejects(self):
        self.frame['passes'][-1]['prefixCopy']['program']=8;self.assertRaises(ValueError,self.check)
    def test_compiled_program_roles_must_be_distinct_and_typed(self):
        for field,value in (('overProgram',True),('copyProgram',20.0),('copyProgram',8),('overProgram',0)):
            with self.subTest(field=field,value=value):
                old=self.events[0][field];self.events[0][field]=value;self.assertRaises(ValueError,self.check);self.events[0][field]=old
    def test_source_must_not_alias_prefix_attachment(self):
        p=self.frame['passes'][-1];p['sourceTexture']=p['sourceTextureBinding']=p['writeTexture'];self.assertRaises(ValueError,self.check)
    def test_copy_feedback_attachment_rejects(self):
        p=self.frame['passes'][-1];p['prefixCopy']['attachedTexture']=p['readTexture'];self.assertRaises(ValueError,self.check)
    def test_default_target_not_final_prefix_rejects(self):
        self.frame['finalCopy']['texture']=101;self.assertRaises(ValueError,self.check)
    def test_final_copy_blended_rejects(self):
        self.frame['finalCopy']['blend']=True;self.assertRaises(ValueError,self.check)
    def test_wrong_control_order_or_boolean_index_rejects(self):
        self.frame['passes'][0]['controlIndex']=True;self.assertRaises(ValueError,self.check)
    def test_previous_prefix_changed_mid_group_rejects(self):
        p=self.frame['passes'][-1];p['readTexture']=102;p['writeTexture']=101;self.assertRaises(ValueError,self.check)

if __name__=='__main__':unittest.main()
