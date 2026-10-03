// Standalone staged producer. Own Wayland connection/context, no Qt QPA.
#include "CommitLedger.hpp"
#include "BackendPolicy.hpp"
#include "LibraryMaterial.hpp"
#include "ReadbackImage.hpp"
#include "CausalImage.hpp"
#include "SamplingExperiment.hpp"
#include "QuantizedOver.hpp"
#include "PixelCoverage.hpp"
#include <QByteArray>
#include <QCryptographicHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <png.h>
#include <wayland-client.h>
#include <wayland-egl.h>
#include "layer-shell-client.h"
#include "presentation-client.h"
#include "viewporter-client.h"
#include "xdg-output-client.h"
#include "fractional-scale-client.h"
#include <chrono>
#include <fcntl.h>
#include <iostream>
#include <memory>
#include <poll.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdio>
#include <set>

using namespace OwnedRoute;
static uint64_t monotonicNs(){timespec t{};clock_gettime(CLOCK_MONOTONIC,&t);return uint64_t(t.tv_sec)*1000000000+t.tv_nsec;}
static QString qs(const std::string& s){return QString::fromStdString(s);}
static void emitEvent(const QJsonObject& value){std::cout<<QJsonDocument(value).toJson(QJsonDocument::Compact).constData()<<'\n'<<std::flush;}
static QJsonObject rectangleJson(const Rect& r){return {{"x",r.x},{"y",r.y},{"width",r.width},{"height",r.height}};}
static Rect rectangle(const QJsonValue& v){auto j=v.toObject();Rect r{j["x"].toDouble(NAN),j["y"].toDouble(NAN),j["width"].toDouble(NAN),j["height"].toDouble(NAN)};if(!r.valid())throw std::invalid_argument("invalid finite rectangle");return r;}
static Identity identity(const QJsonObject& j){double pid=j["pid"].toDouble();if(!std::isfinite(pid)||pid<1||pid>INT32_MAX||std::floor(pid)!=pid)throw std::invalid_argument("invalid PID number");Identity i{j["stableId"].toString().toStdString(),int64_t(pid)};if(!i.valid()||pid!=i.pid||pid>INT32_MAX)throw std::invalid_argument("invalid exact identity");return i;}
static QJsonArray identityJson(const std::vector<Identity>& ids){QJsonArray out;for(const auto& id:ids)out.append(QJsonObject{{"stableId",qs(id.stable)},{"pid",double(id.pid)}});return out;}
static std::vector<Identity> identities(const QJsonObject& j){auto array=j["identities"].toArray();if(array.empty()||array.size()>64)throw std::invalid_argument("exact complete identity vector required");std::vector<Identity> out;std::set<std::string> seen;for(const auto& value:array){auto id=identity(value.toObject());if(!seen.insert(id.stable).second)throw std::invalid_argument("duplicate identity");out.push_back(id);}return out;}
static QJsonArray membersJson(const std::vector<MemberFrame>& members){QJsonArray out;for(const auto& m:members)out.append(QJsonObject{{"stableId",qs(m.source.identity.stable)},{"pid",double(m.source.identity.pid)},{"digest",qs(m.source.digest)},{"rectangle",rectangleJson(m.rectangle)}});return out;}

class Renderer {
    friend struct OfflineCommands;
    struct Output {
        Renderer* owner=nullptr;uint32_t registry=0;uint64_t generation=0;
        wl_output* proxy=nullptr;zxdg_output_v1* logical=nullptr;
        std::string name;int x=0,y=0,width=0,height=0,integerScale=1,preferredScale=0,transform=0,pixelWidth=0,pixelHeight=0,refresh=0;
        bool alive=true,configured=false,frameReady=true,entered=false;
        wl_surface* surface=nullptr;zwlr_layer_surface_v1* layer=nullptr;wp_viewport* viewport=nullptr;
        wp_fractional_scale_v1* fractional=nullptr;wl_egl_window* window=nullptr;EGLSurface egl=EGL_NO_SURFACE;wl_callback* callback=nullptr;
        int bufferWidth=0,bufferHeight=0;uint64_t outstanding=0,lastFrameCallbackNs=0;
        Rect from;bool endpointPresented=false,clearCommitted=false;
        std::array<GLuint,2> prefixTextures{},prefixFramebuffers{};int prefixRead=0,prefixWidth=0,prefixHeight=0;size_t prefixPassCount=0;uint64_t prefixGeneration=0;
        QJsonArray prefixConfigurations;QJsonObject prefixFinalCopy;
    };
    struct Feedback {Renderer* owner;Output* output;uint64_t generation;Frame frame;struct wp_presentation_feedback* proxy;bool sync=false,mismatch=false;};
    wl_display* display=nullptr;wl_registry* registry=nullptr;wl_compositor* compositor=nullptr;
    zwlr_layer_shell_v1* shell=nullptr;wp_presentation* presentation=nullptr;wp_viewporter* viewporter=nullptr;
    zxdg_output_manager_v1* outputManager=nullptr;wp_fractional_scale_manager_v1* fractionalManager=nullptr;
    std::vector<std::unique_ptr<Output>> outputs;std::map<uint64_t,std::unique_ptr<Feedback>> feedbacks;
    EGLDisplay eglDisplay=EGL_NO_DISPLAY;EGLContext context=EGL_NO_CONTEXT;EGLConfig config{};
    GLuint shader=0,texture=0;std::vector<GLuint> familyTextures;std::vector<Identity> familyIdentities;GLint positionLocation=-1,uvLocation=-1;
    uint64_t generationSerial=0;uint32_t clockId=UINT32_MAX;CommitLedger ledger;
    Identity routeIdentity;std::string digest,operation;Rect target,nativeRect,atlasRect,iconRect;
    QJsonObject waitingRetarget;std::vector<Output*> required;
    uint64_t startedNs=0,durationNs=400000000;bool running=false,readySent=false,endpointSent=false,quit=false,announced=false,surfacesEnabled=true,swapping=false;
    std::string deferredCancel;uint64_t routeAcceptedNs=0,endpointHeldNs=0;
    int readbackDirectory=-1;std::set<std::string> readbackSamples,causalSamples;
    bool quantizedOver=false,overCleanupFailed=false;GLuint copyShader=0;GLint outputSizeLocation=-1,prefixLocation=-1,copyPosition=-1,copySize=-1,coverageLocation=-1,sampleRectLocation=-1;
    bool manualSampling=false;GLint atlasSizeLocation=-1;std::map<GLuint,OwnedSampling::Texture> samplerTextures;
    bool causalFixture=false;std::array<GLuint,3> controlTextures{};std::set<uint64_t> controlledGenerations;
    struct CausalObservation {GLint readFramebuffer=-1;GLuint prefixTexture=0;size_t observedPrefixCount=0;QJsonObject readTargetCopy;std::string kind;size_t prefix=0;std::vector<int> controls;std::vector<unsigned char> rgba,nativeRGBA;unsigned nativeFormat=0,nativeType=0;std::string nativeBytesDigest;};
    size_t uploadCount=0,transparentCommitCount=0;bool backendSupported=false,rasterFixture=false;double sampleProgress=0;QByteArray input;
    static GLuint compile(GLenum type,const char* source){GLuint s=glCreateShader(type);glShaderSource(s,1,&source,nullptr);glCompileShader(s);GLint ok=0;glGetShaderiv(s,GL_COMPILE_STATUS,&ok);if(!ok){glDeleteShader(s);throw std::runtime_error("GPU shader compilation failed");}return s;}
    void initializeEGL(){
        eglDisplay=eglGetPlatformDisplay(EGL_PLATFORM_WAYLAND_KHR,display,nullptr);
        EGLint major=0,minor=0,count=0;
        if(eglDisplay==EGL_NO_DISPLAY||!eglInitialize(eglDisplay,&major,&minor)||!eglBindAPI(EGL_OPENGL_ES_API))throw std::runtime_error("owned EGL display unavailable");
        const EGLint attributes[]={EGL_SURFACE_TYPE,EGL_WINDOW_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_NONE};
        if(!eglChooseConfig(eglDisplay,attributes,&config,1,&count)||count!=1)throw std::runtime_error("transparent EGL config unavailable");
        const EGLint ctx[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE};context=eglCreateContext(eglDisplay,config,EGL_NO_CONTEXT,ctx);
        if(context==EGL_NO_CONTEXT)throw std::runtime_error("owned EGL context unavailable");
    }
    void initializeShader(){
        if(shader){if(!backendSupported)throw std::runtime_error("unreviewed EGL commit backend");return;}
        QJsonArray precisionRecords;bool precisionSupported=true;
        for(const auto stage:{GL_VERTEX_SHADER,GL_FRAGMENT_SHADER})for(const auto kind:{GL_LOW_FLOAT,GL_MEDIUM_FLOAT,GL_HIGH_FLOAT}){
            GLint range[2]={0,0},bits=0;glGetShaderPrecisionFormat(stage,kind,range,&bits);
            precisionRecords.append(QJsonObject{{"stage",stage==GL_VERTEX_SHADER?"vertex":"fragment"},{"kind",kind==GL_HIGH_FLOAT?"high":kind==GL_MEDIUM_FLOAT?"medium":"low"},{"rangeMin",range[0]},{"rangeMax",range[1]},{"precisionBits",bits}});
            if(kind==GL_HIGH_FLOAT&&(bits<23||range[0]<127||range[1]<127))precisionSupported=false;
        }
        const auto precisionError=glGetError();
        emitEvent({{"event","shaderPrecision"},{"observed",precisionRecords},{"error",double(precisionError)},{"supported",precisionSupported&&precisionError==GL_NO_ERROR},{"pixelProof",false}});
        if(!precisionSupported||precisionError!=GL_NO_ERROR)throw std::runtime_error("required actual highp shader precision unavailable; no source upload");
        GLuint vertex=compile(GL_VERTEX_SHADER,quantizedOver?OwnedOver::copyVertex:"precision highp float;attribute highp vec2 position;attribute highp vec2 uv;varying highp vec2 tex;void main(){tex=uv;gl_Position=vec4(position,0.,1.);}");
        const char* selectedFragment=quantizedOver?OwnedOver::fragment:manualSampling?OwnedSampling::manualFragment:OwnedSampling::linearFragment;
        GLuint fragment=compile(GL_FRAGMENT_SHADER,selectedFragment);
        shader=glCreateProgram();glAttachShader(shader,vertex);glAttachShader(shader,fragment);glLinkProgram(shader);glDeleteShader(vertex);glDeleteShader(fragment);
        GLint ok=0;glGetProgramiv(shader,GL_LINK_STATUS,&ok);if(!ok)throw std::runtime_error("GPU shader linking failed");
        positionLocation=glGetAttribLocation(shader,"position");uvLocation=glGetAttribLocation(shader,"uv");
        if(manualSampling){atlasSizeLocation=glGetUniformLocation(shader,"atlasSize");if(atlasSizeLocation<0)throw std::runtime_error("manual bilinear extent uniform absent");
            emitEvent({{"event","samplingExperiment"},{"policy",OwnedSampling::policy},{"fragmentSHA256",QString::fromLatin1(QCryptographicHash::hash(QByteArray(selectedFragment),QCryptographicHash::Sha256).toHex())},{"rasterDiagnostic",rasterFixture},{"nativeAuthority",false},{"pixelProof",false}});}
        if(quantizedOver){
            outputSizeLocation=glGetUniformLocation(shader,"outputSize");prefixLocation=glGetUniformLocation(shader,"prefix");coverageLocation=glGetUniformLocation(shader,"coverageBounds");sampleRectLocation=glGetUniformLocation(shader,"sampleRect");
            if(outputSizeLocation<0||prefixLocation<0||coverageLocation<0||sampleRectLocation<0||positionLocation<0||uvLocation!=-1)throw std::runtime_error("quantized over coverage uniforms/vertex roles missing");
            GLuint v=compile(GL_VERTEX_SHADER,OwnedOver::copyVertex),f=compile(GL_FRAGMENT_SHADER,OwnedOver::copyFragment);
            copyShader=glCreateProgram();glAttachShader(copyShader,v);glAttachShader(copyShader,f);glLinkProgram(copyShader);glDeleteShader(v);glDeleteShader(f);
            GLint linked=0;glGetProgramiv(copyShader,GL_LINK_STATUS,&linked);copyPosition=glGetAttribLocation(copyShader,"position");copySize=glGetUniformLocation(copyShader,"outputSize");
            if(!linked||!shader||!copyShader||shader==copyShader||copyPosition<0||copySize<0)throw std::runtime_error("prefix copy program unavailable");
            const auto hash=[](const char* text){return QString::fromLatin1(QCryptographicHash::hash(QByteArray(text),QCryptographicHash::Sha256).toHex());};
            emitEvent({{"event","quantizedOverExperiment"},{"overProgram",int(shader)},{"copyProgram",int(copyShader)},{"policy",OwnedOver::policy},{"coveragePolicy",OwnedCoverage::policy},{"vertexSHA256",hash(OwnedOver::copyVertex)},{"fragmentSHA256",hash(OwnedOver::fragment)},{"copyFragmentSHA256",hash(OwnedOver::copyFragment)},{"rasterDiagnostic",rasterFixture},{"nativeAuthority",false},{"pixelProof",false}});
        }
        emitEvent({{"event","rasterPathSelected"},{"path",quantizedOver?"shader-per-layer-quantized-over":"fixed-function-over"},{"sampler",manualSampling?"four-nearest-centers-highp-bilinear":"hardware-linear"},{"rasterDiagnostic",rasterFixture},{"nativeAuthority",false},{"pixelProof",false}});
        const auto safe=[](const char* value){return std::string(value?value:"");};
        const auto vendor=safe(eglQueryString(eglDisplay,EGL_VENDOR));
        const auto renderer=safe(reinterpret_cast<const char*>(glGetString(GL_RENDERER)));
        const auto version=safe(reinterpret_cast<const char*>(glGetString(GL_VERSION)));
        const auto proofs=installedMesaMaterialProofs();QJsonArray materials;bool material=true;
        for(const auto& proof:proofs){materials.append(proof.json());material=material&&proof.matches;}
        emitEvent({{"event","backendObserved"},{"eglVendor",qs(vendor)},{"renderer",qs(renderer)},{"version",qs(version)},{"eglVersion",qs(safe(eglQueryString(eglDisplay,EGL_VERSION)))},{"nativeAuthority",false},{"reviewed",reviewedGPUBackend(vendor,version,renderer) && material},{"mappedMaterialMatches",material},{"materials",materials}});
        if(!reviewedGPUBackend(vendor,version,renderer)||!material)throw std::runtime_error("unreviewed EGL commit backend; no route authority");
        const bool ditherBefore=glIsEnabled(GL_DITHER)==GL_TRUE;
        const auto inspectionError=glGetError();
        if(inspectionError!=GL_NO_ERROR)throw std::runtime_error("raster state inspection failed before source upload");
        glDisable(GL_DITHER);
        const bool ditherAfter=glIsEnabled(GL_DITHER)==GL_TRUE;
        const auto policyError=glGetError();
        emitEvent({{"event","rasterState"},{"ditherBefore",ditherBefore},{"ditherAfter",ditherAfter},{"error",double(policyError)},{"pixelProof",false}});
        if(ditherAfter||policyError!=GL_NO_ERROR)throw std::runtime_error("deterministic raster state unavailable; no source upload");
        backendSupported=true;
        emitEvent({{"event","gpu"},{"eglVendor",qs(vendor)},{"renderer",qs(renderer)},{"version",reinterpret_cast<const char*>(glGetString(GL_VERSION))}});
    }
    void releasePrefix(Output& o){
        if(!o.prefixTextures[0]&&!o.prefixTextures[1]&&!o.prefixFramebuffers[0]&&!o.prefixFramebuffers[1])return;
        if(eglGetCurrentContext()!=context&&(o.egl==EGL_NO_SURFACE||!eglMakeCurrent(eglDisplay,o.egl,o.egl,context))){overCleanupFailed=true;}
        else{glBindFramebuffer(GL_FRAMEBUFFER,0);glDeleteFramebuffers(2,o.prefixFramebuffers.data());glDeleteTextures(2,o.prefixTextures.data());if(glGetError()!=GL_NO_ERROR)overCleanupFailed=true;}
        o.prefixTextures={};o.prefixFramebuffers={};o.prefixGeneration=0;o.prefixWidth=0;o.prefixHeight=0;o.prefixRead=0;o.prefixPassCount=0;
    }
    void closeOutput(Output& o){
        releasePrefix(o);
        for(auto i=feedbacks.begin();i!=feedbacks.end();){if(i->second->output==&o){wp_presentation_feedback_destroy(i->second->proxy);i=feedbacks.erase(i);}else ++i;}
        o.outstanding=0;
        if(o.callback){wl_callback_destroy(o.callback);o.callback=nullptr;}
        eglMakeCurrent(eglDisplay,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);
        if(o.egl!=EGL_NO_SURFACE){eglDestroySurface(eglDisplay,o.egl);o.egl=EGL_NO_SURFACE;}
        if(o.window){wl_egl_window_destroy(o.window);o.window=nullptr;}
        if(o.fractional){wp_fractional_scale_v1_destroy(o.fractional);o.fractional=nullptr;}
        if(o.viewport){wp_viewport_destroy(o.viewport);o.viewport=nullptr;}
        if(o.layer){zwlr_layer_surface_v1_destroy(o.layer);o.layer=nullptr;}
        if(o.surface){wl_surface_destroy(o.surface);o.surface=nullptr;}
        o.configured=false;o.clearCommitted=false;
    }
    void cancel(const std::string& reason){
        const bool was=ledger.isActive()||!required.empty();auto token=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();ledger.cancel();running=false;waitingRetarget={};
        if(swapping){deferredCancel=reason;return;}
        surfacesEnabled=false;
        for(auto& o:outputs)closeOutput(*o);
        required.clear();readySent=false;endpointSent=false;announced=false;
        if(was)emitEvent({{"event","cancelled"},{"token",qs(token)},{"reason",qs(reason)},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()},{"nativeAuthority",false}});
    }
    void changed(Output& o){
        o.generation=++generationSerial;o.clearCommitted=false;
        if(ledger.isActive())cancel("output generation changed");
        announced=false;
    }
    void createSurface(Output& o){
        if(o.surface||!o.alive||o.name.empty()||o.width<=0||o.height<=0)return;
        o.generation=++generationSerial;o.surface=wl_compositor_create_surface(compositor);
        wl_surface_set_opaque_region(o.surface,nullptr);
        wl_region* empty=wl_compositor_create_region(compositor);wl_surface_set_input_region(o.surface,empty);wl_region_destroy(empty);
        o.layer=zwlr_layer_shell_v1_get_layer_surface(shell,o.surface,o.proxy,ZWLR_LAYER_SHELL_V1_LAYER_OVERLAY,"hoskinson-window-motion");
        zwlr_layer_surface_v1_set_anchor(o.layer,ZWLR_LAYER_SURFACE_V1_ANCHOR_TOP|ZWLR_LAYER_SURFACE_V1_ANCHOR_BOTTOM|ZWLR_LAYER_SURFACE_V1_ANCHOR_LEFT|ZWLR_LAYER_SURFACE_V1_ANCHOR_RIGHT);
        zwlr_layer_surface_v1_set_keyboard_interactivity(o.layer,ZWLR_LAYER_SURFACE_V1_KEYBOARD_INTERACTIVITY_NONE);
        zwlr_layer_surface_v1_set_exclusive_zone(o.layer,-1);zwlr_layer_surface_v1_set_size(o.layer,0,0);
        static const zwlr_layer_surface_v1_listener layerListener={
            [](void* p,zwlr_layer_surface_v1* layer,uint32_t serial,uint32_t w,uint32_t h){auto& o=*static_cast<Output*>(p);zwlr_layer_surface_v1_ack_configure(layer,serial);if(int(w)!=o.width||int(h)!=o.height){o.owner->cancel("layer extent disagrees with logical output");return;}o.configured=true;o.frameReady=true;},
            [](void* p,zwlr_layer_surface_v1*){auto& o=*static_cast<Output*>(p);o.owner->cancel("layer closed");}
        };
        zwlr_layer_surface_v1_add_listener(o.layer,&layerListener,&o);
        o.viewport=wp_viewporter_get_viewport(viewporter,o.surface);wp_viewport_set_destination(o.viewport,o.width,o.height);
        o.fractional=wp_fractional_scale_manager_v1_get_fractional_scale(fractionalManager,o.surface);
        static const wp_fractional_scale_v1_listener fractionalListener={[](void* p,wp_fractional_scale_v1*,uint32_t scale){auto& o=*static_cast<Output*>(p);if(!scale||scale>960){o.owner->cancel("invalid fractional output scale");return;}if(o.preferredScale!=int(scale)){o.preferredScale=scale;o.owner->changed(o);}}};
        wp_fractional_scale_v1_add_listener(o.fractional,&fractionalListener,&o);
        wl_surface_set_buffer_scale(o.surface,1);wl_surface_commit(o.surface);
    }
    bool makeCurrent(Output& o){
        const double scale=o.preferredScale?o.preferredScale/120.0:o.integerScale;
        const int width=std::ceil(o.width*scale),height=std::ceil(o.height*scale);
        if(width<=0||height<=0||width>16384||height>16384)throw std::runtime_error("invalid output buffer extent");
        if(!o.window){o.window=wl_egl_window_create(o.surface,width,height);if(!o.window)throw std::runtime_error("owned EGL window unavailable");o.egl=eglCreateWindowSurface(eglDisplay,config,reinterpret_cast<EGLNativeWindowType>(o.window),nullptr);}
        if(o.egl==EGL_NO_SURFACE)throw std::runtime_error("owned EGL surface unavailable");
        if(o.bufferWidth!=width||o.bufferHeight!=height){wl_egl_window_resize(o.window,width,height,0,0);o.bufferWidth=width;o.bufferHeight=height;}
        if(!eglMakeCurrent(eglDisplay,o.egl,o.egl,context))return false;
        eglSwapInterval(eglDisplay,0);initializeShader();return true;
    }
    GLuint upload(const std::string& path,const std::string& expected,int expectedWidth,int expectedHeight){
        if(path.empty()||path[0]!='/')throw std::invalid_argument("absolute immutable PNG path required");
        int fd=open(path.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)throw std::runtime_error("snapshot open failed");
        struct Close{int fd;~Close(){close(fd);}}closeFile{fd};struct stat st{};
        if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_uid!=geteuid()||(st.st_mode&0077)||st.st_size<=0||st.st_size>134217728)throw std::runtime_error("snapshot is not private immutable input");
        QByteArray bytes;bytes.resize(st.st_size);size_t offset=0;
        while(offset<size_t(bytes.size())){ssize_t n=read(fd,bytes.data()+offset,bytes.size()-offset);if(n<=0)throw std::runtime_error("snapshot short read");offset+=n;}
        if(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex().toStdString()!=expected)throw std::runtime_error("snapshot digest disagrees");
        png_image image{};image.version=PNG_IMAGE_VERSION;
        if(!png_image_begin_read_from_memory(&image,bytes.constData(),bytes.size()))throw std::runtime_error("PNG decode failed");
        struct Free{png_image* i;~Free(){png_image_free(i);}}freeImage{&image};
        if(image.width!=unsigned(expectedWidth)||image.height!=unsigned(expectedHeight))throw std::runtime_error("PNG pixel extent disagrees with captured metadata");
        if(image.width>8192||image.height>8192||!image.width||!image.height)throw std::runtime_error("PNG extent unsupported");
        image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> rgba(PNG_IMAGE_SIZE(image));
        if(!png_image_finish_read(&image,nullptr,rgba.data(),0,nullptr))throw std::runtime_error("PNG pixel decode failed");
        for(size_t i=0;i<rgba.size();i+=4)for(size_t c=0;c<3;c++)rgba[i+c]=(unsigned(rgba[i+c])*rgba[i+3]+127)/255;
        GLuint uploaded=0;glGenTextures(1,&uploaded);glBindTexture(GL_TEXTURE_2D,uploaded);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,manualSampling?GL_NEAREST:GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,manualSampling?GL_NEAREST:GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        glPixelStorei(GL_UNPACK_ALIGNMENT,1);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image.width,image.height,0,GL_RGBA,GL_UNSIGNED_BYTE,rgba.data());
        if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&uploaded);throw std::runtime_error("GPU snapshot upload failed");}
        if(manualSampling)samplerTextures[uploaded]={int(image.width),int(image.height),-1,expected,false};++uploadCount;
        emitEvent({{"event","uploaded"},{"digest",qs(expected)},{"pixels",QJsonArray{int(image.width),int(image.height)}},{"uploadCount",int(uploadCount)}});return uploaded;
    }
    QJsonArray sourceDigests()const{QJsonArray array;for(const auto& source:ledger.familySources())array.append(QJsonObject{{"stableId",qs(source.identity.stable)},{"pid",double(source.identity.pid)},{"digest",qs(source.digest)}});return array;}
    void notifyAuthority(){
        if(rasterFixture)return;
        if(ledger.nativeReady()&&!readySent){readySent=true;emitEvent({{"event","ready"},{"token",qs(ledger.token())},{"stableId",qs(routeIdentity.stable)},{"pid",double(routeIdentity.pid)},{"digest",qs(digest)},{"servicePromoted",true},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()}});}
        if(ledger.nativeEndpoint()&&!endpointSent){endpointSent=true;endpointHeldNs=monotonicNs();emitEvent({{"event","endpoint"},{"token",qs(ledger.token())},{"stableId",qs(routeIdentity.stable)},{"pid",double(routeIdentity.pid)},{"digest",qs(digest)},{"servicePromoted",true},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()}});}
    }
    void emitPresented(const Presented& p,const char* event,bool accepted){
        const auto& frame=p.frame;
        emitEvent({{"event",event},{"accepted",accepted},{"token",qs(frame.token)},{"digest",qs(frame.digest)},{"stableId",qs(frame.identity.stable)},{"pid",double(frame.identity.pid)},{"output",qs(frame.output)},{"generation",double(frame.generation)},{"sequence",QString::number(frame.sequence)},{"submittedNs",QString::number(frame.submittedNs)},{"timestampNs",QString::number(p.timestampNs)},{"feedbackDeliveredNs",QString::number(monotonicNs())},{"outputSequence",QString::number(p.compositorSequence)},{"rectangle",rectangleJson(frame.rectangle)},{"progress",frame.progress},{"endpoint",frame.endpoint},{"members",membersJson(frame.members)},{"bufferWidth",frame.bufferWidth},{"bufferHeight",frame.bufferHeight}});
    }
    void feedbackDone(Feedback& f,uint64_t ns,uint64_t sequence){
        auto* o=f.output;const auto frame=f.frame;const auto generation=f.generation;auto number=frame.sequence;
        Result result=Result::Rejected;
        if(o->alive&&o->generation==generation&&f.sync&&!f.mismatch&&clockId==CLOCK_MONOTONIC)result=ledger.present(number,ns,sequence);
        else {cancel("presentation output/clock mismatch");return;}
        emitPresented(Presented{frame,ns,sequence},result==Result::Deferred?"presentationObservedBeforeSwap":"presented",result==Result::RecordedCurrent||result==Result::RecordedOld);
        if(o->outstanding==number)o->outstanding=0;
        if(result==Result::RecordedCurrent && frame.endpoint)o->endpointPresented=true;
        auto i=feedbacks.find(number);if(i!=feedbacks.end()){wp_presentation_feedback_destroy(i->second->proxy);feedbacks.erase(i);}
        notifyAuthority();
    }
    bool needsDraw(const Output& o)const{
        if(!o.alive||!o.configured||!o.frameReady||o.outstanding||o.endpointPresented)return false;
        return !o.clearCommitted||(ledger.isActive()&&std::find(required.begin(),required.end(),&o)!=required.end());
    }
    void drawQuad(Output& o,const Rect& rect,GLuint texture,QJsonObject* coverageRecord=nullptr){
        const GLfloat left=2*(rect.x-o.x)/o.width-1,right=2*(rect.x+rect.width-o.x)/o.width-1;
        const GLfloat top=1-2*(rect.y-o.y)/o.height,bottom=1-2*(rect.y+rect.height-o.y)/o.height;
        const GLfloat quad[]={left,top,right,top,left,bottom,right,bottom},fullscreen[]={-1,1,1,1,-1,-1,1,-1},uv[]={0,0,1,0,0,1,1,1};
        const GLfloat* positions=quantizedOver?fullscreen:quad;
        glBindTexture(GL_TEXTURE_2D,texture);
        if(manualSampling){
            auto found=samplerTextures.find(texture);if(found==samplerTextures.end())throw std::runtime_error("manual sampler texture extent unavailable");
            auto& source=found->second;OwnedSampling::requireExtent(source);glUniform2f(atlasSizeLocation,source.width,source.height);
            if(!source.announced){
                GLint min=0,mag=0,s=0,t=0;GLfloat extent[2]={0,0};
                glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,&min);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,&mag);
                glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,&s);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,&t);glGetUniformfv(shader,atlasSizeLocation,extent);
                const auto error=glGetError();OwnedSampling::requireState(source,min,mag,s,t,extent[0],extent[1],error);source.announced=true;
                emitEvent({{"event","samplingConfigured"},{"policy",OwnedSampling::policy},{"textureId",int(texture)},{"sourceDigest",qs(source.digest)},{"pixels",QJsonArray{source.width,source.height}},{"controlIndex",source.controlIndex},{"minFilter",min},{"magFilter",mag},{"wrapS",s},{"wrapT",t},{"extentUniform",QJsonArray{extent[0],extent[1]}},{"inspectionError",double(error)},{"nativeAuthority",false},{"pixelProof",false}});
            }
        }
        glVertexAttribPointer(positionLocation,2,GL_FLOAT,GL_FALSE,0,positions);if(uvLocation>=0)glVertexAttribPointer(uvLocation,2,GL_FLOAT,GL_FALSE,0,uv);
        if(quantizedOver){
            if(!coverageRecord)throw std::runtime_error("quantized full-screen coverage record missing");
            GLint enabled=0,size=0,type=0,normalized=0,stride=0,buffer=0;void* pointer=nullptr;
            glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_SIZE,&size);glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_NORMALIZED,&normalized);glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);glGetVertexAttribiv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);glGetVertexAttribPointerv(positionLocation,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
            const auto vertexError=glGetError();
            if(enabled!=1||size!=2||type!=GL_FLOAT||normalized!=0||stride!=0||buffer!=0||pointer!=positions||vertexError!=GL_NO_ERROR)throw std::runtime_error("actual full-screen vertex binding differs");
            const auto* actual=static_cast<const GLfloat*>(pointer);QJsonArray values;
            for(unsigned i=0;i<8;++i){if(actual[i]!=fullscreen[i])throw std::runtime_error("actual full-screen position differs");values.append(actual[i]);}
            (*coverageRecord)["fullscreenPositions"]=values;(*coverageRecord)["vertexState"]=QJsonObject{{"enabled",enabled},{"size",size},{"type",type},{"normalized",normalized},{"stride",stride},{"buffer",buffer},{"inspectionError",double(vertexError)}};
        }
        glDrawArrays(GL_TRIANGLE_STRIP,0,4);
    }
    void beginPrefix(Output& o){
        if(o.prefixGeneration!=o.generation||o.prefixWidth!=o.bufferWidth||o.prefixHeight!=o.bufferHeight){
            releasePrefix(o);if(overCleanupFailed)throw std::runtime_error("prefix resource teardown failed");
            if(!o.generation||o.bufferWidth<=0||o.bufferHeight<=0||o.bufferWidth>16384||o.bufferHeight>16384||uint64_t(o.bufferWidth)*o.bufferHeight*8>256*1024*1024)throw std::runtime_error("prefix current generation/extent bound exceeded");
            glActiveTexture(GL_TEXTURE0);glGenTextures(2,o.prefixTextures.data());glGenFramebuffers(2,o.prefixFramebuffers.data());
            OwnedOver::requireBuffers(o.generation,o.bufferWidth,o.bufferHeight,o.prefixTextures[0],o.prefixTextures[1],o.prefixFramebuffers[0]);
            if(!o.prefixFramebuffers[1]||o.prefixFramebuffers[0]==o.prefixFramebuffers[1]||glGetError()!=GL_NO_ERROR)throw std::runtime_error("separate prefix framebuffer allocation failed");
            for(size_t i=0;i<2;++i){
                glBindTexture(GL_TEXTURE_2D,o.prefixTextures[i]);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
                glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,o.bufferWidth,o.bufferHeight,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
                glBindFramebuffer(GL_FRAMEBUFFER,o.prefixFramebuffers[i]);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,o.prefixTextures[i],0);
                if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE||glGetError()!=GL_NO_ERROR)throw std::runtime_error("bounded RGBA8 prefix attachment unavailable");
            }
            o.prefixGeneration=o.generation;o.prefixWidth=o.bufferWidth;o.prefixHeight=o.bufferHeight;
        }
        o.prefixRead=0;o.prefixPassCount=0;glDisable(GL_BLEND);glBindFramebuffer(GL_FRAMEBUFFER,o.prefixFramebuffers[0]);glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("transparent prefix reset failed");
    }
    QJsonObject copyPrefix(Output& o,GLuint source,GLuint destination){
        if(!source||(source!=o.prefixTextures[0]&&source!=o.prefixTextures[1]))throw std::runtime_error("copy source is not current output prefix");
        glBindFramebuffer(GL_FRAMEBUFFER,destination);
        GLint copyAttachment=0,copyAttachmentType=0;
        if(destination){
            const int slot=destination==o.prefixFramebuffers[0]?0:destination==o.prefixFramebuffers[1]?1:-1;
            if(slot<0)throw std::runtime_error("copy target is not current output attachment");
            glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&copyAttachment);
            glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&copyAttachmentType);
            if(copyAttachmentType!=GL_TEXTURE||copyAttachment!=int(o.prefixTextures[slot])||GLuint(copyAttachment)==source||glGetError()!=GL_NO_ERROR)throw std::runtime_error("copy prefix attachment feedback or ownership differs");
        }
        glDisable(GL_BLEND);glUseProgram(copyShader);glActiveTexture(GL_TEXTURE1);glBindTexture(GL_TEXTURE_2D,source);
        glUniform1i(glGetUniformLocation(copyShader,"prefix"),1);glUniform2f(copySize,o.bufferWidth,o.bufferHeight);
        GLint actualProgram=0,actualFramebuffer=0,actualTexture=0,unit=-1,min=0,mag=0,s=0,t=0;GLfloat extent[2]={};
        glGetIntegerv(GL_CURRENT_PROGRAM,&actualProgram);glGetIntegerv(GL_FRAMEBUFFER_BINDING,&actualFramebuffer);glGetIntegerv(GL_TEXTURE_BINDING_2D,&actualTexture);
        glGetUniformiv(copyShader,glGetUniformLocation(copyShader,"prefix"),&unit);glGetUniformfv(copyShader,copySize,extent);
        glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,&min);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,&mag);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,&s);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,&t);
        const bool blend=glIsEnabled(GL_BLEND)==GL_TRUE;const auto inspection=glGetError();
        if(actualProgram!=int(copyShader)||actualFramebuffer!=int(destination)||actualTexture!=int(source)||unit!=1||extent[0]!=o.bufferWidth||extent[1]!=o.bufferHeight||min!=GL_NEAREST||mag!=GL_NEAREST||s!=GL_CLAMP_TO_EDGE||t!=GL_CLAMP_TO_EDGE||blend||inspection!=GL_NO_ERROR)throw std::runtime_error("actual prefix copy binding/state disagrees");
        const GLfloat positions[]={-1,1,1,1,-1,-1,1,-1};glEnableVertexAttribArray(copyPosition);glVertexAttribPointer(copyPosition,2,GL_FLOAT,GL_FALSE,0,positions);glDrawArrays(GL_TRIANGLE_STRIP,0,4);
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("exact nearest prefix copy failed");
        glUseProgram(shader);glEnableVertexAttribArray(positionLocation);if(uvLocation>=0)glEnableVertexAttribArray(uvLocation);glActiveTexture(GL_TEXTURE0);
        return {{"program",actualProgram},{"attachedTexture",copyAttachment},{"attachmentType",copyAttachmentType},{"framebuffer",actualFramebuffer},{"texture",actualTexture},{"unit",unit},{"extentUniform",QJsonArray{extent[0],extent[1]}},{"minFilter",min},{"magFilter",mag},{"wrapS",s},{"wrapT",t},{"blend",blend},{"inspectionError",double(inspection)}};
    }
    void drawLayer(Output& o,const Rect& rect,GLuint source,size_t prefix){
        if(!quantizedOver){drawQuad(o,rect,source);return;}
        const auto coverage=OwnedCoverage::geometry(rect.x,rect.y,rect.width,rect.height,o.x,o.y,o.width,o.height,o.bufferWidth,o.bufferHeight);
        if(prefix!=o.prefixPassCount+1)throw std::runtime_error("quantized layer order disagrees with current prefix");
        const int write=1-o.prefixRead;const GLuint previous=o.prefixTextures[o.prefixRead],next=o.prefixTextures[write];
        if(o.prefixGeneration!=o.generation||o.prefixWidth!=o.bufferWidth||o.prefixHeight!=o.bufferHeight)throw std::runtime_error("obsolete prefix output generation/extent");
        OwnedOver::requireBuffers(o.generation,o.bufferWidth,o.bufferHeight,previous,next,o.prefixFramebuffers[write]);
        if(!source||source==previous||source==next)throw std::runtime_error("source texture aliases current prefix attachment");
        const auto copied=copyPrefix(o,previous,o.prefixFramebuffers[write]);glDisable(GL_BLEND);glUniform1i(glGetUniformLocation(shader,"atlas"),0);glUniform1i(prefixLocation,1);glUniform2f(outputSizeLocation,o.bufferWidth,o.bufferHeight);
        glUniform4f(coverageLocation,coverage.bounds[0],coverage.bounds[1],coverage.bounds[2],coverage.bounds[3]);glUniform4f(sampleRectLocation,coverage.sample[0],coverage.sample[1],coverage.sample[2],coverage.sample[3]);
        GLfloat actualBounds[4]={},actualSample[4]={};GLint viewport[4]={};glGetIntegerv(GL_VIEWPORT,viewport);glGetUniformfv(shader,coverageLocation,actualBounds);glGetUniformfv(shader,sampleRectLocation,actualSample);const auto coverageError=glGetError();
        OwnedCoverage::requireUniforms(coverage,actualBounds,actualSample,coverageError);
        if(viewport[0]!=0||viewport[1]!=0||viewport[2]!=o.bufferWidth||viewport[3]!=o.bufferHeight)throw std::runtime_error("actual coverage viewport differs from owned buffer");
        // Inspect the actual previous-prefix sampler and current write target.
        glActiveTexture(GL_TEXTURE1);glBindTexture(GL_TEXTURE_2D,previous);
        GLint min=0,mag=0,wrapS=0,wrapT=0,framebuffer=0,attached=0,type=0,samples=0,sourceUnit=-1,prefixUnit=-1,readTexture=0,currentProgram=0,bits[4]={};GLfloat extent[2]={};
        glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,&min);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,&mag);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,&wrapS);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,&wrapT);
        glGetIntegerv(GL_TEXTURE_BINDING_2D,&readTexture);glGetIntegerv(GL_CURRENT_PROGRAM,&currentProgram);
        glGetIntegerv(GL_FRAMEBUFFER_BINDING,&framebuffer);glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&attached);glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&type);
        glGetIntegerv(GL_RED_BITS,bits);glGetIntegerv(GL_GREEN_BITS,bits+1);glGetIntegerv(GL_BLUE_BITS,bits+2);glGetIntegerv(GL_ALPHA_BITS,bits+3);glGetIntegerv(GL_SAMPLES,&samples);
        glGetUniformiv(shader,glGetUniformLocation(shader,"atlas"),&sourceUnit);glGetUniformiv(shader,prefixLocation,&prefixUnit);glGetUniformfv(shader,outputSizeLocation,extent);
        const bool blend=glIsEnabled(GL_BLEND)==GL_TRUE;const auto error=glGetError();
        if(readTexture!=int(previous)||currentProgram!=int(shader))throw std::runtime_error("actual previous prefix or shader binding differs");
        OwnedOver::requireState(framebuffer,o.prefixFramebuffers[write],attached,next,type,blend,bits,samples,min,mag,wrapS,wrapT,sourceUnit,prefixUnit,extent[0],extent[1],o.bufferWidth,o.bufferHeight,error);
        const auto sourceInfo=samplerTextures.find(source);if(sourceInfo==samplerTextures.end())throw std::runtime_error("quantized over immutable source missing");
        const auto& info=sourceInfo->second;
        QJsonObject configuration{{"prefixCopy",copied},{"prefixCount",int(prefix)},{"readTextureBinding",readTexture},{"shaderProgram",currentProgram},{"sourceDigest",qs(info.digest)},{"controlIndex",info.controlIndex},{"pixels",QJsonArray{info.width,info.height}},{"readTexture",int(previous)},{"writeTexture",int(next)},{"writeFramebuffer",framebuffer},{"attachedTexture",attached},{"attachmentType",type},{"blend",blend},{"bits",QJsonArray{bits[0],bits[1],bits[2],bits[3]}},{"samples",samples},{"minFilter",min},{"magFilter",mag},{"wrapS",wrapS},{"wrapT",wrapT},{"sourceUnit",sourceUnit},{"prefixUnit",prefixUnit},{"extentUniform",QJsonArray{extent[0],extent[1]}},{"inspectionError",double(error)}};
        configuration["coveragePolicy"]=OwnedCoverage::policy;configuration["sourceRectangle"]=rectangleJson(rect);configuration["logicalOutput"]=rectangleJson(Rect{double(o.x),double(o.y),double(o.width),double(o.height)});
        configuration["coverageUniform"]=QJsonArray{actualBounds[0],actualBounds[1],actualBounds[2],actualBounds[3]};configuration["sampleRectUniform"]=QJsonArray{actualSample[0],actualSample[1],actualSample[2],actualSample[3]};configuration["coverageInspectionError"]=double(coverageError);
        configuration["viewport"]=QJsonArray{viewport[0],viewport[1],viewport[2],viewport[3]};
        glActiveTexture(GL_TEXTURE0);drawQuad(o,rect,source,&configuration);
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("quantized source-over layer failed");
        GLint boundSource=0;glGetIntegerv(GL_TEXTURE_BINDING_2D,&boundSource);if(boundSource!=int(source)||glGetError()!=GL_NO_ERROR)throw std::runtime_error("actual immutable source texture binding differs");
        configuration["sourceTexture"]=int(source);configuration["sourceTextureBinding"]=boundSource;o.prefixConfigurations.append(configuration);
        o.prefixRead=write;o.prefixPassCount=prefix;
    }
    static std::string byteDigest(const std::vector<unsigned char>& bytes){return QCryptographicHash::hash(QByteArray(reinterpret_cast<const char*>(bytes.data()),bytes.size()),QCryptographicHash::Sha256).toHex().toStdString();}
    CausalObservation observeCausal(Output& o,const std::string& kind,size_t prefix=0,std::vector<int> controls={}){
        CausalObservation result;result.kind=kind;result.prefix=prefix;result.controls=std::move(controls);
        if(quantizedOver){
            if(o.prefixGeneration!=o.generation||o.prefixWidth!=o.bufferWidth||o.prefixHeight!=o.bufferHeight||!o.prefixPassCount
                ||(kind=="member-prefix"&&prefix!=o.prefixPassCount)
                ||(kind=="constant-control"&&result.controls.size()!=o.prefixPassCount))throw std::runtime_error("causal copy differs from complete current prefix");
            result.prefixTexture=o.prefixTextures[o.prefixRead];result.observedPrefixCount=o.prefixPassCount;
            result.readTargetCopy=copyPrefix(o,result.prefixTexture,0);
            glGetIntegerv(GL_FRAMEBUFFER_BINDING,&result.readFramebuffer);
            if(result.readFramebuffer!=0||glGetError()!=GL_NO_ERROR)throw std::runtime_error("causal reads require actual owned EGL default framebuffer");
        }
        GLint format=0,type=0,pack=0;glGetIntegerv(GL_IMPLEMENTATION_COLOR_READ_FORMAT,&format);glGetIntegerv(GL_IMPLEMENTATION_COLOR_READ_TYPE,&type);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("causal read pair inspection failed");
        OwnedCausal::validateReadPair(format,type);result.nativeFormat=format;result.nativeType=type;
        const uint64_t count=uint64_t(o.bufferWidth)*o.bufferHeight*4;
        const auto read=[&](unsigned f,unsigned t){
            std::vector<unsigned char> bytes(count);glPixelStorei(GL_PACK_ALIGNMENT,1);glReadPixels(0,0,o.bufferWidth,o.bufferHeight,f,t,bytes.data());const auto error=glGetError();glPixelStorei(GL_PACK_ALIGNMENT,pack);const auto restored=glGetError();
            if(error!=GL_NO_ERROR||restored!=GL_NO_ERROR)throw std::runtime_error("causal read/pack restore failed");return bytes;
        };
        result.rgba=OwnedReadback::topLeftRows(read(GL_RGBA,GL_UNSIGNED_BYTE),o.bufferWidth,o.bufferHeight);
        auto native=read(format,type);result.nativeBytesDigest=byteDigest(native);
        result.nativeRGBA=OwnedReadback::topLeftRows(OwnedCausal::nativeToRGBA(std::move(native),format,type),o.bufferWidth,o.bufferHeight);
        return result;
    }
    void initializeControls(){
        if(controlTextures[0])return;
        GLint unpack=0;glGetIntegerv(GL_UNPACK_ALIGNMENT,&unpack);glPixelStorei(GL_UNPACK_ALIGNMENT,1);glGenTextures(3,controlTextures.data());
        for(size_t i=0;i<controlTextures.size();++i){glBindTexture(GL_TEXTURE_2D,controlTextures[i]);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,manualSampling?GL_NEAREST:GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,manualSampling?GL_NEAREST:GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,1,1,0,GL_RGBA,GL_UNSIGNED_BYTE,OwnedCausal::controls()[i].data());if(manualSampling)samplerTextures[controlTextures[i]]={1,1,int(i),"",false};}
        const auto uploaded=glGetError();glPixelStorei(GL_UNPACK_ALIGNMENT,unpack);const auto restored=glGetError();
        if(uploaded!=GL_NO_ERROR||restored!=GL_NO_ERROR)throw std::runtime_error("constant control texture upload failed");
        emitEvent({{"event","diagnosticControlsUploaded"},{"textureCount",3},{"familyUploadCount",int(uploadCount)},{"sourceProof",false},{"nativeAuthority",false}});
    }
    void observeControls(Output& o,std::vector<CausalObservation>& records){
        if(controlledGenerations.contains(o.generation))return;
        initializeControls();const Rect whole{double(o.x),double(o.y),double(o.width),double(o.height)};
        for(const auto& order:{std::vector<int>{1},std::vector<int>{0,1},std::vector<int>{0,1,2}}){
            if(quantizedOver)beginPrefix(o);else{glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);}
            size_t prefix=0;for(int index:order)drawLayer(o,whole,controlTextures[index],++prefix);
            if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("constant control draw failed");
            records.push_back(observeCausal(o,"constant-control",0,order));
        }
        controlledGenerations.insert(o.generation);
        if(quantizedOver)beginPrefix(o);
        glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
    }
    void publishCausal(Output& o,const Frame& frame,const std::vector<CausalObservation>& records){
        for(size_t i=0;i<records.size();++i){const auto& r=records[i];
            const auto stem="causal-"+std::to_string(frame.sequence)+"-"+std::to_string(frame.generation)+"-"+std::to_string(i);
            OwnedReadback::publishPNG(readbackDirectory,stem+"-rgba.png",o.bufferWidth,o.bufferHeight,r.rgba);
            OwnedReadback::publishPNG(readbackDirectory,stem+"-native-rgba.png",o.bufferWidth,o.bufferHeight,r.nativeRGBA);
            QJsonArray prefix,controls;for(size_t n=0;n<r.prefix;++n)prefix.append(membersJson({frame.members.at(n)}).at(0));
            for(int index:r.controls){QJsonArray color;for(auto channel:OwnedCausal::controls().at(index))color.append(int(channel));controls.append(QJsonObject{{"index",index},{"premultipliedRGBA",color}});}
            QJsonObject observation{{"event","ownedCausalReadback"},{"kind",qs(r.kind)},{"token",qs(frame.token)},{"digest",qs(frame.digest)},{"stableId",qs(frame.identity.stable)},{"pid",double(frame.identity.pid)},{"sequence",QString::number(frame.sequence)},{"output",qs(frame.output)},{"generation",double(frame.generation)},{"progress",frame.progress},{"members",membersJson(frame.members)},{"prefixCount",int(r.prefix)},{"prefixMembers",prefix},{"controls",controls},{"bufferWidth",frame.bufferWidth},{"bufferHeight",frame.bufferHeight},{"logicalOutput",rectangleJson(Rect{double(o.x),double(o.y),double(o.width),double(o.height)})},{"rgbaFilename",qs(stem+"-rgba.png")},{"nativeRGBAFilename",qs(stem+"-native-rgba.png")},{"rgbaSHA256",qs(byteDigest(r.rgba))},{"nativeRGBASHA256",qs(byteDigest(r.nativeRGBA))},{"nativeBytesSHA256",qs(r.nativeBytesDigest)},{"nativeFormat",double(r.nativeFormat)},{"nativeType",double(r.nativeType)},{"allReadFormatBytesEqual",r.rgba==r.nativeRGBA},{"readError",0},{"encoding","premultiplied-RGBA8-top-left"},{"nativeAuthority",false},{"presentationProof",false}};
            if(quantizedOver){observation["readFramebuffer"]=r.readFramebuffer;observation["prefixTexture"]=int(r.prefixTexture);observation["observedPrefixCount"]=int(r.observedPrefixCount);observation["readTargetCopy"]=r.readTargetCopy;}
            emitEvent(observation);
        }
    }
    void diagnosticReadback(Output& o,const Frame& frame){
        if(readbackDirectory<0)return;
        const auto sample=frame.token+":"+std::to_string(frame.generation)+":"+std::to_string(frame.progress);
        if(!readbackSamples.insert(sample).second)return;
        const uint64_t count=uint64_t(o.bufferWidth)*o.bufferHeight*4;
        if(o.bufferWidth<=0||o.bufferHeight<=0||count>256*1024*1024)throw std::runtime_error("readback extent exceeded");
        QJsonObject attributes;bool valid=true;
        for(auto entry:{std::pair{"red",EGL_RED_SIZE},std::pair{"green",EGL_GREEN_SIZE},std::pair{"blue",EGL_BLUE_SIZE},std::pair{"alpha",EGL_ALPHA_SIZE},std::pair{"buffer",EGL_BUFFER_SIZE},std::pair{"samples",EGL_SAMPLES},std::pair{"sampleBuffers",EGL_SAMPLE_BUFFERS},std::pair{"configId",EGL_CONFIG_ID},std::pair{"colorBufferType",EGL_COLOR_BUFFER_TYPE},std::pair{"nativeVisualId",EGL_NATIVE_VISUAL_ID}}){EGLint value=0;valid=eglGetConfigAttrib(eglDisplay,config,entry.second,&value)&&valid;attributes[entry.first]=value;}
        QJsonObject surface;for(auto entry:{std::pair{"width",EGL_WIDTH},std::pair{"height",EGL_HEIGHT}}){EGLint value=0;valid=eglQuerySurface(eglDisplay,o.egl,entry.second,&value)&&valid;surface[entry.first]=value;}
        QJsonObject glBits;for(auto entry:{std::pair{"red",GL_RED_BITS},std::pair{"green",GL_GREEN_BITS},std::pair{"blue",GL_BLUE_BITS},std::pair{"alpha",GL_ALPHA_BITS},std::pair{"readFormat",GL_IMPLEMENTATION_COLOR_READ_FORMAT},std::pair{"readType",GL_IMPLEMENTATION_COLOR_READ_TYPE},std::pair{"sampleBuffers",GL_SAMPLE_BUFFERS},std::pair{"samples",GL_SAMPLES},std::pair{"framebuffer",GL_FRAMEBUFFER_BINDING}}){GLint value=0;glGetIntegerv(entry.second,&value);glBits[entry.first]=value;}
        const auto eglError=eglGetError();const auto inspectionError=glGetError();
        if(!valid||eglError!=EGL_SUCCESS||inspectionError!=GL_NO_ERROR)throw std::runtime_error("readback buffer inspection failed");
        std::vector<unsigned char> pixels(count);GLint pack=0;glGetIntegerv(GL_PACK_ALIGNMENT,&pack);glPixelStorei(GL_PACK_ALIGNMENT,1);
        glReadPixels(0,0,o.bufferWidth,o.bufferHeight,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());const auto readError=glGetError();glPixelStorei(GL_PACK_ALIGNMENT,pack);const auto restoreError=glGetError();
        if(readError!=GL_NO_ERROR||restoreError!=GL_NO_ERROR)throw std::runtime_error("owned framebuffer readback failed");
        const auto topLeft=OwnedReadback::topLeftRows(pixels,o.bufferWidth,o.bufferHeight);
        const auto filename="owned-"+std::to_string(frame.sequence)+"-"+std::to_string(frame.generation)+".png";
        OwnedReadback::publishPNG(readbackDirectory,filename,o.bufferWidth,o.bufferHeight,topLeft);
        emitEvent({{"event","ownedFramebufferReadback"},{"token",qs(frame.token)},{"digest",qs(frame.digest)},{"stableId",qs(frame.identity.stable)},{"pid",double(frame.identity.pid)},{"sequence",QString::number(frame.sequence)},{"output",qs(frame.output)},{"generation",double(frame.generation)},{"progress",frame.progress},{"members",membersJson(frame.members)},{"bufferWidth",frame.bufferWidth},{"bufferHeight",frame.bufferHeight},{"filename",qs(filename)},{"rawSHA256",QString::fromLatin1(QCryptographicHash::hash(QByteArray(reinterpret_cast<const char*>(topLeft.data()),topLeft.size()),QCryptographicHash::Sha256).toHex())},{"encoding","premultiplied-RGBA8-top-left"},{"eglConfig",attributes},{"eglSurface",surface},{"glBuffer",glBits},{"readError",double(readError)},{"nativeAuthority",false},{"presentationProof",false}});
    }
    void draw(Output& o,double p,uint64_t batchNs){
        if(!needsDraw(o))return;
        const bool active=ledger.isActive()&&std::find(required.begin(),required.end(),&o)!=required.end();
        const auto drawStartedNs=monotonicNs();
        if(!makeCurrent(o)){cancel("eglMakeCurrent failed");return;}
        if(glIsEnabled(GL_DITHER)==GL_TRUE){cancel("owned raster dithering state changed");return;}
        glViewport(0,0,o.bufferWidth,o.bufferHeight);glDisable(GL_SCISSOR_TEST);glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
        auto members=active?ledger.sceneRectangles(o.name,p):std::vector<MemberFrame>{};
        const auto observedToken=ledger.token();const auto observedGeneration=o.generation;
        std::vector<CausalObservation> causalRecords;bool observe=false;
        if(active&&causalFixture){
            OwnedCausal::boundedSampleBytes(o.bufferWidth,o.bufferHeight,members.size());
            const auto sample=ledger.token()+":"+std::to_string(o.generation)+":"+std::to_string(p);
            if(!causalSamples.contains(sample)){
                if(causalSamples.size()>=128)throw std::runtime_error("causal held sample count exceeded");
                causalSamples.insert(sample);observe=true;
            }
        }
        if(active){
            if(quantizedOver){o.prefixConfigurations={};beginPrefix(o);}
            if(members.size()!=familyTextures.size()){cancel("complete family textures unavailable");return;}
            if(quantizedOver)glDisable(GL_BLEND);else glEnable(GL_BLEND);glBlendFunc(GL_ONE,GL_ONE_MINUS_SRC_ALPHA);glUseProgram(shader);glActiveTexture(GL_TEXTURE0);glUniform1i(glGetUniformLocation(shader,"atlas"),0);
            glEnableVertexAttribArray(positionLocation);if(uvLocation>=0)glEnableVertexAttribArray(uvLocation);
            if(observe)observeControls(o,causalRecords);
            for(size_t i=0;i<members.size();++i){const auto& rect=members[i].rectangle;
                if(quantizedOver){const auto found=samplerTextures.find(familyTextures[i]);if(found==samplerTextures.end()||found->second.controlIndex!=-1||found->second.digest!=members[i].source.digest)throw std::runtime_error("ordered quantized source digest differs from immutable member");}
                drawLayer(o,rect,familyTextures[i],i+1);
                if(observe){if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("real prefix draw failed");causalRecords.push_back(observeCausal(o,"member-prefix",i+1));}
            }
            if(quantizedOver){if(o.prefixPassCount!=members.size())throw std::runtime_error("quantized complete family prefix missing");o.prefixFinalCopy=copyPrefix(o,o.prefixTextures[o.prefixRead],0);}
            glDisableVertexAttribArray(positionLocation);if(uvLocation>=0)glDisableVertexAttribArray(uvLocation);
        }
        if(glGetError()!=GL_NO_ERROR){cancel("GPU draw failed");return;}
        const auto drawDoneNs=monotonicNs();
        o.callback=wl_surface_frame(o.surface);o.frameReady=false;
        static const wl_callback_listener frameListener={[](void* p,wl_callback* callback,uint32_t){auto& o=*static_cast<Output*>(p);wl_callback_destroy(callback);o.callback=nullptr;o.frameReady=true;o.lastFrameCallbackNs=monotonicNs();}};
        wl_callback_add_listener(o.callback,&frameListener,&o);
        uint64_t number=0;std::optional<Frame> submittedScene;
        if(active){
            auto frame=ledger.prepareFamily(o.name,o.generation,p,monotonicNs(),o.bufferWidth,o.bufferHeight);if(!frame){cancel("frame ledger rejected submission");return;}
            if(!causalRecords.empty()&&(frame->token!=observedToken||frame->generation!=observedGeneration||frame->members!=members||frame->bufferWidth!=o.bufferWidth||frame->bufferHeight!=o.bufferHeight))throw std::runtime_error("causal observed draw differs from named immutable frame");
            number=frame->sequence;submittedScene=*frame;
            if(quantizedOver){if(frame->token!=observedToken||frame->generation!=observedGeneration||frame->members!=members)throw std::runtime_error("quantized pass/frame immutable binding disagreement");emitEvent({{"event","quantizedOverFrameConfigured"},{"policy",OwnedOver::policy},{"logicalOutput",rectangleJson(Rect{double(o.x),double(o.y),double(o.width),double(o.height)})},{"token",qs(frame->token)},{"sequence",QString::number(frame->sequence)},{"output",qs(frame->output)},{"generation",double(frame->generation)},{"bufferWidth",frame->bufferWidth},{"bufferHeight",frame->bufferHeight},{"members",membersJson(frame->members)},{"passes",o.prefixConfigurations},{"finalCopy",o.prefixFinalCopy},{"nativeAuthority",false},{"pixelProof",false}});}
            publishCausal(o,*frame,causalRecords);diagnosticReadback(o,*frame);auto f=std::make_unique<Feedback>(Feedback{this,&o,o.generation,*frame,wp_presentation_feedback(presentation,o.surface),false,false});
            static const wp_presentation_feedback_listener feedbackListener={
                [](void* p,struct wp_presentation_feedback*,wl_output* output){auto& f=*static_cast<Feedback*>(p);if(output==f.output->proxy)f.sync=true;else f.mismatch=true;},
                [](void* p,struct wp_presentation_feedback*,uint32_t hi,uint32_t lo,uint32_t ns,uint32_t,uint32_t seqhi,uint32_t seqlo,uint32_t){auto& f=*static_cast<Feedback*>(p);f.owner->feedbackDone(f,((uint64_t(hi)<<32)|lo)*1000000000+ns,(uint64_t(seqhi)<<32)|seqlo);},
                [](void* p,struct wp_presentation_feedback*){auto& f=*static_cast<Feedback*>(p);f.owner->ledger.discarded(f.frame.sequence);f.owner->cancel("own commit feedback discarded");}
            };
            wp_presentation_feedback_add_listener(f->proxy,&feedbackListener,f.get());feedbacks[number]=std::move(f);o.outstanding=number;
        }
        const auto swapStartedNs=monotonicNs();swapping=true;const bool success=eglSwapBuffers(eglDisplay,o.egl)==EGL_TRUE;swapping=false;const auto swapReturnedNs=monotonicNs();
        if(!deferredCancel.empty()){auto reason=deferredCancel;deferredCancel.clear();cancel(reason);return;}
        if(active){
            const auto accepted=ledger.swapReturned(number,success);
            // A deferred feedback callback becomes actual accepted evidence only
            // now, tied to its original immutable submitted scene.
            if(accepted==Result::RecordedCurrent||accepted==Result::RecordedOld){const auto& actual=ledger.records().back();emitPresented(actual,"presented",true);if(accepted==Result::RecordedCurrent&&actual.frame.endpoint)o.endpointPresented=true;}
            emitEvent({{"event","swap"},{"success",success},{"token",qs(submittedScene->token)},{"digest",qs(submittedScene->digest)},{"stableId",qs(submittedScene->identity.stable)},{"pid",double(submittedScene->identity.pid)},{"output",qs(submittedScene->output)},{"generation",double(submittedScene->generation)},{"sequence",QString::number(number)},{"rectangle",rectangleJson(submittedScene->rectangle)},{"progress",submittedScene->progress},{"uploadCount",int(uploadCount)},{"members",membersJson(submittedScene->members)},{"bufferWidth",submittedScene->bufferWidth},{"bufferHeight",submittedScene->bufferHeight},{"batchNs",QString::number(batchNs)},{"drawStartedNs",QString::number(drawStartedNs)},{"drawDoneNs",QString::number(drawDoneNs)},{"swapStartedNs",QString::number(swapStartedNs)},{"swapReturnedNs",QString::number(swapReturnedNs)},{"lastFrameCallbackNs",QString::number(o.lastFrameCallbackNs)}});
        }
        if(!success){cancel("eglSwapBuffers failed; authority retired");return;}
        if(!active){o.clearCommitted=true;++transparentCommitCount;}
        notifyAuthority();
    }
    void applyRetarget(){
        if(waitingRetarget.isEmpty()||ledger.hasPending())return;
        auto j=waitingRetarget;waitingRetarget={};auto token=j["token"].toString().toStdString();
        if(!ledger.retargetFamily(familyIdentities,token,j["operation"].toString().toStdString())){cancel("presented handover unavailable");return;}
        for(auto* o:required){o->from=ledger.presentedOrigins().at(o->name).frame.rectangle;o->endpointPresented=false;}
        durationNs=j["durationMs"].toInt()*1000000ULL;startedNs=monotonicNs();running=true;readySent=false;endpointSent=false;routeAcceptedNs=monotonicNs();endpointHeldNs=0;
        QJsonArray origins;for(auto* o:required){const auto& f=ledger.presentedOrigins().at(o->name);origins.append(QJsonObject{{"output",qs(o->name)},{"generation",double(o->generation)},{"sequence",QString::number(f.frame.sequence)},{"timestampNs",QString::number(f.timestampNs)},{"rectangle",rectangleJson(f.frame.rectangle)},{"members",membersJson(f.frame.members)}});}
        emitEvent({{"event","retargeted"},{"token",qs(token)},{"origins",origins},{"startNs",QString::number(startedNs)},{"sourceReused",true},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()},{"nativeAuthority",false},{"uploadCount",int(uploadCount)}});
        if(j["promoted"].toBool()){ledger.promoteFamily(familyIdentities,token);notifyAuthority();}
    }
    void command(const QJsonObject& j){
        auto kind=j["command"].toString();
        if(kind=="state"){
            QJsonArray records;for(const auto& p:ledger.records()){const auto& f=p.frame;records.append(QJsonObject{{"token",qs(f.token)},{"stableId",qs(f.identity.stable)},{"pid",double(f.identity.pid)},{"digest",qs(f.digest)},{"output",qs(f.output)},{"generation",double(f.generation)},{"sequence",QString::number(f.sequence)},{"submittedNs",QString::number(f.submittedNs)},{"timestampNs",QString::number(p.timestampNs)},{"feedbackDeliveredNs",QString::number(monotonicNs())},{"outputSequence",QString::number(p.compositorSequence)},{"rectangle",rectangleJson(f.rectangle)},{"progress",f.progress},{"endpoint",f.endpoint},{"members",membersJson(f.members)},{"bufferWidth",f.bufferWidth},{"bufferHeight",f.bufferHeight}});}
            QJsonArray actualOutputs;for(const auto& o:outputs)if(o->alive)actualOutputs.append(QJsonObject{{"name",qs(o->name)},{"generation",double(o->generation)},{"x",o->x},{"y",o->y},{"width",o->width},{"height",o->height},{"bufferWidth",o->bufferWidth},{"bufferHeight",o->bufferHeight},{"scale",o->preferredScale/120.0},{"transform",o->transform},{"configured",o->configured}});
            emitEvent({{"event","state"},{"observationId",j["observationId"]},{"transparentCommitCount",int(transparentCommitCount)},{"active",ledger.isActive()},{"token",qs(ledger.token())},{"nativeReady",ledger.nativeReady()},{"nativeEndpoint",ledger.nativeEndpoint()},{"pending",int(ledger.pendingCount())},{"uploadCount",int(uploadCount)},{"records",records},{"outputs",actualOutputs},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()}});return;
        }
        if(kind=="prepareOutputs"){if(ledger.isActive())throw std::invalid_argument("route already active");surfacesEnabled=true;announced=false;return;}
        if(kind=="stop"){cancel("renderer shutdown");quit=true;return;}
        if(kind=="cancel"){const auto latest=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();if(j["token"].toString().toStdString()==latest&&identities(j)==familyIdentities)cancel("service cancelled exact latest token");else emitEvent({{"event","cancelRejected"},{"token",j["token"]},{"nativeAuthority",false}});return;}
        if(kind=="seed"){
            if(ledger.isActive())throw std::invalid_argument("active scene must be cancelled before new snapshots");
            auto token=j["token"].toString().toStdString();if(!validToken(token))throw std::invalid_argument("invalid whole scene token");
            auto op=j["operation"].toString();if(op!="minimize"&&op!="restore")throw std::invalid_argument("invalid operation");
            int duration=j["durationMs"].toInt();if(duration<1||duration>4000)throw std::invalid_argument("invalid duration");
            auto items=j["members"].toArray();if(items.empty()||items.size()>64)throw std::invalid_argument("complete ordered family sources required");
            std::vector<Source> sources;std::vector<QJsonObject> inputs;std::vector<Identity> ids;std::set<std::string> seen;uint64_t rgbaBytes=0;QJsonArray digestRecords;
            for(const auto& value:items){auto m=value.toObject();auto id=identity(m);auto hash=m["digest"].toString().toStdString();
                if(!validDigest(hash)||!seen.insert(id.stable).second)throw std::invalid_argument("invalid digest or duplicate family identity");
                auto native=rectangle(m["nativeRect"]),atlas=rectangle(m["atlasRect"]),icon=rectangle(m["iconRect"]);
                auto inset=m["insets"].toObject();double left=inset["left"].toDouble(NAN),top=inset["top"].toDouble(NAN),right=inset["right"].toDouble(NAN),bottom=inset["bottom"].toDouble(NAN);
                for(auto v:{left,top,right,bottom})if(!std::isfinite(v)||v<0)throw std::invalid_argument("invalid captured insets");
                if(std::abs(atlas.x+left-native.x)>1e-6||std::abs(atlas.y+top-native.y)>1e-6||std::abs(atlas.width-left-right-native.width)>1e-6||std::abs(atlas.height-top-bottom-native.height)>1e-6)throw std::invalid_argument("captured atlas/native geometry disagrees");
                auto pixels=m["pixels"].toArray();int pw=pixels.size()==2?pixels[0].toInt():0,ph=pixels.size()==2?pixels[1].toInt():0;double scale=m["captureScale"].toDouble();
                if(!std::isfinite(scale)||scale<=0||scale>8||pw<=0||ph<=0||pw>8192||ph>8192||std::abs(atlas.width*scale-pw)>1e-6||std::abs(atlas.height*scale-ph)>1e-6)throw std::invalid_argument("invalid captured pixel scale/extent");
                rgbaBytes+=uint64_t(pw)*ph*4;if(rgbaBytes>268435456)throw std::invalid_argument("family decoded texture memory exceeds bound");
                sources.push_back({id,hash,native,atlas,icon});ids.push_back(id);inputs.push_back(m);
                digestRecords.append(QJsonObject{{"stableId",qs(id.stable)},{"pid",double(id.pid)},{"digest",qs(hash)},{"nativeRect",rectangleJson(native)},{"atlasRect",rectangleJson(atlas)},{"iconRect",rectangleJson(icon)}});
            }
            auto hash=QCryptographicHash::hash(QJsonDocument(digestRecords).toJson(QJsonDocument::Compact),QCryptographicHash::Sha256).toHex().toStdString();
            std::map<std::string,uint64_t> generations;std::vector<Output*> selected;
            for(auto value:j["outputs"].toArray()){auto o=value.toObject();auto name=o["name"].toString().toStdString();double number=o["generation"].toDouble();if(!std::isfinite(number)||number<1||number>9007199254740991.0||std::floor(number)!=number)throw std::invalid_argument("invalid output generation number");uint64_t gen=number;
                auto match=std::find_if(outputs.begin(),outputs.end(),[&](auto& p){return p->alive&&p->configured&&p->preferredScale&&p->name==name&&p->generation==gen;});
                if(match==outputs.end()||generations.contains(name))throw std::invalid_argument("stale/duplicate output generation");selected.push_back(match->get());generations[name]=gen;
            }
            if(selected.empty())throw std::invalid_argument("no ready required outputs");
            if(!makeCurrent(*selected.front()))throw std::runtime_error("snapshot upload context unavailable");
            std::vector<GLuint> uploaded;try{for(const auto& m:inputs){auto pixels=m["pixels"].toArray();uploaded.push_back(upload(m["path"].toString().toStdString(),m["digest"].toString().toStdString(),pixels[0].toInt(),pixels[1].toInt()));}}catch(...){for(auto t:uploaded){samplerTextures.erase(t);glDeleteTextures(1,&t);}throw;}
            for(auto t:familyTextures){samplerTextures.erase(t);glDeleteTextures(1,&t);}familyTextures=std::move(uploaded);familyIdentities=std::move(ids);
            ledger.configure(generations);ledger.seedFamily(sources,token,hash,op.toStdString());
            routeIdentity=familyIdentities.front();digest=hash;operation=op.toStdString();durationNs=duration*1000000ULL;required=selected;
            for(auto* o:required){o->from=bounds(ledger.sceneRectangles(o->name,0));o->endpointPresented=false;}
            routeAcceptedNs=monotonicNs();endpointHeldNs=0;running=false;readySent=false;endpointSent=false;
            emitEvent({{"event","seeded"},{"token",qs(token)},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()},{"nativeAuthority",false}});return;
        }
        if(kind=="retarget"){
            auto token=j["token"].toString().toStdString();int duration=j["durationMs"].toInt();auto operation=j["operation"].toString();if(operation!="minimize"&&operation!="restore")throw std::invalid_argument("retarget must use retained captured endpoint");
            auto prior=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();
            if(!ledger.isActive()||identities(j)!=familyIdentities||!validToken(token)||token.substr(0,12)!=prior.substr(0,12)||std::stoull(token.substr(13))<=std::stoull(prior.substr(13))||duration<1||duration>4000)throw std::invalid_argument("invalid visual retarget");
            waitingRetarget=j;waitingRetarget["promoted"]=false;ledger.suspendAuthority();readySent=false;endpointSent=false;emitEvent({{"event","retargetAccepted"},{"token",qs(token)},{"receivedNs",QString::number(monotonicNs())},{"identities",identityJson(familyIdentities)},{"sourceDigests",sourceDigests()},{"nativeAuthority",false}});applyRetarget();return;
        }
        if(kind=="sample"){
            if(!rasterFixture||!ledger.isActive()||identities(j)!=familyIdentities||j["token"].toString().toStdString()!=ledger.token())throw std::invalid_argument("held pixel sample unavailable outside exact diagnostic scene");
            double p=j["progress"].toDouble(NAN);if(!std::isfinite(p)||p<0||p>1)throw std::invalid_argument("invalid sample progress");
            ledger.suspendAuthority();running=false;sampleProgress=p;for(auto* o:required)o->endpointPresented=false;
            emitEvent({{"event","sampleAccepted"},{"token",qs(ledger.token())},{"progress",p},{"nativeAuthority",false}});return;
        }
        if(kind=="validate"){
            if(rasterFixture)throw std::invalid_argument("raster diagnostic has no validation authority");
            if(!waitingRetarget.isEmpty()){if(identities(j)!=familyIdentities||j["token"]!=waitingRetarget["token"])throw std::invalid_argument("validation superseded by newer accepted visual intent");waitingRetarget["promoted"]=true;return;}
            if(!ledger.promoteFamily(identities(j),j["token"].toString().toStdString()))throw std::invalid_argument("validation does not match current visual token");notifyAuthority();return;
        }
        if(kind=="start"){
            if(rasterFixture)throw std::invalid_argument("raster diagnostic has no native start authority");
            if(identities(j)!=familyIdentities||j["token"].toString().toStdString()!=ledger.token()||!ledger.nativeReady())throw std::invalid_argument("start lacks exact presented/promoted readiness");
            startedNs=monotonicNs();running=true;return;
        }
        throw std::invalid_argument("unknown command");
    }
    void publishOutputs(){
        if(announced)return;QJsonArray array;std::set<std::string> names;
        for(auto& o:outputs)if(o->alive){if(!o->configured||!o->preferredScale||o->name.empty())return;if(!names.insert(o->name).second)throw std::runtime_error("duplicate actual output name");array.append(QJsonObject{{"name",qs(o->name)},{"generation",double(o->generation)},{"x",o->x},{"y",o->y},{"width",o->width},{"height",o->height},{"scale",o->preferredScale/120.0},{"transform",o->transform},{"pixelWidth",o->pixelWidth},{"pixelHeight",o->pixelHeight},{"refreshMilliHz",o->refresh}});}
        if(!array.isEmpty()){announced=true;emitEvent({{"event","outputs"},{"outputs",array},{"clockId",int(clockId)},{"nativeAuthority",false}});}
    }
    static void addGlobal(void* p,wl_registry* registry,uint32_t name,const char* interface,uint32_t version){
        auto& r=*static_cast<Renderer*>(p);std::string i=interface;
        if(i=="wl_compositor")r.compositor=static_cast<wl_compositor*>(wl_registry_bind(registry,name,&wl_compositor_interface,std::min(version,4u)));
        else if(i=="zwlr_layer_shell_v1")r.shell=static_cast<zwlr_layer_shell_v1*>(wl_registry_bind(registry,name,&zwlr_layer_shell_v1_interface,std::min(version,4u)));
        else if(i=="wp_presentation"){
            r.presentation=static_cast<wp_presentation*>(wl_registry_bind(registry,name,&wp_presentation_interface,1));
            static const wp_presentation_listener listener={[](void* p,wp_presentation*,uint32_t id){static_cast<Renderer*>(p)->clockId=id;}};wp_presentation_add_listener(r.presentation,&listener,&r);
        }
        else if(i=="wp_viewporter")r.viewporter=static_cast<wp_viewporter*>(wl_registry_bind(registry,name,&wp_viewporter_interface,1));
        else if(i=="zxdg_output_manager_v1")r.outputManager=static_cast<zxdg_output_manager_v1*>(wl_registry_bind(registry,name,&zxdg_output_manager_v1_interface,std::min(version,3u)));
        else if(i=="wp_fractional_scale_manager_v1")r.fractionalManager=static_cast<wp_fractional_scale_manager_v1*>(wl_registry_bind(registry,name,&wp_fractional_scale_manager_v1_interface,1));
        else if(i=="wl_output"){
            if(version<4)throw std::runtime_error("wl_output name capability unavailable");
            auto o=std::make_unique<Output>();o->owner=&r;o->registry=name;o->generation=++r.generationSerial;o->proxy=static_cast<wl_output*>(wl_registry_bind(registry,name,&wl_output_interface,4));
            static const wl_output_listener listener={
                [](void* p,wl_output*,int32_t,int32_t,int32_t,int32_t,int32_t,const char*,const char*,int32_t transform){auto& o=*static_cast<Output*>(p);if(o.transform!=transform){o.transform=transform;o.owner->changed(o);}},
                [](void* p,wl_output*,uint32_t flags,int32_t w,int32_t h,int32_t refresh){auto& o=*static_cast<Output*>(p);if((flags&WL_OUTPUT_MODE_CURRENT)&&(o.pixelWidth!=w||o.pixelHeight!=h||o.refresh!=refresh)){o.pixelWidth=w;o.pixelHeight=h;o.refresh=refresh;o.owner->changed(o);}},[](void*,wl_output*){},
                [](void* p,wl_output*,int32_t scale){auto& o=*static_cast<Output*>(p);if(o.integerScale!=scale){o.integerScale=scale;o.owner->changed(o);}},
                [](void* p,wl_output*,const char* name){auto& o=*static_cast<Output*>(p);if(o.name!=name){o.name=name;o.owner->changed(o);}},[](void*,wl_output*,const char*){}
            };wl_output_add_listener(o->proxy,&listener,o.get());r.outputs.push_back(std::move(o));
        }
    }
    static void removeGlobal(void* p,wl_registry*,uint32_t name){auto& r=*static_cast<Renderer*>(p);for(auto& o:r.outputs)if(o->registry==name&&o->alive){r.ledger.outputRemoved(o->name,o->generation);r.cancel("output removed");o->alive=false;if(r.swapping)return;r.closeOutput(*o);if(o->logical){zxdg_output_v1_destroy(o->logical);o->logical=nullptr;}wl_output_release(o->proxy);o->proxy=nullptr;}}
    void attachLogicalOutputs(){
        for(auto& o:outputs)if(o->alive&&!o->logical){
            o->logical=zxdg_output_manager_v1_get_xdg_output(outputManager,o->proxy);
            static const zxdg_output_v1_listener listener={
                [](void* p,zxdg_output_v1*,int32_t x,int32_t y){auto& o=*static_cast<Output*>(p);if(o.x!=x||o.y!=y){o.x=x;o.y=y;o.owner->changed(o);}},
                [](void* p,zxdg_output_v1*,int32_t w,int32_t h){auto& o=*static_cast<Output*>(p);if(o.width!=w||o.height!=h){o.width=w;o.height=h;o.owner->changed(o);}},
                [](void*,zxdg_output_v1*){},[](void*,zxdg_output_v1*,const char*){},[](void*,zxdg_output_v1*,const char*){}
            };zxdg_output_v1_add_listener(o->logical,&listener,o.get());
        }
    }
public:
    explicit Renderer(bool diagnostic=false,const std::string& readback="",bool causal=false,bool manual=false,bool over=false):quantizedOver(over),manualSampling(manual||over),causalFixture(causal),rasterFixture(diagnostic){
        OwnedSampling::requireDiagnostic(manual||over,diagnostic,causal,!readback.empty());OwnedOver::requireDiagnostic(over,diagnostic,causal,!readback.empty());
        if(causal&&(!diagnostic||readback.empty()))throw std::invalid_argument("causal observations require owned raster readback directory");
        if(!readback.empty()){
            if(!diagnostic)throw std::invalid_argument("readback only available in raster diagnostic mode");
            struct stat before{};if(lstat(readback.c_str(),&before)||!S_ISDIR(before.st_mode)||before.st_uid!=getuid()||(before.st_mode&0777)!=0700)throw std::invalid_argument("readback directory must be private existing owned non-symlink directory");
            readbackDirectory=open(readback.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat after{};
            if(readbackDirectory<0||fstat(readbackDirectory,&after)||before.st_dev!=after.st_dev||before.st_ino!=after.st_ino){if(readbackDirectory>=0)close(readbackDirectory);readbackDirectory=-1;throw std::invalid_argument("readback directory changed");}
        }
    }
    ~Renderer(){
        if(readbackDirectory>=0)close(readbackDirectory);
        for(auto& o:outputs)closeOutput(*o);
        if(eglDisplay!=EGL_NO_DISPLAY){eglMakeCurrent(eglDisplay,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);if(context!=EGL_NO_CONTEXT)eglDestroyContext(eglDisplay,context);eglTerminate(eglDisplay);}
        for(auto& o:outputs){if(o->logical)zxdg_output_v1_destroy(o->logical);if(o->proxy)wl_output_release(o->proxy);}
        if(fractionalManager)wp_fractional_scale_manager_v1_destroy(fractionalManager);if(outputManager)zxdg_output_manager_v1_destroy(outputManager);if(viewporter)wp_viewporter_destroy(viewporter);if(presentation)wp_presentation_destroy(presentation);if(shell)zwlr_layer_shell_v1_destroy(shell);if(compositor)wl_compositor_destroy(compositor);if(registry)wl_registry_destroy(registry);if(display)wl_display_disconnect(display);
    }
    void run(){
        display=wl_display_connect(nullptr);if(!display)throw std::runtime_error("owned Wayland connection failed");registry=wl_display_get_registry(display);
        static const wl_registry_listener listener={addGlobal,removeGlobal};wl_registry_add_listener(registry,&listener,this);
        if(wl_display_roundtrip(display)<0||!compositor||!shell||!presentation||!viewporter||!outputManager||!fractionalManager)throw std::runtime_error("required output/presentation/layer protocols unavailable");
        attachLogicalOutputs();if(wl_display_roundtrip(display)<0||clockId!=CLOCK_MONOTONIC)throw std::runtime_error("logical outputs/presentation clock unavailable");initializeEGL();
        fcntl(STDIN_FILENO,F_SETFL,fcntl(STDIN_FILENO,F_GETFL)|O_NONBLOCK);
        while(!quit){
            if(overCleanupFailed)throw std::runtime_error("owned prefix resource cleanup failed");
            if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned display dispatch failed");attachLogicalOutputs();
            if(surfacesEnabled)for(auto& o:outputs)createSurface(*o);applyRetarget();
            const auto batchNow=monotonicNs();const double batchProgress=rasterFixture?sampleProgress:running?std::clamp(double(batchNow-startedNs)/durationNs,0.0,1.0):0;
            for(auto& o:outputs){if(!waitingRetarget.isEmpty())break;draw(*o,batchProgress,batchNow);}publishOutputs();
            if(ledger.timedOut(monotonicNs()))cancel("presentation deadline expired");
            const auto now=monotonicNs();
            if(!rasterFixture&&ledger.isActive()&&((!running&&now-routeAcceptedNs>2000000000ULL)||(endpointHeldNs&&now-endpointHeldNs>2000000000ULL)))cancel("controller handshake deadline expired");
            while(wl_display_prepare_read(display)!=0)if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned pending dispatch failed");
            if(wl_display_flush(display)<0&&errno!=EAGAIN)throw std::runtime_error("owned display flush failed");
            pollfd fds[]={{wl_display_get_fd(display),POLLIN,0},{STDIN_FILENO,POLLIN,0}};int count=poll(fds,2,ledger.isActive()?20:1000);if(count<0&&errno!=EINTR)throw std::runtime_error("owned display poll failed");
            if(fds[0].revents&POLLIN){if(wl_display_read_events(display)<0)throw std::runtime_error("owned display read failed");}else wl_display_cancel_read(display);
            if(fds[0].revents&(POLLHUP|POLLERR))throw std::runtime_error("owned display disconnected");
            if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned display callback failed");
            if(fds[1].revents&(POLLIN|POLLHUP)){
                char buffer[8192];ssize_t n=read(STDIN_FILENO,buffer,sizeof(buffer));if(n==0){cancel("controller pipe closed");quit=true;}else if(n>0)input.append(buffer,n);
                if(input.size()>1048576)throw std::runtime_error("command bound exceeded");
                int index=0;while((index=input.indexOf('\n'))>=0){auto line=input.left(index);input.remove(0,index+1);try{QJsonParseError error;auto doc=QJsonDocument::fromJson(line,&error);if(error.error!=QJsonParseError::NoError||!doc.isObject())throw std::invalid_argument("invalid JSON command");command(doc.object());}catch(const std::exception& e){emitEvent({{"event","rejected"},{"reason",e.what()},{"nativeAuthority",false}});}}
            }
        }
        if(quantizedOver){for(auto& o:outputs)closeOutput(*o);if(overCleanupFailed)throw std::runtime_error("prefix teardown did not finish normally");}
    }
};
#ifndef OWNED_EGL_OFFLINE_TEST
int main(int argc,char** argv){
    if(argc==2&&std::string(argv[1])=="--describe"){emitEvent({{"status","staged prototype"},{"protocols",QJsonArray{"layer-shell","presentation","viewporter","xdg-output","fractional-scale"}},{"namespace","hoskinson-window-motion"},{"nativeTested",false},{"serviceIntegrated",false}});return 0;}
    try{bool diagnostic=false,causal=false,manual=false,over=false;std::string readback;
        if(argc==2&&std::string(argv[1])=="--raster-fixture")diagnostic=true;
        else if(argc==4&&std::string(argv[1])=="--raster-fixture"&&std::string(argv[2])=="--readback-dir"){diagnostic=true;readback=argv[3];}
        else if(argc==4&&std::string(argv[1])=="--raster-fixture"&&std::string(argv[2])=="--causal-readback-dir"){diagnostic=true;causal=true;readback=argv[3];}
        else if(argc==5&&std::string(argv[1])=="--raster-fixture"&&std::string(argv[2])=="--causal-readback-dir"&&std::string(argv[4])=="--manual-bilinear-experiment"){diagnostic=true;causal=true;manual=true;readback=argv[3];}
        else if(argc==5&&std::string(argv[1])=="--raster-fixture"&&std::string(argv[2])=="--causal-readback-dir"&&std::string(argv[4])=="--quantized-over-experiment"){diagnostic=true;causal=true;over=true;readback=argv[3];}
        else if(argc!=1)throw std::invalid_argument("unknown producer option");
        Renderer r(diagnostic,readback,causal,manual,over);r.run();return 0;}catch(const std::exception& e){emitEvent({{"event","fatal"},{"reason",e.what()},{"nativeAuthority",false}});return 1;}
}

#endif
