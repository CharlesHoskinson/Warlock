// Actual consumer draw path with CPU-only GL call stubs. No EGL/Wayland/GPU.
#define OWNED_EGL_OFFLINE_TEST
#include "Renderer.cpp"
#include <sstream>
namespace Stub {
GLuint bound = 0;
GLfloat uniform[2] = {0, 0};
int min = GL_NEAREST, mag = GL_NEAREST, wrapS = GL_CLAMP_TO_EDGE, wrapT = GL_CLAMP_TO_EDGE;
int draws = 0, inspections = 0;
bool corruptUniform = false;
GLenum error = GL_NO_ERROR;
}
extern "C" {
void glBindTexture(GLenum, GLuint texture) { Stub::bound = texture; }
void glUniform2f(GLint, GLfloat w, GLfloat h) { Stub::uniform[0]=w; Stub::uniform[1]=h; }
void glGetUniformfv(GLuint, GLint, GLfloat* p) {
    p[0]=Stub::corruptUniform ? 99 : Stub::uniform[0]; p[1]=Stub::uniform[1];
}
void glGetTexParameteriv(GLenum, GLenum name, GLint* p) {
    ++Stub::inspections;
    if(name==GL_TEXTURE_MIN_FILTER)*p=Stub::min;
    else if(name==GL_TEXTURE_MAG_FILTER)*p=Stub::mag;
    else if(name==GL_TEXTURE_WRAP_S)*p=Stub::wrapS;
    else if(name==GL_TEXTURE_WRAP_T)*p=Stub::wrapT;
}
GLenum glGetError() { auto e=Stub::error; Stub::error=GL_NO_ERROR; return e; }
void glVertexAttribPointer(GLuint, GLint, GLenum, GLboolean, GLsizei, const void*) {}
void glDrawArrays(GLenum, GLint, GLsizei) { ++Stub::draws; }
}

struct OfflineCommands {
static int run() {
    int checks=0;
    auto check=[&](bool ok){ if(!ok)throw std::runtime_error("manual sampler check "+std::to_string(checks+1)+" failed"); ++checks; };
    auto rejects=[](auto f){ try{f();return false;}catch(...){return true;} };
    check(rejects([]{Renderer r(false,"",false,true);}));
    check(rejects([]{Renderer r(true,"",false,true);}));
    check(rejects([]{Renderer r(true,"",true,true);}));
    // Constructor accepted-mode guard checked without opening a native display.
    OwnedSampling::requireDiagnostic(true,true,true,true);check(true);
    Renderer r; r.manualSampling=true; r.shader=8; r.atlasSizeLocation=2;
    Renderer::Output o; o.width=320;o.height=240;
    std::ostringstream events;auto* old=std::cout.rdbuf(events.rdbuf());
    const Rect rect{40,30,120,80};
    auto draw=[&](GLuint tex){r.drawQuad(o,rect,tex);};
    check(rejects([&]{draw(11);})); check(Stub::draws==0);
    r.samplerTextures[11]={0,5,-1,std::string(64,'a'),false};
    check(rejects([&]{draw(11);})); check(Stub::draws==0);
    r.samplerTextures[11]={64,48,-1,std::string(64,'a'),false};
    draw(11);check(Stub::draws==1 && Stub::bound==11 && Stub::uniform[0]==64 && Stub::uniform[1]==48);
    check(r.samplerTextures[11].announced && Stub::inspections==4);
    draw(11);check(Stub::draws==2 && Stub::inspections==4);
    r.samplerTextures[12]={23,17,-1,std::string(64,'b'),false};
    draw(12);check(Stub::uniform[0]==23 && Stub::uniform[1]==17 && Stub::inspections==8);
    r.samplerTextures[13]={1,1,2,"",false};
    draw(13);check(Stub::uniform[0]==1 && Stub::uniform[1]==1 && Stub::inspections==12);
    // Returning to a larger source must set its extent again; no sticky control uniform.
    draw(11);check(Stub::uniform[0]==64 && Stub::uniform[1]==48);
    r.samplerTextures[14]={16,16,-1,std::string(64,'c'),false};
    auto refusedState=[&](auto mutate,auto restore){auto before=Stub::draws;mutate();check(rejects([&]{draw(14);}));check(Stub::draws==before && !r.samplerTextures[14].announced);restore();};
    refusedState([]{Stub::min=GL_LINEAR;},[]{Stub::min=GL_NEAREST;});
    refusedState([]{Stub::mag=GL_LINEAR;},[]{Stub::mag=GL_NEAREST;});
    refusedState([]{Stub::wrapS=GL_REPEAT;},[]{Stub::wrapS=GL_CLAMP_TO_EDGE;});
    refusedState([]{Stub::wrapT=GL_REPEAT;},[]{Stub::wrapT=GL_CLAMP_TO_EDGE;});
    refusedState([]{Stub::corruptUniform=true;},[]{Stub::corruptUniform=false;});
    refusedState([]{Stub::error=GL_INVALID_OPERATION;},[]{});
    draw(14);check(r.samplerTextures[14].announced);
    // Texture retirement removes authority for a recycled GLuint until a fresh upload.
    r.samplerTextures.erase(14);check(rejects([&]{draw(14);}));
    r.samplerTextures[14]={7,9,-1,std::string(64,'d'),false};draw(14);
    check(Stub::uniform[0]==7 && Stub::uniform[1]==9);
    std::cout.rdbuf(old);
    int records=0;for(auto line:QByteArray::fromStdString(events.str()).split('\n'))if(!line.isEmpty()){
        auto event=QJsonDocument::fromJson(line).object();
        check(event["event"]=="samplingConfigured" && event["policy"]==OwnedSampling::policy && event["inspectionError"]==0);
        check(event["nativeAuthority"]==false && event["pixelProof"]==false);
        auto pixels=event["pixels"].toArray(),uniform=event["extentUniform"].toArray();check(pixels==uniform);
        check(event["minFilter"]==GL_NEAREST && event["magFilter"]==GL_NEAREST && event["wrapS"]==GL_CLAMP_TO_EDGE && event["wrapT"]==GL_CLAMP_TO_EDGE);
        if(event["controlIndex"].toInt()==2)check(event["sourceDigest"]=="" && pixels==QJsonArray{1,1});
        ++records;
    }
    check(records==5);
    Renderer original;auto inspected=Stub::inspections;original.drawQuad(o,rect,999);
    check(Stub::inspections==inspected); // ordinary path remains hardware LINEAR
    std::cout<<checks<<" manual sampler actual consumer CPU-stub checks PASS\n";
    return 0;
}
};
int main(){return OfflineCommands::run();}
