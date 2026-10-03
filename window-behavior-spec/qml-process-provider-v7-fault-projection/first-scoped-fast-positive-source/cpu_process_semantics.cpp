#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMetaProperty>
#include <QPointer>
#include <QQmlEngine>
#include <QQmlContext>
#include <functional>
#include <iostream>
#include <stdexcept>
struct Refused:std::runtime_error{using std::runtime_error::runtime_error;};
static int checks=0;
void check(bool a,const char*b){if(!a)throw std::runtime_error(b);++checks;}
class DataStreamParser:public QObject{Q_OBJECT public:using QObject::QObject;};
class StdioCollector:public DataStreamParser{Q_OBJECT public:using DataStreamParser::DataStreamParser;};
class Process:public QObject {
 Q_OBJECT Q_PROPERTY(DataStreamParser* stdout READ out)
public:
 DataStreamParser*selected=nullptr;mutable std::function<void()>fault;
 DataStreamParser*out()const{auto*answer=selected;if(fault){auto call=std::move(fault);fault=nullptr;call();}return answer;}
};
struct Guard {
 QPointer<QObject>process,collector;QPointer<QQmlContext>context;QQmlContext*address;QQmlEngine*engine;
 void stable()const{
  if(process.isNull()||collector.isNull()||context.isNull()||!context->isValid()||context->engine()!=engine||QQmlEngine::contextForObject(process)!=address||QQmlEngine::contextForObject(collector)!=address)throw Refused("actual allocation/context changed");
 }
};
bool selectedPointer(QObject*p,const QMetaProperty&field,QObject*expected,const Guard&guard){
 guard.stable();const auto type=field.metaType();
 if(!field.isReadable()||!type.flags().testFlag(QMetaType::PointerToQObject)||type.sizeOf()!=qsizetype(sizeof(QObject*))||!type.isEqualityComparable())throw Refused("actual comparable QObject pointer property required");
 QVariant wanted=QVariant::fromValue(expected);if(!wanted.convert(type)||wanted.metaType()!=type)throw Refused("live expected pointer conversion refused");guard.stable();
 const auto actual=field.read(p);guard.stable();if(actual.metaType()!=type)throw Refused("actual returned pointer type changed");
 // Compare exact typed pointer storage. Never cast, guard or dereference the
 // returned pointer, which can legitimately be a stale foreign allocation.
 const bool equal=type.equals(actual.constData(),wanted.constData());guard.stable();return equal;
}
template<class F>void refuses(F f,const char*why){bool yes=false;try{f();}catch(const Refused&){yes=true;}check(yes,why);}
int main(int argc,char**argv){QCoreApplication app(argc,argv);try{
 QQmlEngine engine;Process p;StdioCollector collector;QQmlEngine::setContextForObject(&p,engine.rootContext());QQmlEngine::setContextForObject(&collector,engine.rootContext());p.selected=&collector;
 Guard guard{&p,&collector,engine.rootContext(),engine.rootContext(),&engine};const auto field=p.metaObject()->property(p.metaObject()->indexOfProperty("stdout"));
 check(field.metaType().name()==QByteArray("DataStreamParser*"),"actual native exact parser pointer metaType");check(field.metaType()!=QMetaType::fromType<QObject*>(),"native parser pointer differs from generic QObject pointer");check(selectedPointer(&p,field,&collector,guard),"guarded QObject conversion matches actual parser pointer");
 DataStreamParser other;p.selected=&other;check(!selectedPointer(&p,field,&collector,guard),"different live native parser pointer refused");p.selected=nullptr;check(!selectedPointer(&p,field,&collector,guard),"actual null native parser pointer refused");
 auto*dead=new DataStreamParser;delete dead;p.selected=dead;check(!selectedPointer(&p,field,&collector,guard),"foreign stale returned pointer compared without dereference");
 p.selected=&collector;QQmlEngine foreign;p.fault=[&]{QQmlEngine::setContextForObject(&p,foreign.rootContext());};check(selectedPointer(&p,field,&collector,guard),"Qt keeps existing context association; attempted reassignment is not actual replacement");
 {Process process;auto*item=new StdioCollector;auto*ctx=new QQmlContext(&engine);QQmlEngine::setContextForObject(&process,ctx);QQmlEngine::setContextForObject(item,ctx);process.selected=item;Guard g{&process,item,ctx,ctx,&engine};process.fault=[&]{delete item;};refuses([&]{selectedPointer(&process,field,item,g);},"expected collector retirement during getter refused before pointer conversion/equality");delete ctx;}
 {Process process;StdioCollector item;auto*ctx=new QQmlContext(&engine);QQmlEngine::setContextForObject(&process,ctx);QQmlEngine::setContextForObject(&item,ctx);process.selected=&item;Guard g{&process,&item,ctx,ctx,&engine};process.fault=[&]{delete ctx;};refuses([&]{selectedPointer(&process,field,&item,g);},"actual context retirement during getter refused");}
 std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"GUI",false},{"installedQSProcessAccepted",false},{"runtimeRegistryImplemented",false}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
#include "cpu_process_semantics.moc"
