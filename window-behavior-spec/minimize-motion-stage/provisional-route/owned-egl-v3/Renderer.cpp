// Standalone staged producer. Own Wayland connection/context, no Qt QPA.
#include "CommitLedger.hpp"
#include "BackendPolicy.hpp"
#include "LibraryMaterial.hpp"
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

using namespace OwnedRoute;
static uint64_t monotonicNs(){timespec t{};clock_gettime(CLOCK_MONOTONIC,&t);return uint64_t(t.tv_sec)*1000000000+t.tv_nsec;}
static QString qs(const std::string& s){return QString::fromStdString(s);}
static void emitEvent(const QJsonObject& value){std::cout<<QJsonDocument(value).toJson(QJsonDocument::Compact).constData()<<'\n'<<std::flush;}
static QJsonObject rectangleJson(const Rect& r){return {{"x",r.x},{"y",r.y},{"width",r.width},{"height",r.height}};}
static Rect rectangle(const QJsonValue& v){auto j=v.toObject();Rect r{j["x"].toDouble(NAN),j["y"].toDouble(NAN),j["width"].toDouble(NAN),j["height"].toDouble(NAN)};if(!r.valid())throw std::invalid_argument("invalid finite rectangle");return r;}
static Identity identity(const QJsonObject& j){double pid=j["pid"].toDouble();if(!std::isfinite(pid)||pid<1||pid>INT32_MAX||std::floor(pid)!=pid)throw std::invalid_argument("invalid PID number");Identity i{j["stableId"].toString().toStdString(),int64_t(pid)};if(!i.valid()||pid!=i.pid||pid>INT32_MAX)throw std::invalid_argument("invalid exact identity");return i;}
static Rect interpolate(const Rect& a,const Rect& b,double p){return {a.x+(b.x-a.x)*p,a.y+(b.y-a.y)*p,a.width+(b.width-a.width)*p,a.height+(b.height-a.height)*p};}

class Renderer {
    friend struct OfflineCommands;
    struct Output {
        Renderer* owner=nullptr;uint32_t registry=0;uint64_t generation=0;
        wl_output* proxy=nullptr;zxdg_output_v1* logical=nullptr;
        std::string name;int x=0,y=0,width=0,height=0,integerScale=1,preferredScale=0,transform=0,pixelWidth=0,pixelHeight=0,refresh=0;
        bool alive=true,configured=false,frameReady=true,entered=false;
        wl_surface* surface=nullptr;zwlr_layer_surface_v1* layer=nullptr;wp_viewport* viewport=nullptr;
        wp_fractional_scale_v1* fractional=nullptr;wl_egl_window* window=nullptr;EGLSurface egl=EGL_NO_SURFACE;wl_callback* callback=nullptr;
        int bufferWidth=0,bufferHeight=0;uint64_t outstanding=0;
        Rect from;bool endpointPresented=false;
    };
    struct Feedback {Renderer* owner;Output* output;uint64_t generation;Frame frame;struct wp_presentation_feedback* proxy;bool sync=false,mismatch=false;};
    wl_display* display=nullptr;wl_registry* registry=nullptr;wl_compositor* compositor=nullptr;
    zwlr_layer_shell_v1* shell=nullptr;wp_presentation* presentation=nullptr;wp_viewporter* viewporter=nullptr;
    zxdg_output_manager_v1* outputManager=nullptr;wp_fractional_scale_manager_v1* fractionalManager=nullptr;
    std::vector<std::unique_ptr<Output>> outputs;std::map<uint64_t,std::unique_ptr<Feedback>> feedbacks;
    EGLDisplay eglDisplay=EGL_NO_DISPLAY;EGLContext context=EGL_NO_CONTEXT;EGLConfig config{};
    GLuint shader=0,texture=0;GLint positionLocation=-1,uvLocation=-1;
    uint64_t generationSerial=0;uint32_t clockId=UINT32_MAX;CommitLedger ledger;
    Identity routeIdentity;std::string digest,operation;Rect target,nativeRect,atlasRect,iconRect;
    QJsonObject waitingRetarget;std::vector<Output*> required;
    uint64_t startedNs=0,durationNs=400000000;bool running=false,readySent=false,endpointSent=false,quit=false,announced=false,surfacesEnabled=true,swapping=false;
    std::string deferredCancel;uint64_t routeAcceptedNs=0,endpointHeldNs=0;
    size_t uploadCount=0;bool backendSupported=false;QByteArray input;
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
        GLuint vertex=compile(GL_VERTEX_SHADER,"attribute vec2 position;attribute vec2 uv;varying vec2 tex;void main(){tex=uv;gl_Position=vec4(position,0.,1.);}");
        GLuint fragment=compile(GL_FRAGMENT_SHADER,"precision mediump float;uniform sampler2D atlas;varying vec2 tex;void main(){gl_FragColor=texture2D(atlas,tex);}");
        shader=glCreateProgram();glAttachShader(shader,vertex);glAttachShader(shader,fragment);glLinkProgram(shader);glDeleteShader(vertex);glDeleteShader(fragment);
        GLint ok=0;glGetProgramiv(shader,GL_LINK_STATUS,&ok);if(!ok)throw std::runtime_error("GPU shader linking failed");
        positionLocation=glGetAttribLocation(shader,"position");uvLocation=glGetAttribLocation(shader,"uv");
        const auto safe=[](const char* value){return std::string(value?value:"");};
        const auto vendor=safe(eglQueryString(eglDisplay,EGL_VENDOR));
        const auto renderer=safe(reinterpret_cast<const char*>(glGetString(GL_RENDERER)));
        const auto version=safe(reinterpret_cast<const char*>(glGetString(GL_VERSION)));
        const bool material=reviewedInstalledMesaMaterial();
        emitEvent({{"event","backendObserved"},{"eglVendor",qs(vendor)},{"renderer",qs(renderer)},{"version",qs(version)},{"eglVersion",qs(safe(eglQueryString(eglDisplay,EGL_VERSION)))},{"nativeAuthority",false},{"reviewed",reviewedGPUBackend(vendor,version,renderer) && material},{"mappedMaterialMatches",material}});
        if(!reviewedGPUBackend(vendor,version,renderer)||!material)throw std::runtime_error("unreviewed EGL commit backend; no route authority");
        backendSupported=true;
        emitEvent({{"event","gpu"},{"eglVendor",qs(vendor)},{"renderer",qs(renderer)},{"version",reinterpret_cast<const char*>(glGetString(GL_VERSION))}});
    }
    void closeOutput(Output& o){
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
        o.configured=false;
    }
    void cancel(const std::string& reason){
        const bool was=ledger.isActive()||!required.empty();auto token=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();ledger.cancel();running=false;waitingRetarget={};
        if(swapping){deferredCancel=reason;return;}
        surfacesEnabled=false;
        for(auto& o:outputs)closeOutput(*o);
        required.clear();readySent=false;endpointSent=false;announced=false;
        if(was)emitEvent({{"event","cancelled"},{"token",qs(token)},{"reason",qs(reason)},{"nativeAuthority",false}});
    }
    void changed(Output& o){
        o.generation=++generationSerial;
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
    void upload(const std::string& path,const std::string& expected,int expectedWidth,int expectedHeight){
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
        if(texture)glDeleteTextures(1,&texture);glGenTextures(1,&texture);glBindTexture(GL_TEXTURE_2D,texture);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        glPixelStorei(GL_UNPACK_ALIGNMENT,1);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image.width,image.height,0,GL_RGBA,GL_UNSIGNED_BYTE,rgba.data());
        if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("GPU snapshot upload failed");++uploadCount;
        emitEvent({{"event","uploaded"},{"digest",qs(expected)},{"pixels",QJsonArray{int(image.width),int(image.height)}},{"uploadCount",int(uploadCount)}});
    }
    void notifyAuthority(){
        if(ledger.nativeReady()&&!readySent){readySent=true;emitEvent({{"event","ready"},{"token",qs(ledger.token())},{"stableId",qs(routeIdentity.stable)},{"pid",double(routeIdentity.pid)},{"digest",qs(digest)},{"servicePromoted",true}});}
        if(ledger.nativeEndpoint()&&!endpointSent){endpointSent=true;endpointHeldNs=monotonicNs();emitEvent({{"event","endpoint"},{"token",qs(ledger.token())},{"stableId",qs(routeIdentity.stable)},{"pid",double(routeIdentity.pid)},{"digest",qs(digest)},{"servicePromoted",true}});}
    }
    void emitPresented(const Presented& p,const char* event,bool accepted){
        const auto& frame=p.frame;
        emitEvent({{"event",event},{"accepted",accepted},{"token",qs(frame.token)},{"digest",qs(frame.digest)},{"stableId",qs(frame.identity.stable)},{"pid",double(frame.identity.pid)},{"output",qs(frame.output)},{"generation",double(frame.generation)},{"sequence",QString::number(frame.sequence)},{"submittedNs",QString::number(frame.submittedNs)},{"timestampNs",QString::number(p.timestampNs)},{"outputSequence",QString::number(p.compositorSequence)},{"rectangle",rectangleJson(frame.rectangle)},{"progress",frame.progress},{"endpoint",frame.endpoint}});
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
    void draw(Output& o,double p){
        if(!o.alive||!o.configured||!o.frameReady||o.outstanding||o.endpointPresented)return;
        if(!makeCurrent(o)){cancel("eglMakeCurrent failed");return;}
        glViewport(0,0,o.bufferWidth,o.bufferHeight);glDisable(GL_SCISSOR_TEST);glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
        const bool active=ledger.isActive()&&std::find(required.begin(),required.end(),&o)!=required.end();
        Rect rect=o.from;
        if(active){
            rect=interpolate(o.from,target,p);const GLfloat left=2*(rect.x-o.x)/o.width-1,right=2*(rect.x+rect.width-o.x)/o.width-1;
            const GLfloat top=1-2*(rect.y-o.y)/o.height,bottom=1-2*(rect.y+rect.height-o.y)/o.height;
            const GLfloat positions[]={left,top,right,top,left,bottom,right,bottom};const GLfloat uv[]={0,0,1,0,0,1,1,1};
            glEnable(GL_BLEND);glBlendFunc(GL_ONE,GL_ONE_MINUS_SRC_ALPHA);glUseProgram(shader);glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,texture);glUniform1i(glGetUniformLocation(shader,"atlas"),0);
            glEnableVertexAttribArray(positionLocation);glEnableVertexAttribArray(uvLocation);glVertexAttribPointer(positionLocation,2,GL_FLOAT,GL_FALSE,0,positions);glVertexAttribPointer(uvLocation,2,GL_FLOAT,GL_FALSE,0,uv);glDrawArrays(GL_TRIANGLE_STRIP,0,4);
            glDisableVertexAttribArray(positionLocation);glDisableVertexAttribArray(uvLocation);
        }
        if(glGetError()!=GL_NO_ERROR){cancel("GPU draw failed");return;}
        o.callback=wl_surface_frame(o.surface);o.frameReady=false;
        static const wl_callback_listener frameListener={[](void* p,wl_callback* callback,uint32_t){auto& o=*static_cast<Output*>(p);wl_callback_destroy(callback);o.callback=nullptr;o.frameReady=true;}};
        wl_callback_add_listener(o.callback,&frameListener,&o);
        uint64_t number=0;std::optional<Frame> submittedScene;
        if(active){
            auto frame=ledger.prepare(o.name,o.generation,rect,p,p==1,monotonicNs());if(!frame){cancel("frame ledger rejected submission");return;}
            number=frame->sequence;submittedScene=*frame;auto f=std::make_unique<Feedback>(Feedback{this,&o,o.generation,*frame,wp_presentation_feedback(presentation,o.surface),false,false});
            static const wp_presentation_feedback_listener feedbackListener={
                [](void* p,struct wp_presentation_feedback*,wl_output* output){auto& f=*static_cast<Feedback*>(p);if(output==f.output->proxy)f.sync=true;else f.mismatch=true;},
                [](void* p,struct wp_presentation_feedback*,uint32_t hi,uint32_t lo,uint32_t ns,uint32_t,uint32_t seqhi,uint32_t seqlo,uint32_t){auto& f=*static_cast<Feedback*>(p);f.owner->feedbackDone(f,((uint64_t(hi)<<32)|lo)*1000000000+ns,(uint64_t(seqhi)<<32)|seqlo);},
                [](void* p,struct wp_presentation_feedback*){auto& f=*static_cast<Feedback*>(p);f.owner->ledger.discarded(f.frame.sequence);f.owner->cancel("own commit feedback discarded");}
            };
            wp_presentation_feedback_add_listener(f->proxy,&feedbackListener,f.get());feedbacks[number]=std::move(f);o.outstanding=number;
        }
        swapping=true;const bool success=eglSwapBuffers(eglDisplay,o.egl)==EGL_TRUE;swapping=false;
        if(!deferredCancel.empty()){auto reason=deferredCancel;deferredCancel.clear();cancel(reason);return;}
        if(active){
            const auto accepted=ledger.swapReturned(number,success);
            // A deferred feedback callback becomes actual accepted evidence only
            // now, tied to its original immutable submitted scene.
            if(accepted==Result::RecordedCurrent||accepted==Result::RecordedOld){const auto& actual=ledger.records().back();emitPresented(actual,"presented",true);if(accepted==Result::RecordedCurrent&&actual.frame.endpoint)o.endpointPresented=true;}
            emitEvent({{"event","swap"},{"success",success},{"token",qs(submittedScene->token)},{"digest",qs(submittedScene->digest)},{"stableId",qs(submittedScene->identity.stable)},{"pid",double(submittedScene->identity.pid)},{"output",qs(submittedScene->output)},{"generation",double(submittedScene->generation)},{"sequence",QString::number(number)},{"rectangle",rectangleJson(submittedScene->rectangle)},{"progress",submittedScene->progress},{"uploadCount",int(uploadCount)}});
        }
        if(!success){cancel("eglSwapBuffers failed; authority retired");return;}
        notifyAuthority();
    }
    void applyRetarget(){
        if(waitingRetarget.isEmpty()||ledger.hasPending())return;
        auto j=waitingRetarget;waitingRetarget={};auto token=j["token"].toString().toStdString();
        if(!ledger.retarget(routeIdentity,token)){cancel("presented handover unavailable");return;}
        for(auto* o:required){o->from=ledger.presentedOrigins().at(o->name).frame.rectangle;o->endpointPresented=false;}
        target=rectangle(j["target"]);durationNs=j["durationMs"].toInt()*1000000ULL;startedNs=monotonicNs();running=true;readySent=false;endpointSent=false;routeAcceptedNs=monotonicNs();endpointHeldNs=0;
        QJsonArray origins;for(auto* o:required){const auto& f=ledger.presentedOrigins().at(o->name);origins.append(QJsonObject{{"output",qs(o->name)},{"generation",double(o->generation)},{"sequence",QString::number(f.frame.sequence)},{"timestampNs",QString::number(f.timestampNs)},{"rectangle",rectangleJson(f.frame.rectangle)}});}
        emitEvent({{"event","retargeted"},{"token",qs(token)},{"origins",origins},{"startNs",QString::number(startedNs)},{"sourceReused",true},{"nativeAuthority",false},{"uploadCount",int(uploadCount)}});
        if(j["promoted"].toBool()){ledger.promote(routeIdentity,token);notifyAuthority();}
    }
    void command(const QJsonObject& j){
        auto kind=j["command"].toString();
        if(kind=="state"){
            QJsonArray records;for(const auto& p:ledger.records()){const auto& f=p.frame;records.append(QJsonObject{{"token",qs(f.token)},{"stableId",qs(f.identity.stable)},{"pid",double(f.identity.pid)},{"digest",qs(f.digest)},{"output",qs(f.output)},{"generation",double(f.generation)},{"sequence",QString::number(f.sequence)},{"submittedNs",QString::number(f.submittedNs)},{"timestampNs",QString::number(p.timestampNs)},{"outputSequence",QString::number(p.compositorSequence)},{"rectangle",rectangleJson(f.rectangle)},{"progress",f.progress},{"endpoint",f.endpoint}});}
            emitEvent({{"event","state"},{"active",ledger.isActive()},{"token",qs(ledger.token())},{"nativeReady",ledger.nativeReady()},{"nativeEndpoint",ledger.nativeEndpoint()},{"pending",int(ledger.pendingCount())},{"uploadCount",int(uploadCount)},{"records",records}});return;
        }
        if(kind=="prepareOutputs"){if(ledger.isActive())throw std::invalid_argument("route already active");surfacesEnabled=true;announced=false;return;}
        if(kind=="stop"){cancel("renderer shutdown");quit=true;return;}
        if(kind=="cancel"){const auto latest=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();if(j["token"].toString().toStdString()==latest&&identity(j)==routeIdentity)cancel("service cancelled exact latest token");else emitEvent({{"event","cancelRejected"},{"token",j["token"]},{"nativeAuthority",false}});return;}
        if(kind=="seed"){
            if(ledger.isActive())throw std::invalid_argument("active route must be cancelled before new snapshot");
            auto id=identity(j);auto token=j["token"].toString().toStdString(),hash=j["digest"].toString().toStdString();
            if(!validToken(token)||!validDigest(hash))throw std::invalid_argument("invalid whole token/digest");
            auto from=rectangle(j["from"]),end=rectangle(j["target"]),native=rectangle(j["nativeRect"]),atlas=rectangle(j["atlasRect"]),icon=rectangle(j["iconRect"]);
            auto inset=j["insets"].toObject();double left=inset["left"].toDouble(NAN),top=inset["top"].toDouble(NAN),right=inset["right"].toDouble(NAN),bottom=inset["bottom"].toDouble(NAN);
            for(auto value:{left,top,right,bottom})if(!std::isfinite(value)||value<0)throw std::invalid_argument("invalid captured insets");
            if(std::abs(atlas.x+left-native.x)>1e-6||std::abs(atlas.y+top-native.y)>1e-6||std::abs(atlas.width-left-right-native.width)>1e-6||std::abs(atlas.height-top-bottom-native.height)>1e-6)throw std::invalid_argument("captured atlas/native geometry disagrees");
            auto pixels=j["pixels"].toArray();int pw=pixels.size()==2?pixels[0].toInt():0,ph=pixels.size()==2?pixels[1].toInt():0;
            double captureScale=j["captureScale"].toDouble();if(!std::isfinite(captureScale)||captureScale<=0||captureScale>8||pw<=0||ph<=0||std::abs(atlas.width*captureScale-pw)>1e-6||std::abs(atlas.height*captureScale-ph)>1e-6)throw std::invalid_argument("invalid captured pixel scale/extent");
            auto op=j["operation"].toString();if(op!="minimize"&&op!="restore")throw std::invalid_argument("invalid operation");
            if(from!=(op=="minimize"?atlas:icon)||end!=(op=="minimize"?icon:atlas))throw std::invalid_argument("seed rectangle does not match captured operation endpoints");
            int duration=j["durationMs"].toInt();if(duration<1||duration>4000)throw std::invalid_argument("invalid duration");
            std::map<std::string,uint64_t> generations;std::vector<Output*> selected;
            for(auto value:j["outputs"].toArray()){
                auto o=value.toObject();auto name=o["name"].toString().toStdString();double number=o["generation"].toDouble();if(!std::isfinite(number)||number<1||number>9007199254740991.0||std::floor(number)!=number)throw std::invalid_argument("invalid output generation number");uint64_t gen=number;
                auto match=std::find_if(outputs.begin(),outputs.end(),[&](auto& p){return p->alive&&p->configured&&p->preferredScale&&p->name==name&&p->generation==gen;});
                if(match==outputs.end()||generations.contains(name))throw std::invalid_argument("stale/duplicate output generation");
                selected.push_back(match->get());generations[name]=gen;
            }
            if(selected.empty())throw std::invalid_argument("no ready required outputs");
            if(!makeCurrent(*selected.front()))throw std::runtime_error("snapshot upload context unavailable");
            upload(j["path"].toString().toStdString(),hash,pw,ph);ledger.configure(generations);ledger.seed(id,token,hash);
            routeIdentity=id;digest=hash;operation=op.toStdString();nativeRect=native;atlasRect=atlas;iconRect=icon;target=end;durationNs=duration*1000000ULL;required=selected;
            for(auto* o:required){o->from=from;o->endpointPresented=false;}
            routeAcceptedNs=monotonicNs();endpointHeldNs=0;
            running=false;readySent=false;endpointSent=false;emitEvent({{"event","seeded"},{"token",qs(token)},{"nativeAuthority",false}});return;
        }
        if(kind=="retarget"){
            auto token=j["token"].toString().toStdString();int duration=j["durationMs"].toInt();auto end=rectangle(j["target"]);auto operation=j["operation"].toString();if((operation!="minimize"&&operation!="restore")||end!=(operation=="minimize"?iconRect:atlasRect))throw std::invalid_argument("retarget must use retained captured endpoint");
            auto prior=waitingRetarget.isEmpty()?ledger.token():waitingRetarget["token"].toString().toStdString();
            if(!ledger.isActive()||identity(j)!=routeIdentity||!validToken(token)||token.substr(0,12)!=prior.substr(0,12)||std::stoull(token.substr(13))<=std::stoull(prior.substr(13))||duration<1||duration>4000)throw std::invalid_argument("invalid visual retarget");
            waitingRetarget=j;waitingRetarget["promoted"]=false;ledger.suspendAuthority();readySent=false;endpointSent=false;emitEvent({{"event","retargetAccepted"},{"token",qs(token)},{"receivedNs",QString::number(monotonicNs())},{"nativeAuthority",false}});applyRetarget();return;
        }
        if(kind=="validate"){
            if(!waitingRetarget.isEmpty()){if(identity(j)!=routeIdentity||j["token"]!=waitingRetarget["token"])throw std::invalid_argument("validation superseded by newer accepted visual intent");waitingRetarget["promoted"]=true;return;}
            if(!ledger.promote(identity(j),j["token"].toString().toStdString()))throw std::invalid_argument("validation does not match current visual token");notifyAuthority();return;
        }
        if(kind=="start"){
            if(identity(j)!=routeIdentity||j["token"].toString().toStdString()!=ledger.token()||!ledger.nativeReady())throw std::invalid_argument("start lacks exact presented/promoted readiness");
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
    ~Renderer(){
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
            if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned display dispatch failed");attachLogicalOutputs();
            if(surfacesEnabled)for(auto& o:outputs)createSurface(*o);applyRetarget();
            const auto batchNow=monotonicNs();const double batchProgress=running?std::clamp(double(batchNow-startedNs)/durationNs,0.0,1.0):0;
            for(auto& o:outputs){if(!waitingRetarget.isEmpty())break;draw(*o,batchProgress);}publishOutputs();
            if(ledger.timedOut(monotonicNs()))cancel("presentation deadline expired");
            const auto now=monotonicNs();
            if(ledger.isActive()&&((!running&&now-routeAcceptedNs>2000000000ULL)||(endpointHeldNs&&now-endpointHeldNs>2000000000ULL)))cancel("controller handshake deadline expired");
            while(wl_display_prepare_read(display)!=0)if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned pending dispatch failed");
            if(wl_display_flush(display)<0&&errno!=EAGAIN)throw std::runtime_error("owned display flush failed");
            pollfd fds[]={{wl_display_get_fd(display),POLLIN,0},{STDIN_FILENO,POLLIN,0}};int count=poll(fds,2,20);if(count<0&&errno!=EINTR)throw std::runtime_error("owned display poll failed");
            if(fds[0].revents&POLLIN){if(wl_display_read_events(display)<0)throw std::runtime_error("owned display read failed");}else wl_display_cancel_read(display);
            if(fds[0].revents&(POLLHUP|POLLERR))throw std::runtime_error("owned display disconnected");
            if(wl_display_dispatch_pending(display)<0)throw std::runtime_error("owned display callback failed");
            if(fds[1].revents&(POLLIN|POLLHUP)){
                char buffer[8192];ssize_t n=read(STDIN_FILENO,buffer,sizeof(buffer));if(n==0){cancel("controller pipe closed");quit=true;}else if(n>0)input.append(buffer,n);
                if(input.size()>1048576)throw std::runtime_error("command bound exceeded");
                int index=0;while((index=input.indexOf('\n'))>=0){auto line=input.left(index);input.remove(0,index+1);try{QJsonParseError error;auto doc=QJsonDocument::fromJson(line,&error);if(error.error!=QJsonParseError::NoError||!doc.isObject())throw std::invalid_argument("invalid JSON command");command(doc.object());}catch(const std::exception& e){emitEvent({{"event","rejected"},{"reason",e.what()},{"nativeAuthority",false}});}}
            }
        }
    }
};
#ifndef OWNED_EGL_OFFLINE_TEST
int main(int argc,char** argv){
    if(argc==2&&std::string(argv[1])=="--describe"){emitEvent({{"status","staged prototype"},{"protocols",QJsonArray{"layer-shell","presentation","viewporter","xdg-output","fractional-scale"}},{"namespace","hoskinson-window-motion"},{"nativeTested",false},{"serviceIntegrated",false}});return 0;}
    try{Renderer r;r.run();return 0;}catch(const std::exception& e){emitEvent({{"event","fatal"},{"reason",e.what()},{"nativeAuthority",false}});return 1;}
}

#endif
