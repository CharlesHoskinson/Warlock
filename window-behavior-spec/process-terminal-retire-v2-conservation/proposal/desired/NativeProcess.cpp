#include "NativeProcess.hpp"
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJSValue>
#include <QRegularExpression>
#include <QMetaProperty>
#include <sys/stat.h>
#include <unistd.h>
#include <filesystem>
#include <cmath>
#include <cerrno>
#include <QSet>
#include <set>
namespace Lifetime {
namespace {
int integer(const QJsonValue&v,int low=0,int high=2147483647){if(!v.isDouble()||v.toDouble()!=v.toInt(-1)||v.toInt(-1)<low||v.toInt(-1)>high)throw Refused("Exact JSON integer authority required");return v.toInt();}
QString string(const QJsonValue&v,const char*pattern=nullptr){if(!v.isString())throw Refused("Exact JSON string required");const auto s=v.toString();if(pattern&&!QRegularExpression(QString::fromLatin1(pattern)).match(s).hasMatch())throw Refused("Canonical JSON string authority required");return s;}
bool boolean(const QJsonValue&v){if(!v.isBool())throw Refused("Exact JSON Boolean authority required");return v.toBool();}
QJsonObject object(const QJsonValue&v){if(!v.isObject())throw Refused("Exact JSON object authority required");return v.toObject();}
void ownedDirectory(const QString&path){struct stat s{};if(QFileInfo(path).canonicalFilePath()!=path||lstat(path.toUtf8().constData(),&s)||!S_ISDIR(s.st_mode)||s.st_uid!=getuid()||(s.st_mode&07777)!=0700)throw Refused("Exact private owned0700 directory required");}
void privatePath(const QString&path,const QString&runtime){if(!path.startsWith(runtime+'/')||QFileInfo(path).canonicalFilePath()!=path)throw Refused("Actual private canonical path required");ownedDirectory(runtime);auto parent=QFileInfo(path).absolutePath();while(parent!=runtime){ownedDirectory(parent);parent=QFileInfo(parent).absolutePath();if(!parent.startsWith(runtime))throw Refused("Private parent escape refused");}}
QByteArray finalARGV(const QJsonArray&items){QByteArray r;for(const auto&item:items)r+=string(item).toUtf8()+'\0';return r;}
QByteArray finalARGV(const QStringList&items){QByteArray r;for(const auto&item:items)r+=item.toUtf8()+'\0';return r;}
QJsonObject fullToken(const QJsonObject&t){const QSet<QString>fields={"address","stableId","pid","session","compositorPid","compositorStart","incarnation","epoch","generation"};const auto keys=t.keys();if(QSet<QString>(keys.begin(),keys.end())!=fields)throw Refused("Complete captured native pin token required");integer(t["pid"],1);integer(t["compositorPid"],1);string(t["address"],"^0x[0-9a-f]+$");string(t["stableId"],"^[0-9a-f]+$");string(t["session"],"^[A-Za-z0-9_]+$");string(t["incarnation"],"^[0-9a-f]{32}$");string(t["compositorStart"],"^[1-9][0-9]*$");for(const auto*key:{"epoch","generation"}){bool ok=false;const auto v=string(t[key],"^[1-9][0-9]*$").toULongLong(&ok);if(!ok||!v)throw Refused("Exact uint64 native pin generation required");}return t;}
QJsonObject publicToken(const QJsonObject&t){const auto keys=t.keys();const QSet<QString>fields={"address","stableId","pid"};if(QSet<QString>(keys.begin(),keys.end())!=fields)throw Refused("Exact captured public pin triple required");integer(t["pid"],1);string(t["address"],"^0x[0-9a-f]+$");string(t["stableId"],"^(0|[1-9a-f][0-9a-f]{0,15})$");return t;}
QJsonObject menuState(QObject*menu){QPointer<QObject>guard=menu;const auto i=menu->metaObject()->indexOfProperty("menuState");if(i<0)throw Refused("Actual lexical menuState property missing");const auto field=menu->metaObject()->property(i);if(!field.isReadable())throw Refused("Actual lexical menuState unreadable");auto raw=field.read(menu);if(guard.isNull())throw Refused("Actual menu retired across state getter");if(raw.metaType()==QMetaType::fromType<QJSValue>())raw=raw.value<QJSValue>().toVariant();if(guard.isNull()||raw.metaType()!=QMetaType::fromType<QVariantMap>())throw Refused("Actual menuState object representation differs");return QJsonObject::fromVariantMap(raw.toMap());}
struct Stamp {uint64_t device,inode,size;int64_t seconds,nanos;uint32_t mode,uid,links;bool operator==(const Stamp&)const=default;};
Stamp stamp(const QString&path){struct stat s{};if(lstat(path.toUtf8().constData(),&s))throw Refused("Actual source/file stamp refused");return {uint64_t(s.st_dev),uint64_t(s.st_ino),uint64_t(s.st_size),int64_t(s.st_mtim.tv_sec),int64_t(s.st_mtim.tv_nsec),uint32_t(s.st_mode),uint32_t(s.st_uid),uint32_t(s.st_nlink)};}
struct Config {
 Authority provider;QString processPath,pinPath,manifestPath,runtime,home,evidenceDir,role,entry,originalJSON;QByteArray processRaw,pinRaw,manifestRaw;
 QJsonObject pin,request;QJsonValue nonce;QPointer<QObject>menu,process,row,popup,out,err;QPointer<QQmlContext>menuContext;QQmlEngine*engine=nullptr;
 KernelExpected expected;std::map<QString,Stamp>anchors;
 std::array<QPointer<QObject>,6>lexicalObjects;std::array<QPointer<QQmlContext>,6>lexicalContexts;
 void contexts(){for(size_t i=0;i<lexicalObjects.size();++i){const auto&o=lexicalObjects[i];const auto&c=lexicalContexts[i];if(o.isNull()||c.isNull()||QQmlEngine::contextForObject(o.data())!=c.data()||!c->isValid()||c->engine()!=engine||qmlEngine(o.data())!=engine)throw Refused("Original actual lexical context/engine changed");}}
 void lexical(){
  contexts();
  const std::array<std::pair<QPointer<QObject>,QString>,5>ids={{{menu,"root"},{row,"toggleButton"},{process,role=="capture"?"captureProcess":"actionProcess"},{out,role=="capture"?"captureOut":"actionOut"},{err,role=="capture"?"captureErr":"actionErr"}}};
  for(const auto&[guard,id]:ids){if(guard.isNull())throw Refused("Actual fixed lexical Process object retired");auto*context=QQmlEngine::contextForObject(guard.data());QPointer<QQmlContext>cg=context;if(!context||!context->isValid()||context->engine()!=engine||context->objectForName(id)!=guard.data()||cg.isNull()||guard.isNull())throw Refused("Actual fixed lexical Process id/factory differs");}
  if(popup.isNull()||menu.isNull())throw Refused("Actual lexical popup retired");auto*ctx=QQmlEngine::contextForObject(popup.data());if(!ctx||!ctx->isValid()||ctx->engine()!=engine)throw Refused("Actual lexical popup factory differs");const auto index=popup->metaObject()->indexOfProperty("owner");if(index<0)throw Refused("Actual popup owner missing");auto value=popup->metaObject()->property(index).read(popup.data());if(popup.isNull()||menu.isNull())throw Refused("Actual lexical tuple retired across owner getter");QObject*owner=nullptr;
  if(value.metaType()==QMetaType::fromType<QJSValue>()){const auto js=value.value<QJSValue>();if(!js.isQObject())throw Refused("Actual popup owner JS object differs");owner=js.toQObject();}
  else if(value.metaType()==QMetaType::fromType<QObject*>())owner=value.value<QObject*>();else if(value.metaType()==QMetaType::fromType<QQuickItem*>())owner=value.value<QQuickItem*>();else throw Refused("Actual popup owner representation differs");
  if(popup.isNull()||menu.isNull()||owner!=menu.data())throw Refused("Actual popup lexical owner differs");contexts();
 }
 void source(){
  provider.verify();lexical();for(const auto&[path,expectedStamp]:anchors)if(stamp(path)!=expectedStamp)throw Refused("Original source/config/file identity changed");if(QString::fromLocal8Bit(qgetenv("WINDOW_PIN_PROCESS_CONFIG"))!=processPath||QString::fromLocal8Bit(qgetenv("WINDOW_PIN_NATIVE_CONFIG"))!=pinPath)throw Refused("Actual selected Process/Pin config changed");
  if(guardedRegular(processPath,0600,getuid(),1048576)!=processRaw||guardedRegular(pinPath,0600,getuid(),1048576)!=pinRaw||guardedRegular(manifestPath,0600,getuid(),16*1024*1024)!=manifestRaw)throw Refused("Actual frozen Process source/config bytes changed");
  ownedDirectory(runtime);ownedDirectory(home);ownedDirectory(evidenceDir);const auto entryRow=object(pin[role=="capture"?"captureEntry":"entry"]);if(digest(guardedRegular(entry,0700,getuid(),1048576))!=string(entryRow["sha256"]).toLatin1())throw Refused("Actual unchanged direct helper source changed");
  const auto selectors=object(pin["selectors"]);for(auto i=selectors.begin();i!=selectors.end();++i)if(QString::fromLocal8Bit(qgetenv(i.key().toUtf8().constData()))!=string(i.value()))throw Refused("Actual selected frontend environment changed");
  if(menu.isNull()||process.isNull()||menuContext.isNull()||QQmlEngine::contextForObject(menu)!=menuContext.data()||!menuContext->isValid()||menuContext->engine()!=engine)throw Refused("Actual lexical Process source retired");
  auto read=[&](const char*name,QMetaType type){const auto index=process->metaObject()->indexOfProperty(name);if(index<0)throw Refused("Actual Process launch policy property missing");const auto p=process->metaObject()->property(index);if(!p.isReadable()||p.metaType()!=type)throw Refused("Actual Process launch policy type differs");const auto v=p.read(process);if(process.isNull()||v.metaType()!=type)throw Refused("Actual Process launch policy retired/type differs");return v;};
  if(read("clearEnvironment",QMetaType::fromType<bool>()).toBool()||!read("environment",QMetaType::fromType<QVariantHash>()).toHash().isEmpty()||!read("workingDirectory",QMetaType::fromType<QString>()).toString().isEmpty())throw Refused("Actual source Process inheritance policy changed");
 }
 void current(){
  if(menu.isNull())throw Refused("Actual menu retired");contexts();const auto a=menuState(menu.data());contexts();const auto b=menuState(menu.data());contexts();if(a!=b||a["nonce"]!=nonce||!boolean(a["open"])||object(a[role=="capture"?"target":"token"])!=request)throw Refused("Actual menu nonce/captured owner changed");
 }
 void receipt(const QByteArray&out,const QByteArray&err,const KernelWitness&w,int code){
  source();if(code<0||code>3)throw Refused("Actual helper exit outside explicit schema");const auto raw=(code==0||(role=="toggle"&&code==2))?out:err;if(raw.isEmpty())throw Refused("Actual helper receipt missing");if(!((code==0||(role=="toggle"&&code==2))?err:out).isEmpty())throw Refused("Unexpected helper secondary stream");const auto r=strictObject(raw);
  if(integer(r["automaticRetries"])!=0)throw Refused("Helper automatic retry claim differs");const bool claimed=boolean(r["nativeCompletionClaimed"]);const auto result=string(r["result"]);
  const auto identity=QJsonObject{{"pid",w.pid},{"start",w.start},{"parent",w.parent},{"pgid",w.group}};
  const auto file=evidenceDir+'/'+QString::number(w.pid)+'-'+w.start+".json";
  // The frozen helpers can refuse before authority/publication. This admits
  // only normal refused exit1, with no send/authority/success; no Pin completion.
  if(code==1&&!r.contains("authority")){
   if(claimed||result!="refused"||!r["error"].isString()||(r.contains("transport")&&boolean(object(r["transport"])["sendStarted"])))throw Refused("Malformed pre-send refusal");
   struct stat s{};if(lstat(file.toUtf8().constData(),&s)==0||errno!=ENOENT)throw Refused("Unexpected evidence for authority-free refusal");return;
  }
  const auto authority=object(r["authority"]);if(string(authority["role"])!="shell"||object(authority["compositor"])!=object(object(pin["compositor"])["identity"]))throw Refused("Actual helper source role/compositor projection differs");if(object(authority["frontend"])!=identity)throw Refused("Actual helper frontend kernel projection differs");const auto requester=object(authority["requester"]);if(integer(requester["pid"],1)!=getpid()||string(requester["start"])!=provider.start||integer(requester["pgid"],1)!=getpgrp())throw Refused("Actual helper requester differs");
  if(role=="toggle"){if(fullToken(object(r["captured"]))!=request)throw Refused("Actual helper captured owner differs");}else if(object(r["publicIdentity"])!=request||integer(r["nativeWrites"])!=0)throw Refused("Actual capture public owner/write projection differs");
  const auto fileStamp=stamp(file);const auto fileRaw=guardedRegular(file,0600,getuid(),1048576);if(strictObject(fileRaw)!=r)throw Refused("Actual immutable helper receipt file differs");
  const auto transport=object(r["transport"]);if(code==0||(role=="toggle"&&code==2)){
   if(!boolean(transport["sendStarted"])||!boolean(transport["completeServerEOF"]))throw Refused("Actual helper full transport EOF missing");const auto peer=object(transport["peer"]);const auto compositor=object(object(pin["compositor"])["identity"]);if(integer(peer["pid"],1)!=integer(compositor["pid"],1)||static_cast<quint64>(integer(peer["uid"]))!=static_cast<quint64>(getuid()))throw Refused("Actual native helper peer identity differs");
   if(role=="capture"){
    if(code!=0||claimed||result!="captured")throw Refused("Actual capture outcome differs");const auto captured=fullToken(object(r["captured"]));for(const auto*key:{"address","stableId","pid"})if(captured[key]!=request[key])throw Refused("Actual capture native/public owner differs");if(captured["compositorPid"]!=compositor["pid"]||captured["compositorStart"]!=compositor["start"]||captured["session"]!=object(pin["selectors"])["HYPRLAND_INSTANCE_SIGNATURE"])throw Refused("Actual captured compositor differs");
   }else{
    const auto native=object(r["rawNativeResult"]);const bool ok=boolean(native["ok"]),actions=boolean(native["actionsInvoked"]),partial=boolean(native["possiblePartialOutcome"]);const auto phase=string(native["phase"]);string(native["reason"]);if(partial!=(!ok&&actions)||claimed!=ok||((code==0)!=ok)||result!=(ok?"complete":"native-refused"))throw Refused("Actual native action outcome differs");
    if(ok){if(phase!="complete"||!actions||fullToken(object(native["captured"]))!=request)throw Refused("Actual native completed owner/action differs");for(const auto*side:{"before","after"}){const auto row=object(native[side]);for(const auto*key:{"address","stableId","pid","session","incarnation","epoch","generation"})if(row[key]!=request[key])throw Refused("Native completed member projection differs");if(!boolean(row["live"])||!boolean(row["normal"])||boolean(row["fullscreen"]))throw Refused("Native completed member policy differs");boolean(row["floating"]);boolean(row["pinned"]);}const auto before=object(native["before"]),after=object(native["after"]);const bool desired=boolean(native["desiredPinned"]);if(desired==boolean(before["pinned"])||!boolean(after["floating"])||boolean(after["pinned"])!=desired)throw Refused("Native completed exact pin state differs");}
    else{if(phase=="complete"||(phase=="validate"&&actions)||(phase!="validate"&&!actions))throw Refused("Native refused phase/action differs");if(native.contains("captured")&&fullToken(object(native["captured"]))!=request)throw Refused("Native refused owner differs");}
   }
  }else if(claimed||result!=(code==1?"refused":"uncertain"))throw Refused("Actual refused/uncertain helper result differs");
  source();if(stamp(file)!=fileStamp||guardedRegular(file,0600,getuid(),1048576)!=fileRaw)throw Refused("Helper evidence changed across confirmation");
 }
};
}
ProcessArm nativeProcessArm(QQmlEngine*engine,QObject*provider,QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QString&role,const QString&originalJSON,const Authority&authority){
 verifyQuickshellProcess();if(role!="capture"&&role!="toggle")throw Refused("Actual fixed helper role required");if(originalJSON.toUtf8().size()>4096)throw Refused("Original exact helper JSON bound exceeded");auto c=std::make_shared<Config>();c->provider=authority;c->engine=engine;c->menu=menu;c->process=process;c->row=row;c->popup=popup;c->out=out;c->err=err;c->menuContext=QQmlEngine::contextForObject(menu);c->lexicalObjects={menu,row,popup,process,out,err};for(size_t i=0;i<c->lexicalObjects.size();++i){if(c->lexicalObjects[i].isNull())throw Refused("Actual lexical Process object required");c->lexicalContexts[i]=QQmlEngine::contextForObject(c->lexicalObjects[i].data());}c->contexts();c->role=role;c->originalJSON=originalJSON;c->request=strictObject(originalJSON.toUtf8());if(role=="capture")publicToken(c->request);else fullToken(c->request);
 c->processPath=QString::fromLocal8Bit(qgetenv("WINDOW_PIN_PROCESS_CONFIG"));c->pinPath=QString::fromLocal8Bit(qgetenv("WINDOW_PIN_NATIVE_CONFIG"));c->anchors[c->processPath]=stamp(c->processPath);c->anchors[c->pinPath]=stamp(c->pinPath);c->processRaw=guardedRegular(c->processPath,0600,getuid(),1048576);const auto processConfig=strictObject(c->processRaw);if(string(processConfig["schema"])!="qml-pin-process-config-v1")throw Refused("Explicit native Process source config required");
 c->pinRaw=guardedRegular(c->pinPath,0600,getuid(),1048576);c->pin=strictObject(c->pinRaw);if(integer(c->pin["version"],1)!=1||digest(c->pinRaw)!=string(object(processConfig["pinConfig"])["sha256"]).toLatin1()||c->pinPath!=string(object(processConfig["pinConfig"])["path"]))throw Refused("Exact native Pin config source differs");
 c->runtime=string(c->pin["runtime"]);c->home=string(object(c->pin["selectors"])["HOME"]);c->evidenceDir=string(c->pin["evidenceDirectory"]);ownedDirectory(c->runtime);ownedDirectory(c->home);ownedDirectory(c->evidenceDir);privatePath(c->processPath,c->runtime);privatePath(c->pinPath,c->runtime);privatePath(c->evidenceDir,c->runtime);
 if(string(object(c->pin["selectors"])["WINDOW_PIN_PROCESS_CONFIG"])!=c->processPath)throw Refused("Exact preselected registry selector required");
 const auto inputSource=object(processConfig["frozenInputs"]);c->manifestPath=string(inputSource["path"]);privatePath(c->manifestPath,c->runtime);c->anchors[c->manifestPath]=stamp(c->manifestPath);c->manifestRaw=guardedRegular(c->manifestPath,0600,getuid(),16*1024*1024);if(digest(c->manifestRaw)!=string(inputSource["sha256"]).toLatin1())throw Refused("Frozen native Process dependency packet differs");const auto manifest=strictObject(c->manifestRaw,16*1024*1024);const auto hashes=object(manifest["inputs"]),modes=object(manifest["inputModes"]),links=object(manifest["symlinks"]);for(auto i=hashes.begin();i!=hashes.end();++i)c->expected.code[i.key()]={string(i.value()).toLatin1(),uint32_t(integer(modes[i.key()],0,07777))};for(auto i=links.begin();i!=links.end();++i)c->expected.links[i.key()]=string(i.value());
 const auto entryRow=object(c->pin[role=="capture"?"captureEntry":"entry"]);c->entry=string(entryRow["path"]);privatePath(c->entry,c->runtime);c->anchors[c->entry]=stamp(c->entry);if(digest(guardedRegular(c->entry,0700,getuid(),1048576))!=string(entryRow["sha256"]).toLatin1())throw Refused("Actual frozen unchanged helper entry differs");
 const auto interpreter=object(c->pin["interpreter"]);c->expected.executable=string(interpreter["path"]);c->expected.executableSHA256=string(interpreter["sha256"]).toLatin1();c->expected.parent=getpid();c->expected.group=getpgrp();c->expected.argv=finalARGV(QStringList{"/usr/bin/python3","-I","-S",c->entry,role,originalJSON});c->expected.cgroup=boundedFile("/proc/self/cgroup");if(!c->expected.cgroup.contains("/qa-harness.slice/qa-harness-"))throw Refused("Actual private QA source scope required");
 for(const auto*name:{"user","mnt","net","pid","ipc","uts","cgroup"})c->expected.namespaces[QString::fromLatin1(name)]=QString::fromStdString(std::filesystem::read_symlink(std::string("/proc/self/ns/")+name).string());const auto selectors=object(c->pin["selectors"]);for(auto i=selectors.begin();i!=selectors.end();++i)c->expected.environment[i.key().toUtf8()]=string(i.value()).toUtf8();
 int rootCount=0;for(const auto&root:c->pin["requestRoots"].toArray()){const auto r=object(root),id=object(r["identity"]);if(integer(id["pid"],1)!=getpid())continue;++rootCount;c->expected.observerExecutable=string(r["executable"]);c->expected.observerSHA256=string(r["executableSHA256"]).toLatin1();c->expected.observerARGV=finalARGV(r["argv"].toArray());c->expected.observerCgroup=string(r["cgroup"]).toUtf8();for(const auto&[key,_]:c->expected.environment)if(qEnvironmentVariableIsSet(key.constData()))c->expected.observerEnvironment[key]=qgetenv(key.constData());if(string(r["role"])!="shell"||string(id["start"])!=authority.start||integer(id["pgid"],1)!=getpgrp()||finalARGV(r["argv"].toArray())!=boundedFile("/proc/self/cmdline")||string(r["executable"])!=QFileInfo("/proc/self/exe").canonicalFilePath()||string(r["executableSHA256"]).toLatin1()!=digest(boundedFile("/proc/self/exe",128*1024*1024))||string(r["cgroup"]).toUtf8()!=c->expected.cgroup)throw Refused("Actual original shell requester source differs");}if(rootCount!=1)throw Refused("One exact actual shell request root required");
 const auto state=menuState(menu);c->nonce=state["nonce"];if(!c->nonce.isDouble()||c->nonce.toDouble()<=0||c->nonce.toDouble()>=double(SAFE_MAX)||c->nonce.toDouble()!=std::floor(c->nonce.toDouble()))throw Refused("Actual exact menu nonce required");c->source();c->current();
 ProcessArm a;a.engine=engine;a.provider=provider;a.menu=menu;a.row=row;a.popup=popup;a.process=process;a.out=out;a.err=err;a.processClass="Process";a.collectorClass="StdioCollector";a.role=role;a.command={c->entry,role,originalJSON};a.kernel=c->expected;a.changed=[c,providerGuard=QPointer<QObject>(provider),processGuard=QPointer<QObject>(process)](uint64_t lease){
  if(providerGuard.isNull()||processGuard.isNull())return;
  QMetaObject::invokeMethod(providerGuard.data(),[c,providerGuard,processGuard,lease]{
   if(providerGuard.isNull()||processGuard.isNull())return;
   try{requireOwnerThread();c->source();if(providerGuard.isNull()||processGuard.isNull()||providerGuard->thread()!=QThread::currentThread()||processGuard->thread()!=QThread::currentThread())return;
    QMetaObject::invokeMethod(providerGuard.data(),"processLifecycleChanged",Qt::DirectConnection,Q_ARG(QObject*,processGuard.data()),Q_ARG(qulonglong,qulonglong(lease)));
   }catch(...){} // No hint is proof and retired sources cannot emit one.
  },Qt::QueuedConnection);
 };a.sourceGuard=[c]{c->source();};a.currentGuard=[c]{c->current();};a.receiptGuard=[c](const QByteArray&o,const QByteArray&e,const KernelWitness&w,int code){c->receipt(o,e,w,code);};return a;
}
ProcessRetireScope nativeProcessRetireScope(QQmlEngine*engine,QObject*provider,QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QVariant&rawLease,const Authority&authority){
 requireOwnerThread();verifyQuickshellProcess();const auto owner=QThread::currentThread();QPointer<QQmlEngine>eg=engine;QPointer<QObject>pg=provider;
 const std::array<QObject*,6>objects={menu,row,popup,process,out,err};std::array<QPointer<QObject>,6>guards;std::array<QPointer<QQmlContext>,6>contexts;std::set<QObject*>distinct;
 if(!engine||!provider||engine->thread()!=owner||provider->thread()!=owner)throw Refused("Actual terminal factory/thread required");
 for(size_t i=0;i<objects.size();++i){auto*o=objects[i];if(!o||o->thread()!=owner||!distinct.insert(o).second)throw Refused("Exact terminal lexical tuple required");guards[i]=o;}
 auto alive=[&]{if(eg.isNull()||pg.isNull()||eg->thread()!=owner||pg->thread()!=owner)throw Refused("Terminal factory retired");for(size_t i=0;i<objects.size();++i)if(guards[i].isNull()||guards[i].data()!=objects[i]||guards[i]->thread()!=owner)throw Refused("Terminal lexical object retired");};
 alive();const auto activation=Registry::shared().scope(engine,provider);alive();
 for(size_t i=0;i<objects.size();++i){alive();contexts[i]=QQmlEngine::contextForObject(objects[i]);if(contexts[i].isNull()||!contexts[i]->isValid()||contexts[i]->thread()!=owner||contexts[i]->engine()!=engine||qmlEngine(objects[i])!=engine)throw Refused("Actual terminal lexical context required");alive();}
 auto sourceGuard=[eg,pg,guards,contexts,activation,authority,owner]{
  requireOwnerThread();if(QThread::currentThread()!=owner||eg.isNull()||pg.isNull())throw Refused("Terminal source owner/factory changed");
  auto tuple=[&]{if(eg.isNull()||pg.isNull()||eg->thread()!=owner||pg->thread()!=owner||Registry::shared().scope(eg.data(),pg.data())!=activation)throw Refused("Terminal source activation changed");for(size_t i=0;i<guards.size();++i){if(guards[i].isNull()||contexts[i].isNull()||guards[i]->thread()!=owner||contexts[i]->thread()!=owner||!contexts[i]->isValid()||contexts[i]->engine()!=eg.data()||QQmlEngine::contextForObject(guards[i].data())!=contexts[i].data()||qmlEngine(guards[i].data())!=eg.data())throw Refused("Terminal source lexical generation/context changed");}};
  tuple();authority.verify();tuple();
 };
 sourceGuard();QVariant leaseValue=rawLease;if(leaseValue.metaType()==QMetaType::fromType<QJSValue>()){const auto value=leaseValue.value<QJSValue>();if(!value.isNumber())throw Refused("Exact numeric terminal lease required");leaseValue=QVariant(value.toNumber());}sourceGuard();uint64_t lease=0;
 if(leaseValue.metaType()==QMetaType::fromType<double>()){const auto n=leaseValue.toDouble();if(!std::isfinite(n)||n<=0||n>=double(SAFE_MAX)||n!=std::floor(n))throw Refused("Exact safe terminal lease required");lease=uint64_t(n);}
 else if(leaseValue.metaType()==QMetaType::fromType<qulonglong>()||leaseValue.metaType()==QMetaType::fromType<uint>()){lease=leaseValue.toULongLong();}
 else if(leaseValue.metaType()==QMetaType::fromType<qlonglong>()||leaseValue.metaType()==QMetaType::fromType<int>()){const auto n=leaseValue.toLongLong();if(n<=0)throw Refused("Positive terminal lease required");lease=uint64_t(n);}
 else throw Refused("Numeric terminal lease type required; Boolean/string refused");
 if(!lease||lease>=SAFE_MAX)throw Refused("Terminal lease representability refused");sourceGuard();ProcessRetireScope scope;scope.engine=engine;scope.provider=provider;scope.objects=objects;scope.lease=lease;scope.sourceGuard=std::move(sourceGuard);return scope;
}
}
