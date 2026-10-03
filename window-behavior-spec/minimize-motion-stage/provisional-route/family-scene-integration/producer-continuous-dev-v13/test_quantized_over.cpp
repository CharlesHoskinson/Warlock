// Actual staged draw consumer with GL call stubs; no EGL/GPU/Wayland connection.
#define OWNED_EGL_OFFLINE_TEST
#include "Renderer.cpp"
#include <sstream>
#include <type_traits>
namespace Stub {
GLuint program=0,framebuffer=0;int unit=0;std::array<GLuint,2> textures{};
std::map<std::pair<GLuint,GLint>,std::array<float,4>> floats;
std::map<GLuint,const void*> vertexPointers;bool corruptCoverage=false,corruptSample=false,corruptVertex=false;
int corruptCoverageIndex=0,corruptSampleIndex=0;GLenum corruptVertexField=GL_VERTEX_ATTRIB_ARRAY_STRIDE;bool corruptVertexPointer=false;
int corruptViewportIndex=-1;bool failCoverageQuery=false;
std::map<std::pair<GLuint,GLint>,GLint> ints;
struct Draw {GLuint program,framebuffer,source,previous;};std::vector<Draw> draws;
bool blend=false,forceBlend=false,corruptRead=false,corruptAttached=false,corruptUniform=false;
int bitWidth=8,samples=0,filter=GL_NEAREST;GLenum error=GL_NO_ERROR;
GLuint nextTexture=301,nextFramebuffer=401;bool partialTextures=false,incomplete=false,failContext=false,failDelete=false;
int textureAllocations=0,framebufferAllocations=0,clears=0,pack=4;bool ignoreDefaultBinding=false,failRead=false,failNativeRead=false;
struct Read{GLuint framebuffer;GLenum format,type;int pack;};std::vector<Read> reads;std::vector<GLuint> deletedTextures,deletedFramebuffers;
std::map<GLuint,GLuint> attachments;std::vector<std::array<int,2>> extents;
}
extern "C" {
void glUseProgram(GLuint p){Stub::program=p;}
void glActiveTexture(GLenum unit){Stub::unit=unit-GL_TEXTURE0;}
void glBindTexture(GLenum,GLuint texture){Stub::textures.at(Stub::unit)=texture;}
void glBindFramebuffer(GLenum,GLuint framebuffer){if(framebuffer||!Stub::ignoreDefaultBinding)Stub::framebuffer=framebuffer;}
void glDisable(GLenum key){if(key==GL_BLEND)Stub::blend=false;}
GLboolean glIsEnabled(GLenum key){return key==GL_BLEND&&(Stub::blend||Stub::forceBlend);}
GLint glGetUniformLocation(GLuint,const GLchar* name){return std::string(name)=="prefix"?3:std::string(name)=="outputSize"?4:std::string(name)=="coverageBounds"?5:std::string(name)=="sampleRect"?6:0;}
void glUniform1i(GLint loc,GLint value){Stub::ints[{Stub::program,loc}]=value;}
void glUniform2f(GLint loc,GLfloat x,GLfloat y){Stub::floats[{Stub::program,loc}]={x,y,0,0};}
void glUniform4f(GLint loc,GLfloat x,GLfloat y,GLfloat z,GLfloat w){Stub::floats[{Stub::program,loc}]={x,y,z,w};}
void glGetUniformiv(GLuint prog,GLint loc,GLint* out){*out=Stub::ints.at({prog,loc});}
void glGetUniformfv(GLuint prog,GLint loc,GLfloat* out){auto value=Stub::floats.at({prog,loc});for(int i=0;i<(loc==5||loc==6?4:2);++i)out[i]=value[i];if(Stub::corruptUniform)out[0]=99;if(Stub::corruptCoverage&&loc==5)out[Stub::corruptCoverageIndex]+=1;if(Stub::corruptSample&&loc==6)out[Stub::corruptSampleIndex]+=1;if(Stub::failCoverageQuery&&(loc==5||loc==6))Stub::error=GL_INVALID_OPERATION;}
void glGetTexParameteriv(GLenum,GLenum key,GLint* out){*out=(key==GL_TEXTURE_MIN_FILTER||key==GL_TEXTURE_MAG_FILTER)?Stub::filter:GL_CLAMP_TO_EDGE;}
void glGetIntegerv(GLenum key,GLint* out){
    if(key==GL_VIEWPORT){out[0]=0;out[1]=0;out[2]=320;out[3]=240;if(Stub::corruptViewportIndex>=0)out[Stub::corruptViewportIndex]+=1;}
    else if(key==GL_FRAMEBUFFER_BINDING)*out=Stub::framebuffer;
    else if(key==GL_TEXTURE_BINDING_2D)*out=Stub::corruptRead?999:Stub::textures.at(Stub::unit);
    else if(key==GL_CURRENT_PROGRAM)*out=Stub::program;
    else if(key==GL_SAMPLES)*out=Stub::samples;
    else if(key==GL_PACK_ALIGNMENT)*out=Stub::pack;
    else if(key==GL_IMPLEMENTATION_COLOR_READ_FORMAT)*out=Stub::framebuffer?GL_RGBA:OwnedCausal::BGRA;
    else if(key==GL_IMPLEMENTATION_COLOR_READ_TYPE)*out=GL_UNSIGNED_BYTE;
    else *out=Stub::bitWidth;
}
void glGetFramebufferAttachmentParameteriv(GLenum,GLenum,GLenum key,GLint* out){
    *out=key==GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE?GL_TEXTURE:
        Stub::corruptAttached?101:Stub::attachments.contains(Stub::framebuffer)?Stub::attachments.at(Stub::framebuffer):Stub::framebuffer==201?101:102;
}
GLenum glGetError(){auto error=Stub::error;Stub::error=GL_NO_ERROR;return error;}
void glGenTextures(GLsizei count,GLuint* ids){++Stub::textureAllocations;for(int i=0;i<count;++i)ids[i]=Stub::partialTextures&&i==0?0:Stub::nextTexture++;}
void glGenFramebuffers(GLsizei count,GLuint* ids){++Stub::framebufferAllocations;for(int i=0;i<count;++i)ids[i]=Stub::nextFramebuffer++;}
void glDeleteTextures(GLsizei count,const GLuint* ids){for(int i=0;i<count;++i)if(ids[i])Stub::deletedTextures.push_back(ids[i]);if(Stub::failDelete)Stub::error=GL_INVALID_OPERATION;}
void glDeleteFramebuffers(GLsizei count,const GLuint* ids){for(int i=0;i<count;++i)if(ids[i])Stub::deletedFramebuffers.push_back(ids[i]);}
void glTexParameteri(GLenum,GLenum,GLint){}
void glTexImage2D(GLenum,GLint,GLint,GLsizei width,GLsizei height,GLint,GLenum,GLenum,const void*){Stub::extents.push_back({width,height});}
void glFramebufferTexture2D(GLenum,GLenum,GLenum,GLuint texture,GLint){Stub::attachments[Stub::framebuffer]=texture;}
GLenum glCheckFramebufferStatus(GLenum){return Stub::incomplete?GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:GL_FRAMEBUFFER_COMPLETE;}
void glClearColor(GLfloat,GLfloat,GLfloat,GLfloat){}
void glClear(GLbitfield){++Stub::clears;}
EGLContext eglGetCurrentContext(){return EGL_NO_CONTEXT;}
EGLBoolean eglMakeCurrent(EGLDisplay,EGLSurface,EGLSurface,EGLContext){return Stub::failContext?EGL_FALSE:EGL_TRUE;}
void glPixelStorei(GLenum key,GLint value){if(key==GL_PACK_ALIGNMENT)Stub::pack=value;}
void glReadPixels(GLint,GLint,GLsizei width,GLsizei height,GLenum format,GLenum type,void* data){
    Stub::reads.push_back({Stub::framebuffer,format,type,Stub::pack});auto* bytes=static_cast<unsigned char*>(data);
    for(int i=0;i<width*height;++i){bytes[i*4]=format==GL_RGBA?2:7;bytes[i*4+1]=5;bytes[i*4+2]=format==GL_RGBA?7:2;bytes[i*4+3]=11;}
    if(Stub::failRead||(Stub::failNativeRead&&format==OwnedCausal::BGRA))Stub::error=GL_INVALID_OPERATION;
}
void glEnableVertexAttribArray(GLuint){}
void glVertexAttribPointer(GLuint location,GLint,GLenum,GLboolean,GLsizei,const void* pointer){Stub::vertexPointers[location]=pointer;}
void glGetVertexAttribiv(GLuint,GLenum name,GLint* out){*out=name==GL_VERTEX_ATTRIB_ARRAY_ENABLED?1:name==GL_VERTEX_ATTRIB_ARRAY_SIZE?2:name==GL_VERTEX_ATTRIB_ARRAY_TYPE?GL_FLOAT:0;if(Stub::corruptVertex&&name==Stub::corruptVertexField)*out+=1;}
void glGetVertexAttribPointerv(GLuint location,GLenum,void** out){*out=Stub::corruptVertexPointer?nullptr:const_cast<void*>(Stub::vertexPointers.at(location));}
void glDrawArrays(GLenum,GLint,GLsizei){Stub::draws.push_back({Stub::program,Stub::framebuffer,Stub::textures[0],Stub::textures[1]});}
}
struct OfflineCommands {
static int run(){
    int n=0;auto check=[&](bool value){if(!value)throw std::runtime_error("over consumer check "+std::to_string(n+1));++n;};
    auto rejects=[](auto f){try{f();return false;}catch(...){return true;}};
    Renderer productionDefault;check(productionDefault.quantizedOver&&productionDefault.manualSampling&&!productionDefault.rasterFixture);
    check(std::string(productionDefault.selection.role)=="production-default"&&!productionDefault.selection.explicitExperiment);
    static_assert(std::is_const_v<decltype(productionDefault.rasterFixture)>);
    Renderer diagnosticDefault(true);check(diagnosticDefault.quantizedOver&&diagnosticDefault.manualSampling&&diagnosticDefault.rasterFixture);
    check(std::string(diagnosticDefault.selection.role)=="diagnostic-default"&&!diagnosticDefault.selection.explicitExperiment);
    check(rejects([]{OwnedProduction::select(false,true,false);}));check(rejects([]{OwnedProduction::select(false,false,true);}));
    check(rejects([]{OwnedProduction::select(true,true,true);}));
    const auto legacyDiagnostic=OwnedProduction::select(true,true,false);check(legacyDiagnostic.manual&&!legacyDiagnostic.over&&legacyDiagnostic.explicitExperiment);
    const auto explicitOver=OwnedProduction::select(true,false,true);check(explicitOver.manual&&explicitOver.over&&explicitOver.explicitExperiment);
    check(rejects([]{Renderer r(false,"",false,false,true);}));
    check(rejects([]{Renderer r(true,"",false,false,true);}));
    check(rejects([]{Renderer r(true,"",true,false,true);}));
    OwnedOver::requireDiagnostic(true,true,true,true);check(true);
    check(rejects([]{OwnedOver::requireBuffers(1,320,240,101,101,201);}));
    check(rejects([]{OwnedOver::requireBuffers(0,320,240,101,102,202);}));
    check(rejects([]{OwnedOver::requireBuffers(1,16384,16384,101,102,202);}));
    Renderer r;r.quantizedOver=true;r.manualSampling=true;r.shader=8;r.copyShader=20;
    r.positionLocation=0;r.uvLocation=1;r.atlasSizeLocation=2;r.outputSizeLocation=4;r.prefixLocation=3;r.copyPosition=0;r.copySize=4;
    r.coverageLocation=5;r.sampleRectLocation=6;
    Renderer::Output o;o.name="private";o.generation=9;o.prefixGeneration=9;
    o.width=o.bufferWidth=o.prefixWidth=320;o.height=o.bufferHeight=o.prefixHeight=240;
    o.prefixTextures={101,102};o.prefixFramebuffers={201,202};
    r.samplerTextures[11]={13,7,-1,std::string(64,'a'),false};
    r.samplerTextures[12]={23,17,-1,std::string(64,'b'),false};
    const Rect rect{40,30,120,80};std::ostringstream events;auto* old=std::cout.rdbuf(events.rdbuf());
    r.drawLayer(o,rect,11,1);
    check(o.prefixRead==1&&o.prefixPassCount==1&&Stub::draws.size()==2);
    check(Stub::draws[0].program==20&&Stub::draws[0].framebuffer==202&&Stub::draws[0].previous==101);
    check(Stub::draws[1].program==8&&Stub::draws[1].framebuffer==202&&Stub::draws[1].source==11&&Stub::draws[1].previous==101);
    check(!Stub::blend&&o.prefixConfigurations.size()==1);
    const auto configured=o.prefixConfigurations.at(0).toObject();
    check(configured["coverageUniform"].toArray()==QJsonArray{40,30,160,110});
    check(configured["sampleRectUniform"].toArray()==QJsonArray{40,30,120,80});
    check(configured["fullscreenPositions"].toArray()==QJsonArray{-1,1,1,1,-1,-1,1,-1});
    check(configured["sourceRectangle"].toObject()==rectangleJson(rect));
    r.drawLayer(o,rect,12,2);
    check(o.prefixRead==0&&o.prefixPassCount==2&&Stub::draws.size()==4);
    check(Stub::draws[2].framebuffer==201&&Stub::draws[2].previous==102);
    check(Stub::draws[3].source==12&&Stub::draws[3].previous==102);
    auto refuse=[&](auto mutate,auto undo,const char*){
        const auto prefix=o.prefixPassCount;const auto read=o.prefixRead;const auto records=o.prefixConfigurations.size();
        mutate();check(rejects([&]{r.drawLayer(o,rect,11,3);}));
        check(o.prefixPassCount==prefix&&o.prefixRead==read&&o.prefixConfigurations.size()==records);undo();
    };
    refuse([&]{o.generation=10;},[&]{o.generation=9;},"generation");
    refuse([&]{o.bufferWidth=480;},[&]{o.bufferWidth=320;},"extent");
    refuse([&]{o.prefixTextures[1]=101;},[&]{o.prefixTextures[1]=102;},"feedback attachment");
    refuse([]{Stub::forceBlend=true;},[]{Stub::forceBlend=false;},"double blend");
    refuse([]{Stub::bitWidth=5;},[]{Stub::bitWidth=8;},"bits");
    refuse([]{Stub::samples=4;},[]{Stub::samples=0;},"samples");
    refuse([]{Stub::filter=GL_LINEAR;},[]{Stub::filter=GL_NEAREST;},"filter");
    refuse([]{Stub::corruptRead=true;},[]{Stub::corruptRead=false;},"bound previous");
    refuse([]{Stub::corruptAttached=true;},[]{Stub::corruptAttached=false;},"attachment");
    refuse([]{Stub::corruptUniform=true;},[]{Stub::corruptUniform=false;},"uniform");
    for(int i=0;i<4;++i){
        Stub::corruptCoverageIndex=i;refuse([]{Stub::corruptCoverage=true;},[]{Stub::corruptCoverage=false;},"coverage uniform");
        Stub::corruptSampleIndex=i;refuse([]{Stub::corruptSample=true;},[]{Stub::corruptSample=false;},"sample rectangle uniform");
    }
    for(auto field:{GL_VERTEX_ATTRIB_ARRAY_ENABLED,GL_VERTEX_ATTRIB_ARRAY_SIZE,GL_VERTEX_ATTRIB_ARRAY_TYPE,GL_VERTEX_ATTRIB_ARRAY_NORMALIZED,GL_VERTEX_ATTRIB_ARRAY_STRIDE,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING}){
        Stub::corruptVertexField=field;refuse([]{Stub::corruptVertex=true;},[]{Stub::corruptVertex=false;},"full-screen vertex query");
    }
    refuse([]{Stub::corruptVertexPointer=true;},[]{Stub::corruptVertexPointer=false;},"vertex array pointer");
    for(int i=0;i<4;++i)refuse([&]{Stub::corruptViewportIndex=i;},[]{Stub::corruptViewportIndex=-1;},"owned full-buffer viewport");
    refuse([]{Stub::failCoverageQuery=true;},[]{Stub::failCoverageQuery=false;},"uniform query error");
    const auto child=OwnedCoverage::geometry(333.4,105,55.2,38.2,320,0,320,240,480,360);
    check(child.bounds==std::array<int,4>{20,157,103,215});check(child.sample[1]==157.5f);
    for(const auto x:{-21.5,-10.0,0.0,0.5,1.0,5.25,10.5,21.0})for(const auto width:{0.125,0.5,1.0,3.75,8.0,31.0}){
        const auto projected=OwnedCoverage::geometry(x,105,width,38.2,0,0,21,240,32,360);
        bool agrees=true;for(int px=0;px<32;++px){const double center=(double(px)+0.5)*21/32;agrees&=(x<=center&&center<x+width)==(projected.bounds[0]<=px&&px<projected.bounds[2]);}
        check(agrees);
    }
    check(rejects([]{OwnedCoverage::geometry(0,0,0,1,0,0,320,240,320,240);}));
    check(rejects([]{OwnedCoverage::geometry(0,0,1,1,0,0,0,240,320,240);}));
    check(rejects([]{OwnedCoverage::geometry(INFINITY,0,1,1,0,0,320,240,320,240);}));
    check(rejects([]{OwnedCoverage::geometry(0,0,1e308,1,0,0,320,240,320,240);}));
    const auto before=Stub::draws.size();check(rejects([&]{r.drawLayer(o,rect,11,4);}));check(Stub::draws.size()==before);
    r.drawLayer(o,rect,11,3);check(o.prefixPassCount==3&&o.prefixRead==1);
    const auto complete=o.prefixConfigurations;
    for(int i=0;i<complete.size();++i){const auto record=complete[i].toObject();
        check(record["prefixCount"]==i+1&&record["readTexture"]!=record["writeTexture"]);
        check(record["attachedTexture"]==record["writeTexture"]&&record["readTextureBinding"]==record["readTexture"]);
        check(record["blend"]==false&&record["bits"]==QJsonArray{8,8,8,8}&&record["samples"]==0);
        check(record["sourceUnit"]==0&&record["prefixUnit"]==1&&record["extentUniform"]==QJsonArray{320,240});
    }
    r.copyPrefix(o,o.prefixTextures[o.prefixRead],0);check(Stub::draws.back().framebuffer==0&&Stub::draws.back().program==20);
    const auto prefixBefore=o.prefixRead;const auto passBefore=o.prefixPassCount;const auto configsBefore=o.prefixConfigurations.size();
    const auto priorCopies=Stub::draws.size();
    auto observed=r.observeCausal(o,"member-prefix",3);
    check(Stub::draws.size()==priorCopies+1&&Stub::draws.back().program==20&&Stub::draws.back().framebuffer==0&&Stub::draws.back().previous==102);
    check(Stub::reads.size()==2&&Stub::reads[0].framebuffer==0&&Stub::reads[1].framebuffer==0);
    check(Stub::reads[0].format==GL_RGBA&&Stub::reads[1].format==OwnedCausal::BGRA&&Stub::reads[1].type==GL_UNSIGNED_BYTE);
    check(observed.nativeFormat==OwnedCausal::BGRA&&observed.rgba==observed.nativeRGBA&&observed.rgba.size()==320*240*4);
    check(observed.readFramebuffer==0&&observed.prefixTexture==102&&observed.observedPrefixCount==3&&observed.readTargetCopy["framebuffer"]==0);
    check(o.prefixRead==prefixBefore&&o.prefixPassCount==passBefore&&o.prefixConfigurations.size()==configsBefore&&Stub::pack==4);
    // A later original source layer continues from the actual prefix, not the copied default target.
    r.drawLayer(o,rect,11,4);check(o.prefixRead==0&&o.prefixPassCount==4&&Stub::draws.back().framebuffer==201);
    const auto readsBefore=Stub::reads.size();const auto drawBefore=Stub::draws.size();
    check(rejects([&]{r.observeCausal(o,"member-prefix",3);}));check(Stub::reads.size()==readsBefore&&Stub::draws.size()==drawBefore);
    o.generation=10;check(rejects([&]{r.observeCausal(o,"member-prefix",4);}));check(Stub::reads.size()==readsBefore);o.generation=9;
    o.bufferWidth=480;check(rejects([&]{r.observeCausal(o,"member-prefix",4);}));check(Stub::reads.size()==readsBefore);o.bufferWidth=320;
    Stub::ignoreDefaultBinding=true;Stub::framebuffer=201;check(rejects([&]{r.observeCausal(o,"member-prefix",4);}));Stub::ignoreDefaultBinding=false;check(Stub::reads.size()==readsBefore);
    Stub::failRead=true;check(rejects([&]{r.observeCausal(o,"member-prefix",4);}));Stub::failRead=false;check(Stub::pack==4&&o.prefixPassCount==4&&o.prefixRead==0);
    Stub::failNativeRead=true;check(rejects([&]{r.observeCausal(o,"member-prefix",4);}));Stub::failNativeRead=false;check(Stub::pack==4&&o.prefixPassCount==4&&o.prefixRead==0);
    o.prefixRead=1;o.prefixPassCount=3;
    const auto control=r.observeCausal(o,"constant-control",0,{0,1,2});check(control.readFramebuffer==0&&control.observedPrefixCount==3&&control.nativeFormat==OwnedCausal::BGRA);
    check(rejects([&]{r.observeCausal(o,"constant-control",0,{0,1});}));
    // Restore the earlier complete three-prefix fixture used by alias controls below.
    o.prefixRead=1;o.prefixPassCount=3;
    const auto beforeAlias=Stub::draws.size();
    check(rejects([&]{r.drawLayer(o,rect,101,4);}));check(Stub::draws.size()==beforeAlias);
    check(rejects([&]{r.drawLayer(o,rect,102,4);}));check(Stub::draws.size()==beforeAlias);
    const auto beforeCopy=Stub::draws.size();
    check(rejects([&]{r.copyPrefix(o,101,201);}));check(Stub::draws.size()==beforeCopy);
    check(rejects([&]{r.copyPrefix(o,101,999);}));check(Stub::draws.size()==beforeCopy);
    Renderer resources;Renderer::Output owned;owned.generation=19;owned.bufferWidth=320;owned.bufferHeight=240;
    resources.beginPrefix(owned);
    check(Stub::textureAllocations==1&&Stub::framebufferAllocations==1&&Stub::extents.size()==2);
    check(owned.prefixGeneration==19&&owned.prefixWidth==320&&owned.prefixHeight==240&&owned.prefixRead==0&&owned.prefixPassCount==0);
    check(owned.prefixTextures[0]!=owned.prefixTextures[1]&&owned.prefixFramebuffers[0]!=owned.prefixFramebuffers[1]);
    const auto firstTextures=owned.prefixTextures;const auto firstFramebuffers=owned.prefixFramebuffers;
    owned.prefixRead=1;owned.prefixPassCount=3;resources.beginPrefix(owned);
    check(Stub::textureAllocations==1&&Stub::framebufferAllocations==1&&owned.prefixRead==0&&owned.prefixPassCount==0&&Stub::clears==2);
    owned.generation=20;owned.bufferWidth=480;resources.beginPrefix(owned);
    check(Stub::textureAllocations==2&&Stub::framebufferAllocations==2&&Stub::extents.back()==std::array<int,2>{480,240});
    check(Stub::deletedTextures==std::vector<GLuint>(firstTextures.begin(),firstTextures.end()));
    check(Stub::deletedFramebuffers==std::vector<GLuint>(firstFramebuffers.begin(),firstFramebuffers.end()));
    resources.releasePrefix(owned);check(owned.prefixTextures==std::array<GLuint,2>{}&&owned.prefixFramebuffers==std::array<GLuint,2>{}&&owned.prefixGeneration==0);
    const auto deletedCount=Stub::deletedTextures.size();resources.releasePrefix(owned);check(Stub::deletedTextures.size()==deletedCount);
    const auto allocations=Stub::textureAllocations;
    for(auto extent:std::vector<std::array<int,2>>{{0,240},{320,-1},{20000,1},{16384,16384}}){owned.bufferWidth=extent[0];owned.bufferHeight=extent[1];check(rejects([&]{resources.beginPrefix(owned);}));}
    check(Stub::textureAllocations==allocations);
    owned.bufferWidth=320;owned.bufferHeight=240;owned.generation=0;check(rejects([&]{resources.beginPrefix(owned);}));check(Stub::textureAllocations==allocations);owned.generation=21;
    Stub::partialTextures=true;check(rejects([&]{resources.beginPrefix(owned);}));Stub::partialTextures=false;
    check(owned.prefixTextures[0]==0&&owned.prefixTextures[1]!=0&&owned.prefixGeneration==0);
    const auto partialTexture=owned.prefixTextures[1];resources.releasePrefix(owned);check(Stub::deletedTextures.back()==partialTexture&&owned.prefixTextures==std::array<GLuint,2>{});
    Stub::incomplete=true;check(rejects([&]{resources.beginPrefix(owned);}));Stub::incomplete=false;
    check(owned.prefixGeneration==0&&owned.prefixTextures[0]!=0);resources.releasePrefix(owned);
    resources.beginPrefix(owned);Stub::failDelete=true;resources.releasePrefix(owned);Stub::failDelete=false;
    check(resources.overCleanupFailed);check(rejects([&]{resources.beginPrefix(owned);}));
    Renderer contextFailure;Renderer::Output detached;detached.prefixTextures={901,902};detached.prefixFramebuffers={903,904};
    contextFailure.context=reinterpret_cast<EGLContext>(1);Stub::failContext=true;contextFailure.releasePrefix(detached);Stub::failContext=false;
    check(contextFailure.overCleanupFailed&&detached.prefixTextures==std::array<GLuint,2>{});contextFailure.context=EGL_NO_CONTEXT;
    // Retain the isolated old helper branch as an offline diagnostic control.
    Renderer original(true);original.quantizedOver=false;original.manualSampling=false;const auto prior=Stub::draws.size();original.drawLayer(o,rect,999,8);
    check(Stub::draws.size()==prior+1);
    const auto originalDraws=Stub::draws.size();Stub::framebuffer=0;auto ordinary=original.observeCausal(o,"member-prefix",1);
    check(Stub::draws.size()==originalDraws&&ordinary.readTargetCopy.isEmpty());check(ordinary.nativeFormat==OwnedCausal::BGRA&&ordinary.rgba==ordinary.nativeRGBA);
    std::cout.rdbuf(old);std::cout<<n<<" quantized-over actual consumer CPU-stub checks PASS\n";return 0;
}
};
int main(){return OfflineCommands::run();}
