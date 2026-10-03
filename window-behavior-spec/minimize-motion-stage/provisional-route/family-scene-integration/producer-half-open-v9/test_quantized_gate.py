import copy
from pathlib import Path
import unittest
import hashlib
from verify_quantized_over import verify,shader_digests,POLICY,COVERAGE_POLICY,VERTEX,coverage_geometry

class Gate(unittest.TestCase):
    def setUp(self):
        self.hashes=shader_digests(Path(__file__).with_name('QuantizedOver.hpp').read_text())
        self.sources=[{'digest':c*64,'pixels':[13+i*10,7+i*10]} for i,c in enumerate('abc')]
        self.readback={'token':'0123456789ab-1','sequence':'17','output':'private','generation':9,'bufferWidth':320,'bufferHeight':240,
            'members':[{'stableId':f'aa0{i+1}','pid':41+i,'digest':s['digest'],'rectangle':{'x':10+i,'y':20+i,'width':50,'height':40}} for i,s in enumerate(self.sources)]}
        self.events=[{'event':'quantizedOverExperiment','overProgram':8,'copyProgram':20,'policy':POLICY,'fragmentSHA256':self.hashes[0],'copyFragmentSHA256':self.hashes[1],'rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False},
            {'event':'samplingExperiment','policy':'four-nearest-centers-highp-bilinear-v1','fragmentSHA256':self.hashes[0],'rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False},
            {'event':'rasterPathSelected','path':'shader-per-layer-quantized-over','sampler':'four-nearest-centers-highp-bilinear','rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False}]
        self.events[0].update(coveragePolicy=COVERAGE_POLICY,vertexSHA256=hashlib.sha256(VERTEX.encode()).hexdigest())
        self.logical={'x':0,'y':0,'width':320,'height':240}
        self.events.append({'event':'outputs','outputs':[dict(self.logical,name='private',generation=9)]})
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
                rect=self.readback['members'][number]['rectangle'] if number<3 else self.logical
                bounds,sample=coverage_geometry(rect,self.logical,[320,240])
                passes[-1].update(coveragePolicy=COVERAGE_POLICY,sourceRectangle=copy.deepcopy(rect),logicalOutput=copy.deepcopy(self.logical),coverageUniform=bounds,sampleRectUniform=sample,viewport=[0,0,320,240],coverageInspectionError=0,fullscreenPositions=[-1,1,1,1,-1,-1,1,-1],vertexState=dict(enabled=1,size=2,type=5126,normalized=0,stride=0,buffer=0,inspectionError=0))
                previous=write
        self.frame=dict(self.readback,event='quantizedOverFrameConfigured',policy=POLICY,logicalOutput=copy.deepcopy(self.logical),passes=passes,finalCopy=self.copy_state(0,102),nativeAuthority=False,pixelProof=False)
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
    def test_each_coverage_limit_and_sample_coordinate_queried(self):
        p=self.frame['passes'][-1]
        for field in ('coverageUniform','sampleRectUniform'):
            for index in range(4):
                with self.subTest(field=field,index=index):
                    old=p[field][index];p[field][index]+=1;self.assertRaises(ValueError,self.check);p[field][index]=old
    def test_boolean_coverage_coordinate_refused(self):
        self.frame['passes'][-1]['coverageUniform'][0]=True;self.assertRaises(ValueError,self.check)
    def test_nonfinite_sample_coordinate_refused(self):
        self.frame['passes'][-1]['sampleRectUniform'][0]=float('nan');self.assertRaises(ValueError,self.check)
    def test_missing_coverage_uniform_refused(self):
        del self.frame['passes'][-1]['coverageUniform'];self.assertRaises(ValueError,self.check)
    def test_coverage_query_error_refused(self):
        self.frame['passes'][-1]['coverageInspectionError']=1282;self.assertRaises(ValueError,self.check)
    def test_member_rectangle_cannot_borrow_another_pass_geometry(self):
        self.frame['passes'][-1]['sourceRectangle']=self.frame['passes'][-2]['sourceRectangle'];self.assertRaises(ValueError,self.check)
    def test_control_must_cover_exact_logical_output(self):
        p=self.frame['passes'][0];p['sourceRectangle']=self.readback['members'][0]['rectangle'];self.assertRaises(ValueError,self.check)
    def test_fullscreen_positions_cannot_be_member_quad(self):
        self.frame['passes'][-1]['fullscreenPositions'][0]=-.3;self.assertRaises(ValueError,self.check)
    def test_every_actual_vertex_state_field_refused_on_drift(self):
        v=self.frame['passes'][-1]['vertexState']
        for field in v:
            with self.subTest(field=field):
                old=v[field];v[field]+=1;self.assertRaises(ValueError,self.check);v[field]=old
    def test_coverage_policy_and_compiled_vertex_digest_refused_on_drift(self):
        for field in ('coveragePolicy','vertexSHA256'):
            old=self.events[0][field];self.events[0][field]='wrong';self.assertRaises(ValueError,self.check);self.events[0][field]=old
    def test_actual_output_generation_geometry_required(self):
        self.events[3]['outputs'][0]['x']=320;self.assertRaises(ValueError,self.check)
    def test_output_observation_missing_refused(self):
        self.events.pop(3);self.assertRaises(ValueError,self.check)
    def test_conflicting_same_generation_output_geometry_refused(self):
        self.events.append({'event':'outputs','outputs':[dict(self.logical,name='private',generation=9,width=640)]});self.assertRaises(ValueError,self.check)
    def test_member_pass_output_geometry_drift_refused(self):
        self.frame['passes'][-1]['logicalOutput']['height']=360;self.assertRaises(ValueError,self.check)
    def test_v10_half_center_child_top_row_included(self):
        rect={'x':333.4,'y':105,'width':55.2,'height':38.2};output={'x':320,'y':0,'width':320,'height':240}
        bounds,sample=coverage_geometry(rect,output,[480,360]);self.assertEqual(bounds,[20,157,103,215]);self.assertEqual(sample[1],157.5)
    def test_actual_full_buffer_viewport_must_match_every_coordinate(self):
        p=self.frame['passes'][-1]
        for index in range(4):
            old=p['viewport'][index];p['viewport'][index]+=1;self.assertRaises(ValueError,self.check);p['viewport'][index]=old

if __name__=='__main__':unittest.main()
