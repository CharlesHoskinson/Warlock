#include "ProcessRegistry.hpp"
#include "ProcessRelay.hpp"
#include <QMetaMethod>
#include <qqml.h>
#include <set>
namespace Lifetime {
namespace {
const QMetaObject*classMeta(QObject*o,const QString&name){for(auto*m=o->metaObject();m;m=m->superClass())if(QString::fromLatin1(m->className())==name)return m;throw Refused("Actual native observer class missing");}
QMetaProperty property(QObject*o,const char*name,QMetaType type){const auto index=o->metaObject()->indexOfProperty(name);if(index<0)throw Refused("Actual observer property missing");const auto p=o->metaObject()->property(index);if(!p.isReadable()||p.metaType()!=type)throw Refused("Actual observer property type differs");return p;}
QMetaProperty pointerProperty(QObject*o,const char*name){const auto index=o->metaObject()->indexOfProperty(name);if(index<0)throw Refused("Actual native parser property missing");const auto p=o->metaObject()->property(index);const auto type=p.metaType();if(!p.isReadable()||QByteArray(type.name())!="DataStreamParser*"||!type.flags().testFlag(QMetaType::PointerToQObject)||type.sizeOf()!=qsizetype(sizeof(QObject*))||!type.isEqualityComparable())throw Refused("Actual comparable native parser pointer property required");return p;}
int processPID(const QVariant&value){const auto id=value.metaType().id();if(id!=QMetaType::Int&&id!=QMetaType::LongLong&&id!=QMetaType::UInt&&id!=QMetaType::ULongLong)throw Refused("Actual processId exact integer QVariant required");bool ok=false;auto n=value.toLongLong(&ok);if(!ok||n<=0||n>2147483647)throw Refused("Actual processId range refused");return int(n);}
}
struct ProcessRegistry::Invocation {
 ProcessArm arm;uint64_t lease=0;EngineToken activation;
 std::array<QObject*,6>objects{};std::array<QPointer<QObject>,6>guards{};std::array<uint64_t,6>generations{};
 std::array<QQmlContext*,6>contexts{};std::array<QPointer<QQmlContext>,6>contextGuards{};std::array<uint64_t,6>contextGenerations{};
 QPointer<QQmlEngine>engine;QPointer<QObject>provider;QMetaProperty outPointer,errPointer,command,pid,outText,errText,outWait,errWait;
 QVariant expectedOut,expectedErr;ProcessRelay*relay=nullptr;std::vector<QMetaObject::Connection>connections;
 bool started=false,kernel=false,exited=false,normal=false,out=false,err=false,gone=false,receipt=false,current=true,fault=false,accepted=false,normalLife=false;
 int code=-1;QByteArray stdoutBytes,stderrBytes;KernelWitness witness;QVariantMap evidence;QString failure;
};
ProcessRegistry::ProcessRegistry(Registry&r):base(r){requireOwnerThread();thread=QThread::currentThread();context=new QObject;}
ProcessRegistry::~ProcessRegistry(){for(auto&[_,r]:rows)for(const auto&c:r->connections)QObject::disconnect(c);delete context;}
ProcessRegistry&ProcessRegistry::shared(){requireOwnerThread();static auto*value=new ProcessRegistry(Registry::shared());return *value;}
std::shared_ptr<ProcessRegistry::Invocation>ProcessRegistry::find(QObject*p,uint64_t lease){requireOwnerThread();if(QThread::currentThread()!=thread)throw Refused("Actual observer thread differs");const auto it=rows.find(p);if(it==rows.end()||it->second->lease!=lease)return {};return it->second;}
void ProcessRegistry::stable(const std::shared_ptr<Invocation>&r,bool current){
 requireOwnerThread();if(QThread::currentThread()!=thread)throw Refused("Actual observer thread differs");r->arm.sourceGuard();
 if(r->engine.isNull()||r->provider.isNull()||base.scope(r->engine.data(),r->provider.data())!=r->activation)throw Refused("Actual observer activation changed");
 auto guards=[&]{
  for(size_t i=0;i<r->objects.size();++i){auto*o=r->objects[i];auto*c=r->contexts[i];if(r->guards[i].isNull()||r->guards[i].data()!=o||r->contextGuards[i].isNull()||r->contextGuards[i].data()!=c||o->thread()!=thread||c->thread()!=thread||!c->isValid()||c->engine()!=r->engine.data()||QQmlEngine::contextForObject(o)!=c||qmlEngine(o)!=r->engine.data()||base.object(o)!=r->generations[i]||base.object(c)!=r->contextGenerations[i])throw Refused("Actual observer object/context generation changed");}
  if(base.scope(r->engine.data(),r->provider.data())!=r->activation)throw Refused("Actual observer activation changed across getter");
 };
 guards();
 auto read=[&](QObject*o,const QMetaProperty&p){guards();const auto value=p.read(o);guards();if(p.metaType()!=QMetaType::fromType<QVariant>()&&value.metaType()!=p.metaType())throw Refused("Actual property result type changed");return value;};
 const auto out=read(r->arm.process,r->outPointer),err=read(r->arm.process,r->errPointer);
 if(out.metaType()!=r->outPointer.metaType()||err.metaType()!=r->errPointer.metaType()||!out.metaType().equals(out.constData(),r->expectedOut.constData())||!err.metaType().equals(err.constData(),r->expectedErr.constData()))throw Refused("Actual native parser pointer changed");guards();
 if(read(r->arm.process,r->command).toStringList()!=r->arm.command||read(r->arm.out,r->outWait).metaType()!=QMetaType::fromType<bool>()||!read(r->arm.out,r->outWait).toBool()||!read(r->arm.err,r->errWait).toBool())throw Refused("Actual Process command/collector semantics changed");
 if(r->out&&read(r->arm.out,r->outText).toString().toUtf8()!=r->stdoutBytes)throw Refused("Actual stdout changed after bound EOF");
 if(r->err&&read(r->arm.err,r->errText).toString().toUtf8()!=r->stderrBytes)throw Refused("Actual stderr changed after bound EOF");
 r->arm.sourceGuard();guards();if(current)r->arm.currentGuard();guards();
}
uint64_t ProcessRegistry::arm(ProcessArm spec){
 requireOwnerThread();if(!spec.sourceGuard||!spec.currentGuard||!spec.receiptGuard||!spec.engine||!spec.provider||!spec.menu||!spec.row||!spec.popup||!spec.process||!spec.out||!spec.err||spec.out==spec.err)throw Refused("Complete actual observer scope required");
 const auto old=rows.find(spec.process);if(old!=rows.end()&&!old->second->guards[3].isNull()&&!lifecycle(old->second))throw Refused("Previous actual helper exit/EOF/gone incomplete");
 if(old!=rows.end()){for(const auto&c:old->second->connections)QObject::disconnect(c);history.push_back(old->second);rows.erase(old);}checkedCapacity(rows.size()+history.size(),CAPACITY);
 auto r=std::make_shared<Invocation>();r->arm=std::move(spec);r->lease=base.allocate(nextLease);r->engine=r->arm.engine;r->provider=r->arm.provider;r->activation=base.scope(r->engine.data(),r->provider.data());
 r->objects={r->arm.menu,r->arm.row,r->arm.popup,r->arm.process,r->arm.out,r->arm.err};std::set<QObject*>seen;
 auto alive=[&]{if(r->engine.isNull()||r->provider.isNull())throw Refused("Actual observer factory retired");for(size_t i=0;i<r->objects.size();++i)if(r->guards[i].isNull()||r->guards[i].data()!=r->objects[i])throw Refused("Actual observer tuple retired during arm");};
 for(size_t i=0;i<r->objects.size();++i){if(!seen.insert(r->objects[i]).second||r->objects[i]->thread()!=thread)throw Refused("Actual distinct observer objects/thread required");r->guards[i]=r->objects[i];}alive();
 r->arm.sourceGuard();alive();classMeta(r->arm.process,r->arm.processClass);classMeta(r->arm.out,r->arm.collectorClass);classMeta(r->arm.err,r->arm.collectorClass);
 for(size_t i=0;i<r->objects.size();++i){alive();r->generations[i]=base.object(r->objects[i]);alive();auto*c=QQmlEngine::contextForObject(r->objects[i]);r->contexts[i]=c;r->contextGuards[i]=c;if(!c||!c->isValid()||c->engine()!=r->engine.data()||qmlEngine(r->objects[i])!=r->engine.data()||c->thread()!=thread)throw Refused("Actual lexical observer factory context required");r->contextGenerations[i]=base.object(c);alive();if(r->contextGuards[i].isNull())throw Refused("Actual observer context retired while arm");}
 r->outPointer=pointerProperty(r->arm.process,"stdout");r->errPointer=pointerProperty(r->arm.process,"stderr");
 // Convert only existing live guarded lexical objects, BEFORE any native getter.
 r->expectedOut=QVariant::fromValue(r->arm.out);r->expectedErr=QVariant::fromValue(r->arm.err);
 if(!r->expectedOut.convert(r->outPointer.metaType())||!r->expectedErr.convert(r->errPointer.metaType()))throw Refused("Actual live lexical collector pointer conversion failed");alive();
 r->command=property(r->arm.process,"command",QMetaType::fromType<QStringList>());r->pid=property(r->arm.process,"processId",QMetaType::fromType<QVariant>());
 r->outText=property(r->arm.out,"text",QMetaType::fromType<QString>());r->errText=property(r->arm.err,"text",QMetaType::fromType<QString>());r->outWait=property(r->arm.out,"waitForEnd",QMetaType::fromType<bool>());r->errWait=property(r->arm.err,"waitForEnd",QMetaType::fromType<bool>());
 stable(r,true);const auto initialPID=r->pid.read(r->arm.process);stable(r,true);if(initialPID.isValid()&&!initialPID.isNull())throw Refused("Actual Process already has a live invocation");const auto process=r->arm.process;const auto lease=r->lease;
 r->relay=new ProcessRelay(context,[this,process,lease](int kind,int code,QProcess::ExitStatus status){callback(process,lease,kind,code,status);});
 const std::array<std::tuple<QObject*,const char*,const char*>,4>signalBindings={{{process,"started()","started()"},{process,"exited(int,QProcess::ExitStatus)","exited(int,QProcess::ExitStatus)"},{r->arm.out,"streamFinished()","outFinished()"},{r->arm.err,"streamFinished()","errFinished()"}}};
 rows.emplace(process,r);
 try{
  for(const auto&[sender,signal,slot]:signalBindings){const auto a=sender->metaObject()->indexOfSignal(signal),b=r->relay->metaObject()->indexOfSlot(slot);if(a<0||b<0)throw Refused("Actual observer signal ABI missing");const auto c=QObject::connect(sender,sender->metaObject()->method(a),r->relay,r->relay->metaObject()->method(b),Qt::DirectConnection);if(!c)throw Refused("Actual observer signal connection refused");r->connections.push_back(c);}
  for(auto*o:r->objects)r->connections.push_back(QObject::connect(o,&QObject::destroyed,context,[this,process,lease]{callback(process,lease,4);},Qt::DirectConnection));
  stable(r,true);if(r->started||r->exited||r->out||r->err||r->fault)throw Refused("Actual invocation occurred during observer arm");return lease;
 }catch(...){for(const auto&c:r->connections)QObject::disconnect(c);delete r->relay;const auto it=rows.find(process);if(it!=rows.end()&&it->second==r)rows.erase(it);throw;}
}
void ProcessRegistry::callback(QObject*p,uint64_t lease,int kind,int code,QProcess::ExitStatus status){auto r=find(p,lease);if(!r)return;try{event(p,lease,kind,code,status);}catch(const std::exception&e){r->fault=true;r->accepted=false;r->normalLife=false;r->failure=QString::fromUtf8(e.what());r->evidence.insert("failure",r->failure);}}
void ProcessRegistry::event(QObject*p,uint64_t lease,int kind,int code,QProcess::ExitStatus status){
 auto r=find(p,lease);if(!r)return;r->accepted=false;r->normalLife=false;stable(r,false);
 if(kind==0){if(r->started)throw Refused("Duplicate actual started");r->started=true;const auto raw=r->pid.read(p);stable(r,false);const auto pid=processPID(raw);r->evidence.insert("observedProcessId",pid);
  QVariantMap observation;KernelWitness before;try{before=readKernel(pid,r->arm.kernel,&observation);}catch(...){r->evidence.insert("kernelObservationBefore",observation);throw;}r->evidence.insert("kernelObservationBefore",observation);r->evidence.insert("kernelBefore",before.value());r->evidence.insert("kernelBeforeMaps",QString::fromLatin1(before.maps));observation.clear();KernelWitness after;try{after=readKernel(pid,r->arm.kernel,&observation);}catch(...){r->evidence.insert("kernelObservationAfter",observation);throw;}r->evidence.insert("kernelObservationAfter",observation);r->evidence.insert("kernelAfter",after.value());r->evidence.insert("kernelAfterMaps",QString::fromLatin1(after.maps));
  auto a=before,b=after;a.maps.clear();b.maps.clear();if(a!=b)throw Refused("Actual kernel identity changed across registration");r->witness=after;r->kernel=true;stable(r,false);
 }else if(kind==1){if(!r->started||r->exited)throw Refused("Missing start/duplicate actual exit");r->exited=true;r->normal=status==QProcess::NormalExit;r->code=code;if(!r->normal)throw Refused("Actual helper CrashExit is not normal lifecycle");
 }else if(kind==2||kind==3){bool&seen=kind==2?r->out:r->err;if(!r->started||seen)throw Refused("Missing start/duplicate actual EOF");const auto actualText=kind==2?r->outText.read(r->arm.out):r->errText.read(r->arm.err);stable(r,false);if(actualText.metaType()!=QMetaType::fromType<QString>())throw Refused("Actual EOF collector text type differs");const auto bytes=actualText.toString().toUtf8();if(bytes.size()>65536)throw Refused("Actual helper stream bound exceeded");(kind==2?r->stdoutBytes:r->stderrBytes)=bytes;seen=true;
 }else throw Refused("Actual observer object retired/unsupported current callback");
}
bool ProcessRegistry::lifecycle(const std::shared_ptr<Invocation>&r){
 if(r->fault||!r->started||!r->kernel||!r->exited||!r->normal||!r->out||!r->err)return false;stable(r,false);r->gone=kernelGone(r->witness);return r->gone;
}
QVariantMap ProcessRegistry::state(QObject*p){
 requireOwnerThread();const auto it=rows.find(p);if(it==rows.end())throw Refused("Actual Process registration missing");auto r=it->second;r->accepted=false;r->normalLife=false;
 try{r->normalLife=lifecycle(r);if(r->normalLife){r->arm.receiptGuard(r->stdoutBytes,r->stderrBytes,r->witness,r->code);r->receipt=true;if(r->current){try{stable(r,true);r->accepted=r->code==0;}catch(const std::exception&e){r->current=false;r->failure=QString::fromUtf8(e.what());}}}}
 catch(const std::exception&e){r->fault=true;r->receipt=false;r->accepted=false;r->normalLife=false;r->failure=QString::fromUtf8(e.what());}
 return {{"lease",qulonglong(r->lease)},{"started",r->started},{"kernelBound",r->kernel},{"exited",r->exited},{"normalExit",r->normal},{"exitCode",r->code},{"stdoutEOF",r->out},{"stderrEOF",r->err},{"kernelGone",r->gone},{"receiptVerified",r->receipt},{"current",r->current},{"fault",r->fault},{"normalLifecycle",r->normalLife},{"complete",r->accepted},{"failure",r->failure},{"stdout",QString::fromUtf8(r->stdoutBytes)},{"stderr",QString::fromUtf8(r->stderrBytes)},{"evidence",r->evidence},{"nativeWrites",0},{"automaticRetries",0}};
}
void ProcessRegistry::cancel(QObject*p){requireOwnerThread();const auto it=rows.find(p);if(it==rows.end())throw Refused("Actual Process registration missing");it->second->current=false;it->second->accepted=false;}
}
