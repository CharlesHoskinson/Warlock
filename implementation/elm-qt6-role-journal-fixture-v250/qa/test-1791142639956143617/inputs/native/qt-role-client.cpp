#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <QApplication>
#include <QDialog>
#include <QLineEdit>
#include <QMenu>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QPainter>
#include <QPlatformSurfaceEvent>
#include <QPointer>
#include <QPushButton>
#include <QSocketNotifier>
#include <QTimer>
#include <QVBoxLayout>
#include <QWindow>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
#include <QtGui/qpa/qplatformwindow_p.h>
#include <wayland-client.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <chrono>
#include <fstream>
#include <regex>
#include <cmath>
#include <iostream>
#include "commands.hpp"
#include "private-runtime.h"
struct Role {char name=0;quint64 instance=0,generation=0;QPointer<QWidget> widget,landmark;QPointer<QLineEdit> entry;QPointer<QWindow> window;QMetaObject::Connection stateConnection;};
static Role roles[5];
static quint64 eventSequence,requestSequence,instanceSequence,processStarted;
static int exitCode,retiring;
static bool stopping,applicationModal,exitEmitted;
static quint64 monotonicUs(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
static quint32 resource(QWindow *w){if(!w)return 0;auto *native=w->nativeInterface<QNativeInterface::Private::QWaylandWindow>();auto *surface=native?native->surface():nullptr;return surface?wl_proxy_get_id(reinterpret_cast<wl_proxy *>(surface)):0;}
static void point(QJsonObject&o,const char*prefix,QPointF p){if(!std::isfinite(p.x())||!std::isfinite(p.y())){o[QString(prefix)+"Available"]=false;return;}o[QString(prefix)+"X"]=p.x();o[QString(prefix)+"Y"]=p.y();}
static QJsonObject record(const char*event,const Role*r=nullptr){QJsonObject o{{"schema",1},{"sequence",qint64(++eventSequence)},{"pid",qint64(getpid())},{"processStarted",qint64(processStarted)},{"monotonicUs",qint64(monotonicUs())},{"requestSequence",qint64(requestSequence)},{"event",event},{"profile",applicationModal?"application-modal":"window-modal"}};
 if(r){o["role"]=QString(QChar(r->name));o["instance"]=qint64(r->instance);o["mapGeneration"]=qint64(r->generation);QWindow*w=r->widget?r->widget->windowHandle():r->window.data();o["surfaceId"]=qint64(resource(w));o["visible"]=r->widget&&!r->widget->isHidden();if(w){o["observedWindowState"]=int(w->windowStates());o["observedModality"]=int(w->modality());o["observedWindowType"]=int(w->type());o["transientSurfaceId"]=qint64(resource(w->transientParent()));o["windowWidth"]=w->width();o["windowHeight"]=w->height();o["devicePixelRatio"]=w->devicePixelRatio();point(o,"windowPosition",w->position());}
 if(r->widget){o["requestedModality"]=int(r->widget->windowModality());o["widgetWidth"]=r->widget->width();o["widgetHeight"]=r->widget->height();}
 if(r->entry){auto draft=r->entry->text();o["draftUTF8"]=draft;o["draftBytes"]=draft.toUtf8().size();}
 if(r->landmark&&r->widget){point(o,"landmarkWindow",r->landmark->mapTo(r->widget,QPoint(0,0)));o["landmarkWidth"]=r->landmark->width();o["landmarkHeight"]=r->landmark->height();}
 }
 return o;}
static void emitRecord(QJsonObject o){auto text=QJsonDocument(o).toJson(QJsonDocument::Compact);std::cout.write(text.constData(),text.size());std::cout<<'\n'<<std::flush;}
static void exitIfRetired(){if(stopping&&!retiring&&!exitEmitted){exitEmitted=true;emitRecord(record(exitCode?"failed-exit":"normalexit"));QApplication::exit(exitCode);}}
static void retire(Role&r){if(!r.widget)return;emitRecord(record("destroy-request",&r));QWidget*widget=r.widget;auto instance=r.instance;auto generation=r.generation;auto surfaceId=resource(r.widget->windowHandle());char name=r.name;QObject::disconnect(r.stateConnection);r.stateConnection={};r.widget=nullptr;r.window=nullptr;r.entry=nullptr;r.landmark=nullptr;retiring++;QObject::connect(widget,&QObject::destroyed,qApp,[instance,name,generation,surfaceId]{auto o=record("local-destroy");o["role"]=QString(QChar(name));o["instance"]=qint64(instance);o["mapGeneration"]=qint64(generation);o["surfaceId"]=qint64(surfaceId);emitRecord(o);retiring--;exitIfRetired();});widget->deleteLater();}
static void retireFamily(int index){if(index<0||index>=5||!roles[index].widget)return;auto*owner=roles[index].widget.data();if(index==0||index==2){if(roles[4].widget&&roles[4].widget->parentWidget()==owner)retire(roles[4]);if(roles[1].widget&&roles[1].widget->parentWidget()==owner){retire(roles[3]);retire(roles[1]);}}else if(index==1)retire(roles[3]);retire(roles[index]);}
static void finish(int code){if(stopping)return;stopping=true;exitCode=code;retire(roles[4]);retire(roles[3]);retire(roles[1]);retire(roles[0]);retire(roles[2]);QTimer::singleShot(0,qApp,exitIfRetired);}
class Landmark final:public QWidget {char role;public:explicit Landmark(char name,QWidget*parent):QWidget(parent),role(name){setMinimumSize(100,60);setObjectName("landmark");}protected:void paintEvent(QPaintEvent*)override{QPainter p(this);p.fillRect(rect(),role=='A'?QColor(200,40,40):role=='C'?QColor(40,200,40):role=='B'?QColor(40,40,200):QColor(80,80,80));p.fillRect(QRect(4,4,8,8),Qt::yellow);for(auto&r:roles)if(r.landmark==this){auto o=record("draw-queued",&r);o["drawWidth"]=width();o["drawHeight"]=height();emitRecord(o);break;}}};
static Role* roleWindow(QWindow*w){for(auto&r:roles)if(r.widget&&r.widget->windowHandle()==w)return &r;return nullptr;}
static Role* roleWidget(QWidget*w){for(auto&r:roles)if(r.widget&&w->window()==r.widget)return &r;return nullptr;}
class Observer final:public QObject {bool eventFilter(QObject*object,QEvent*event)override{auto *window=qobject_cast<QWindow*>(object);auto *widget=qobject_cast<QWidget*>(object);Role*r=window?roleWindow(window):widget?roleWidget(widget):nullptr;
 if(r&&widget==r->widget&&(event->type()==QEvent::Show||event->type()==QEvent::Hide)){if(event->type()==QEvent::Show)r->generation++;emitRecord(record(event->type()==QEvent::Show?"map":"unmap",r));}
 if(r&&widget==r->widget&&event->type()==QEvent::Close){int i=int(r-roles);retireFamily(i);return true;}
 if(r&&window&&(event->type()==QEvent::WindowStateChange||event->type()==QEvent::Expose||event->type()==QEvent::PlatformSurface)){auto o=record(event->type()==QEvent::PlatformSurface?"platform-surface":"window-state",r);o["rawEventType"]=int(event->type());if(event->type()==QEvent::PlatformSurface)o["platformSurfaceEvent"]=int(static_cast<QPlatformSurfaceEvent*>(event)->surfaceEventType());emitRecord(o);}
 bool mouse=event->type()==QEvent::MouseButtonPress||event->type()==QEvent::MouseButtonRelease||event->type()==QEvent::MouseButtonDblClick||event->type()==QEvent::MouseMove;bool key=event->type()==QEvent::KeyPress||event->type()==QEvent::KeyRelease;
 if((mouse||key)&&(window||widget)){QString name=window?"window-":"widget-";name+=mouse?(event->type()==QEvent::MouseMove?"motion":event->type()==QEvent::MouseButtonDblClick?"button-double-click":event->type()==QEvent::MouseButtonPress?"button-press":"button-release"):(event->type()==QEvent::KeyPress?"key-press":"key-release");auto o=record(name.toUtf8().constData(),r);QWindow*source=window?window:widget->windowHandle()?widget->windowHandle():widget->window()->windowHandle();o["sourceSurfaceId"]=qint64(resource(source));o["trackedRecipient"]=r!=nullptr;if(widget)o["recipientWidget"]=widget->objectName();o["rawEventType"]=int(event->type());auto *input=static_cast<QInputEvent*>(event);o["qtTimestamp"]=qint64(input->timestamp());o["qtModifiers"]=qint64(input->modifiers());if(mouse){auto*m=static_cast<QMouseEvent*>(event);o["qtButton"]=qint64(m->button());o["qtButtons"]=qint64(m->buttons());o["qtMouseSource"]=int(m->source());point(o,"local",m->position());point(o,"globalQt",m->globalPosition());}else{auto*k=static_cast<QKeyEvent*>(event);o["qtKey"]=k->key();o["nativeScanCode"]=qint64(k->nativeScanCode());o["nativeVirtualKey"]=qint64(k->nativeVirtualKey());o["nativeModifiers"]=qint64(k->nativeModifiers());o["autoRepeat"]=k->isAutoRepeat();o["keyText"]=k->text();}emitRecord(o);}
 return false;}};
static bool currentRole(int index,quint64 instance,const QWidget*widget){return index>=0&&index<5&&instance!=0&&roles[index].widget&&roles[index].instance==instance&&roles[index].widget==widget;}
static void bindWindow(int index){auto&r=roles[index];if(!r.widget)return;auto*w=r.widget.data();auto*window=w->windowHandle();QObject::disconnect(r.stateConnection);r.window=window;auto instance=r.instance;if(window)r.stateConnection=QObject::connect(window,&QWindow::windowStateChanged,w,[index,instance,w,window](Qt::WindowState){if(currentRole(index,instance,w)&&w->windowHandle()==window)emitRecord(record("observed-state",&roles[index]));});}
static void createWindow(int index,char name,QWidget*parent){Role&r=roles[index];QWidget*w=parent?static_cast<QWidget*>(new QDialog(parent)):new QWidget();r.name=name;r.instance=++instanceSequence;r.generation=0;r.widget=w;w->setObjectName(QString("root-%1").arg(QChar(name)));w->setWindowTitle(QString("ELM-QT6-%1-%2").arg(QChar(name)).arg(getpid()));if(parent)w->setWindowModality(applicationModal?Qt::ApplicationModal:Qt::WindowModal);auto*layout=new QVBoxLayout(w);auto*area=new Landmark(name,w);r.landmark=area;layout->addWidget(area);auto*entry=new QLineEdit("ELM-ROLE-DRAFT",w);entry->setObjectName("draft");entry->setMaxLength(256);r.entry=entry;layout->addWidget(entry);auto*button=new QPushButton("ELM-ROLE-ACTION",w);button->setObjectName("action");layout->addWidget(button);auto instance=r.instance;QObject::connect(button,&QPushButton::clicked,w,[index,instance,w]{if(currentRole(index,instance,w))emitRecord(record("button-clicked",&roles[index]));});w->resize(320,180);emitRecord(record("create",&r));w->show();bindWindow(index);}
static bool execute(const Command&c){if(c.sequence<=requestSequence)return false;requestSequence=c.sequence;auto o=record("request");o["command"]=QString::fromStdString(c.operation);if(c.role)o["requestedRole"]=QString(QChar(c.role));emitRecord(o);const auto&op=c.operation;
 if(op=="quit"){finish(0);return true;}if(op=="inspect"){for(auto&r:roles)if(r.widget)emitRecord(record("inspect",&r));return true;}
 if(op=="open-owner"){if(roles[0].widget)return false;createWindow(0,'A',nullptr);return true;}
 if(op=="reparent-modal"){auto&owner=roles[c.role=='A'?0:2];auto&r=roles[1];if(!owner.widget||!r.widget)return false;retire(roles[3]);retire(roles[4]);auto*w=r.widget.data();QObject::disconnect(r.stateConnection);r.stateConnection={};w->setParent(owner.widget,w->windowFlags());w->setWindowModality(applicationModal?Qt::ApplicationModal:Qt::WindowModal);emitRecord(record("reparent-request",&r));w->show();bindWindow(1);return true;}
 if(op=="create-owners"||op=="create-family"){if(roles[0].widget||roles[2].widget)return false;createWindow(0,'A',nullptr);createWindow(2,'C',nullptr);if(op=="create-family")createWindow(1,'B',roles[0].widget);return true;}
 if(!roles[0].widget&&!c.role)return false;
 if(op=="open-modal"){if(roles[1].widget)return false;createWindow(1,'B',roles[0].widget);return true;}
 if(op=="close-modal"){if(!roles[1].widget)return false;retireFamily(1);return true;}if(op=="close-owner"){retireFamily(0);return true;}
 if(op=="open-nested"){if(roles[3].widget||!roles[1].widget)return false;createWindow(3,'D',roles[1].widget);return true;}if(op=="close-nested"){if(!roles[3].widget)return false;retire(roles[3]);return true;}
 if(op=="open-popup"){if(roles[4].widget)return false;Role&r=roles[4];r.name='P';r.instance=++instanceSequence;r.generation=0;auto*menu=new QMenu(roles[0].widget);r.widget=menu;menu->setObjectName("popup-menu");menu->addAction("ELM-POPUP-ACTION");auto instance=r.instance;QObject::connect(menu,&QMenu::triggered,menu,[menu,instance](QAction*){if(currentRole(4,instance,menu))emitRecord(record("popup-action-triggered",&roles[4]));});emitRecord(record("create",&r));menu->popup(roles[0].widget->mapToGlobal(QPoint(24,24)));r.window=menu->windowHandle();return true;}
 if(op=="close-popup"){if(!roles[4].widget)return false;retire(roles[4]);return true;}
 auto&r=roles[c.role=='A'?0:2];if(!r.widget)return false;if(op=="minimize")r.widget->showMinimized();else if(op=="restore")r.widget->setWindowState(r.widget->windowState()&~Qt::WindowMinimized);else if(op=="maximize")r.widget->showMaximized();else if(op=="unmaximize")r.widget->setWindowState(r.widget->windowState()&~Qt::WindowMaximized);else return false;emitRecord(record("requested-state",&r));return true;
}
static bool privateEnvironment(){const char*gate=getenv("ELM_QT_ROLE_QA"),*runtime=getenv("XDG_RUNTIME_DIR"),*display=getenv("WAYLAND_DISPLAY");if(!gate||strcmp(gate,"1")||!canonical_private_runtime(runtime)||!display||!*display||!strcmp(display,".")||!strcmp(display,"..")||strchr(display,'/')||qEnvironmentVariable("QT_QPA_PLATFORM")!="wayland"||qEnvironmentVariable("WAYLAND_DEBUG")!="client")return false;std::ifstream file("/proc/self/cgroup");std::string groups((std::istreambuf_iterator<char>(file)),{});struct rlimit limit;if(!std::regex_search(groups,std::regex("/qa-harness\\.slice/qa-harness-[A-Za-z0-9_-]+\\.scope(\\n|$)"))||getrlimit(RLIMIT_CORE,&limit)||limit.rlim_cur!=1||limit.rlim_max!=1)return false;struct sockaddr_un address{};address.sun_family=AF_UNIX;int count=snprintf(address.sun_path,sizeof address.sun_path,"%s/%s",runtime,display);struct stat info;if(count<0||size_t(count)>=sizeof address.sun_path||lstat(address.sun_path,&info)||!S_ISSOCK(info.st_mode)||info.st_uid!=geteuid())return false;int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC|SOCK_NONBLOCK,0);if(fd<0)return false;struct ucred peer{};socklen_t length=sizeof peer;bool valid=connect(fd,reinterpret_cast<sockaddr*>(&address),sizeof address)==0&&getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&length)==0&&length==sizeof peer&&peer.uid==geteuid();close(fd);return valid;}
static quint64 ownStart(){QFile f("/proc/self/stat");if(!f.open(QIODevice::ReadOnly))return 0;auto bytes=f.read(4096);auto fields=bytes.mid(bytes.lastIndexOf(')')+2).split(' ');if(fields.size()<20)return 0;bool ok=false;auto start=fields[19].toULongLong(&ok);return ok&&start<=quint64(INT64_MAX)?start:0;}
int main(int argc,char**argv){if(argc==2&&!strcmp(argv[1],"--describe")){std::cout<<"{\"schema\":1,\"toolkit\":\"Qt6\",\"nativeQualification\":false}\n";return 0;}if(argc==3&&!strcmp(argv[1],"--validate-command")){Command c;return parseCommand(argv[2],c)?0:6;}if(argc!=2||(strcmp(argv[1],"--run")&&strcmp(argv[1],"--run-application-modal"))||!privateEnvironment()){std::cerr<<"private Qt Wayland QA environment required\n";return 2;}applicationModal=!strcmp(argv[1],"--run-application-modal");processStarted=ownStart();if(!processStarted)return 2;QApplication app(argc,argv);app.setQuitOnLastWindowClosed(false);Observer observer;app.installEventFilter(&observer);int flags=fcntl(STDIN_FILENO,F_GETFL);if(flags<0||fcntl(STDIN_FILENO,F_SETFL,flags|O_NONBLOCK)<0)return 2;QSocketNotifier notifier(STDIN_FILENO,QSocketNotifier::Read);std::string line;QObject::connect(&notifier,&QSocketNotifier::activated,&app,[&]{char bytes[256];ssize_t n=read(STDIN_FILENO,bytes,sizeof bytes);if(n<0&&(errno==EAGAIN||errno==EINTR))return;if(n<=0){notifier.setEnabled(false);if(!line.empty())emitRecord(record("refusal"));finish(line.empty()?0:6);return;}for(ssize_t i=0;i<n;i++){if(bytes[i]=='\n'){Command c;if(!parseCommand(line,c)||!execute(c)){emitRecord(record("refusal"));notifier.setEnabled(false);finish(6);return;}line.clear();if(stopping){notifier.setEnabled(false);return;}}else if(!bytes[i]||line.size()>=511){emitRecord(record("refusal"));notifier.setEnabled(false);finish(6);return;}else line.push_back(bytes[i]);}});emitRecord(record("ready"));return app.exec();}
