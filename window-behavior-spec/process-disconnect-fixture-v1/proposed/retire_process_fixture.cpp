#include "ProcessRegistry.hpp"
#include <QCoreApplication>
#include <QMetaMethod>
#include <QJsonDocument>
#include <QJsonArray>
#include <QFileInfo>
#include <QProcessEnvironment>
#include <QQmlContext>
#include <QEventLoop>
#include <QTimer>
#include <filesystem>
#include <iostream>
#include <memory>
#include <unistd.h>
using namespace Lifetime;
static int checks=0;
void check(bool yes,const char*why){if(!yes)throw std::runtime_error(why);++checks;}
class DataStreamParser:public QObject{Q_OBJECT public:using QObject::QObject;};
class StdioCollector:public DataStreamParser {
 Q_OBJECT Q_PROPERTY(QString text READ text) Q_PROPERTY(bool waitForEnd READ waitForEnd)
public:QString collected;bool waiting=true;using DataStreamParser::DataStreamParser;QString text()const{return collected;}bool waitForEnd()const{return waiting;}
signals:void streamFinished();
};
class Process:public QObject {
 Q_OBJECT Q_PROPERTY(DataStreamParser* stdout READ out) Q_PROPERTY(DataStreamParser* stderr READ err)
 Q_PROPERTY(QStringList command READ command) Q_PROPERTY(QVariant processId READ processId)
public:
 QProcess child;StdioCollector*outAllocation,*errAllocation;QStringList selected;bool outFirst=true,missingErr=false;mutable std::function<void()>getterFault;
 Process(StdioCollector*out,StdioCollector*err):outAllocation(out),errAllocation(err){
  connect(&child,&QProcess::started,this,[&]{emit started();child.write("x");});
  connect(&child,&QProcess::finished,this,[&](int code,QProcess::ExitStatus status){outAllocation->collected=QString::fromUtf8(child.readAllStandardOutput());errAllocation->collected=QString::fromUtf8(child.readAllStandardError());if(outFirst){emit outAllocation->streamFinished();if(!missingErr)emit errAllocation->streamFinished();emit exited(code,status);}else{emit exited(code,status);if(!missingErr)emit errAllocation->streamFinished();emit outAllocation->streamFinished();}});
 }
 DataStreamParser*out()const{auto*result=outAllocation;if(getterFault){auto f=std::move(getterFault);getterFault=nullptr;f();}return result;}
 DataStreamParser*err()const{return errAllocation;}QStringList command()const{return selected;}QVariant processId()const{return child.state()==QProcess::NotRunning?QVariant::fromValue(nullptr):QVariant::fromValue(child.processId());}
 void launch(){child.setProgram(selected[0]);child.setArguments(selected.mid(1));QProcessEnvironment env;env.insert("HOME",qEnvironmentVariable("HOME"));env.insert("XDG_RUNTIME_DIR",qEnvironmentVariable("XDG_RUNTIME_DIR"));env.insert("PATH","/usr/bin");env.insert("LC_ALL","C");child.setProcessEnvironment(env);child.start();}
public:std::function<void(const QMetaMethod&)>disconnectProbe;
protected:
 void disconnectNotify(const QMetaMethod&method)override{if(disconnectProbe){auto probe=disconnectProbe;probe(method);}QObject::disconnectNotify(method);}
signals:void started();void exited(int,QProcess::ExitStatus);
};
QByteArray argv(const QStringList&parts){QByteArray raw;for(const auto&p:parts)raw+=p.toUtf8()+'\0';return raw;}
KernelExpected expected(const QStringList&command,const QJsonObject&packet){KernelExpected e;e.parent=getpid();e.group=getpgrp();e.executable=QFileInfo(command[0]).canonicalFilePath();e.executableSHA256=digest(boundedFile(e.executable,128*1024*1024));e.argv=argv(command);e.cgroup=boundedFile("/proc/self/cgroup");e.environment={{"HOME",qgetenv("HOME")},{"XDG_RUNTIME_DIR",qgetenv("XDG_RUNTIME_DIR")},{"PATH","/usr/bin"},{"LC_ALL","C"}};
 for(const auto&name:{"user","mnt","net","pid","ipc","uts","cgroup"})e.namespaces[QString::fromLatin1(name)]=QString::fromStdString(std::filesystem::read_symlink(std::string("/proc/self/ns/")+name).string());
 e.observerExecutable=QFileInfo("/proc/self/exe").canonicalFilePath();e.observerSHA256=digest(boundedFile("/proc/self/exe",128*1024*1024));e.observerARGV=boundedFile("/proc/self/cmdline");e.observerCgroup=e.cgroup;for(const auto&[key,_]:e.environment)if(qEnvironmentVariableIsSet(key.constData()))e.observerEnvironment[key]=qgetenv(key.constData());
 const auto modes=packet["inputModes"].toObject();const auto inputs=packet["inputs"].toObject();for(auto i=inputs.begin();i!=inputs.end();++i)e.code[i.key()]={i.value().toString().toLatin1(),uint32_t(modes[i.key()].toInt())};const auto links=packet["symlinks"].toObject();for(auto i=links.begin();i!=links.end();++i)e.links[i.key()]=i.value().toString();return e;
}
struct Case {
 QQmlEngine engine;QObject provider,menu,row,popup;StdioCollector out,err;Process process{&out,&err};bool source=true,current=true,strict=true;
 Case(Registry&base,const QStringList&command){process.selected=command;for(auto*o:{&provider,&menu,&row,&popup,static_cast<QObject*>(&process),static_cast<QObject*>(&out),static_cast<QObject*>(&err)})QQmlEngine::setContextForObject(o,engine.rootContext());base.registerProvider(&engine,&provider);}
 ProcessArm arm(const QJsonObject&packet){ProcessArm a;a.engine=&engine;a.provider=&provider;a.menu=&menu;a.row=&row;a.popup=&popup;a.process=&process;a.out=&out;a.err=&err;a.processClass="Process";a.collectorClass="StdioCollector";a.command=process.selected;a.kernel=expected(a.command,packet);a.role="CPUFixture";
  a.sourceGuard=[this]{if(!source)throw Refused("actual CPU source boundary invalidated");};a.currentGuard=[this]{if(!current)throw Refused("actual CPU consumer cancelled");};
  a.receiptGuard=[this](const QByteArray&outBytes,const QByteArray&errBytes,const KernelWitness&w,int code){if(!strict)throw Refused("actual malformed fixture receipt");const auto raw=code==0?outBytes:errBytes;const auto r=strictObject(raw);if(r["cpuFixture"]!=QJsonValue(true)||!r["pid"].isDouble()||r["pid"].toInt()!=w.pid||r["code"].toInt(-1)!=code)throw Refused("actual CPU child receipt projection differs");};return a;
 }
 void run(){QEventLoop loop;QTimer timer;timer.setSingleShot(true);timer.setInterval(5000);QObject::connect(&timer,&QTimer::timeout,&loop,&QEventLoop::quit);QObject::connect(&process.child,qOverload<int,QProcess::ExitStatus>(&QProcess::finished),&loop,&QEventLoop::quit);timer.start();process.launch();loop.exec();check(process.child.state()==QProcess::NotRunning,"actual CPU child exited within original bounded deadline");}
};
template<class F>void refuses(F f,const char*why){bool yes=false;try{f();}catch(const Refused&){yes=true;}check(yes,why);}
int main(int argc,char**args){QCoreApplication app(argc,args);try{
 check(argc==3,"actual CPU fixture paths required");const auto packet=strictObject(boundedFile(QString::fromLocal8Bit(args[2]),16*1024*1024),16*1024*1024);Registry base;ProcessRegistry observer(base);const auto entry=QString::fromLocal8Bit(args[1]);auto command=[&](const char*mode){return QStringList{"/usr/bin/python3","-I","-S",entry,QString::fromLatin1(mode)};};
 {Case c(base,command("normal"));const auto lease=observer.arm(c.arm(packet));c.run();const auto s=observer.state(&c.process);check(s["normalLifecycle"].toBool()&&s["complete"].toBool(),qPrintable(QJsonDocument::fromVariant(s).toJson()));
  observer.callback(&c.process,lease-1,1,3,QProcess::CrashExit);observer.callback(&c.process,lease-1,0);observer.callback(&c.process,lease-1,2);check(observer.state(&c.process)==s,"old lease callbacks preserve actual accepted record");observer.callback(&c.process,lease,2);check(observer.state(&c.process)["fault"].toBool(),"duplicate current EOF refuses");}
 {Case c(base,command("normal"));c.process.outFirst=false;observer.arm(c.arm(packet));c.run();check(observer.state(&c.process)["complete"].toBool(),"actual Exit-before-EOF alternative order accepted");}
 {Case c(base,command("refusal"));observer.arm(c.arm(packet));c.run();const auto s=observer.state(&c.process);check(s["normalLifecycle"].toBool()&&!s["complete"].toBool()&&s["exitCode"].toInt()==2,"real refusal exit2 normal lifecycle not completion");}
 {Case c(base,command("crash"));observer.arm(c.arm(packet));c.run();const auto s=observer.state(&c.process);check(!s["normalLifecycle"].toBool()&&s["fault"].toBool(),"actual QProcess CrashExit cannot become normal");}
 {Case c(base,command("normal"));c.process.missingErr=true;observer.arm(c.arm(packet));c.run();check(!observer.state(&c.process)["normalLifecycle"].toBool(),"actual missing stderr EOF blocks lifecycle");}
 {Case c(base,command("normal"));observer.arm(c.arm(packet));observer.cancel(&c.process);c.run();const auto s=observer.state(&c.process);check(s["normalLifecycle"].toBool()&&!s["complete"].toBool(),"cancellation retains actual normal lifecycle without completion");}
 {Case c(base,command("normal"));observer.arm(c.arm(packet));c.strict=false;c.run();check(observer.state(&c.process)["fault"].toBool(),"actual malformed receipt invalidates completion");}
 {Case c(base,command("normal"));c.process.getterFault=[&]{c.out.waiting=false;};refuses([&]{observer.arm(c.arm(packet));},"actual collector semantics mutation during getter refuses arm");}
 {Case c(base,command("normal"));const auto lease=observer.arm(c.arm(packet));refuses([&]{observer.arm(c.arm(packet));},"pending real lease cannot be replaced");c.run();check(!observer.state(&c.process)["fault"].toBool(),"pending refusal did not silently replace registered original child");observer.callback(&c.process,lease,0);check(observer.state(&c.process)["fault"].toBool(),"duplicate current started refuses");}
 {Case c(base,command("normal"));auto a=c.arm(packet);a.kernel.argv+="extra";observer.arm(a);c.run();check(observer.state(&c.process)["fault"].toBool(),"actual final raw argv mismatch refuses kernel authority");}
 std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"GUI",false},{"actualQProcessKernel",true},{"installedQSProcessAccepted",false},{"unchangedProductFastHelperAccepted",false}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
#include "retire_process_fixture.moc"
