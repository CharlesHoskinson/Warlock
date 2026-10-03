#include <QCoreApplication>
#include <QCryptographicHash>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMetaObject>
#include <QPluginLoader>
#include <QQmlEngine>
#include <QQmlExtensionPlugin>
#include <QPointer>
#include <QQuickItem>
#include <sys/stat.h>
#include <unistd.h>
#include <iostream>
#include <stdexcept>
static int checks=0;
void require(bool value,const char*name){if(!value)throw std::runtime_error(name);++checks;}
QByteArray read(const QString&p){QFile f(p);if(!f.open(QIODevice::ReadOnly))throw std::runtime_error("actual readonly fixture source");return f.readAll();}
QByteArray hash(const QByteArray&b){return QCryptographicHash::hash(b,QCryptographicHash::Sha256).toHex();}
QByteArray start(){const auto raw=read("/proc/self/stat");return raw.mid(raw.lastIndexOf(')')+2).simplified().split(' ')[19];}
void config(const QString&image,const QString&path){
 struct stat s{};require(lstat(image.toUtf8().constData(),&s)==0,"actual image stat");
 const auto exe=QFileInfo("/proc/self/exe").canonicalFilePath();
 const QList<QByteArray>lines={"qml-object-lifetime-config-v1",QByteArray("pid=")+QByteArray::number(getpid()),QByteArray("start=")+start(),QByteArray("executable=")+exe.toUtf8(),QByteArray("executableSHA256=")+hash(read(exe)),QByteArray("argvSHA256=")+hash(read("/proc/self/cmdline")),QByteArray("cgroupSHA256=")+hash(read("/proc/self/cgroup")),QByteArray("runtime=")+qgetenv("XDG_RUNTIME_DIR"),QByteArray("home=")+qgetenv("HOME"),QByteArray("image=")+image.toUtf8(),QByteArray("imageSHA256=")+hash(read(image)),QByteArray("imageMode=")+QByteArray::number(s.st_mode&07777),QByteArray("imageDevice=")+QByteArray::number(qulonglong(s.st_dev)),QByteArray("imageInode=")+QByteArray::number(qulonglong(s.st_ino))};
 QByteArray raw;for(const auto&line:lines)raw+=line+'\n';QFile f(path);require(f.open(QIODevice::WriteOnly|QIODevice::NewOnly),"fresh config");require(f.write(raw)==raw.size()&&f.flush(),"full fixture config write");f.setPermissions(QFileDevice::ReadOwner|QFileDevice::WriteOwner);f.close();
}
QVariantMap scope(QObject*p){QVariantMap row;require(QMetaObject::invokeMethod(p,"engineScope",Qt::DirectConnection,Q_RETURN_ARG(QVariantMap,row)),"actual registered scope method");return row;}
qulonglong number(const QVariantMap&r,const char*k){require(r.contains(k),"actual numeric field");bool ok=false;const auto n=r[k].toULongLong(&ok);require(ok&&n>0&&n<=(qulonglong{1}<<53)-1,"actual safe positive field");return n;}
bool mapped(const QString&image){const auto raw=read("/proc/self/maps");return raw.contains(image.toUtf8());}
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);
 try{
  require(argc==3,"explicit image/mode");const QString image=QFileInfo(QString::fromLocal8Bit(argv[1])).canonicalFilePath();const QByteArray mode=argv[2];const auto path=QString::fromLocal8Bit(qgetenv("WINDOW_OBJECT_LIFETIME_CONFIG"));config(image,path);
  QPluginLoader loader(image);loader.setLoadHints(QLibrary::ResolveAllSymbolsHint);auto*plugin=qobject_cast<QQmlExtensionPlugin*>(loader.instance());require(plugin!=nullptr,loader.errorString().toUtf8().constData());plugin->registerTypes("WindowObjectLifetimeV1");
  auto engine=std::make_unique<QQmlEngine>();auto*provider=engine->singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");require(provider!=nullptr,"actual Qt singleton factory");
  const auto first=scope(provider);require(!first.contains("error"),QJsonDocument::fromVariant(first).toJson().constData());const auto eg=number(first,"engineGeneration"),ep=number(first,"engineEpoch"),pg=number(first,"providerGeneration");
  require(first["schema"].toString()=="qml-engine-metadata-v1"&&!first.contains("visualDescendant")&&!first.contains("windowBound"),"metadata cannot claim widget authority");
  if(mode=="lifecycle"){
   require(scope(provider)==first,"repeated query preserves generations");QPointer<QObject>old=provider;engine->clearSingletons();auto*replacement=engine->singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");require(replacement&&replacement!=old.data(),"actual singleton recreation");
   if(old){const auto retired=scope(old.data());require(retired.contains("error"),"old surviving singleton refuses");}
   const auto newScope=scope(replacement);require(!newScope.contains("error"),"fresh actual singleton scope");require(number(newScope,"engineGeneration")==eg&&number(newScope,"engineEpoch")>ep&&number(newScope,"providerGeneration")>pg,"actual factory recreation changes activation not engine lifetime");
   const auto lastEpoch=number(newScope,"engineEpoch");engine.reset();require(old.isNull(),"actual old singleton retired with engine");
   const bool unloaded=loader.unload();require(unloaded,"actual QPluginLoader unload returns normally");require(mapped(image),"NODELETE retains actual executable image after Qt unload");
   QPluginLoader reopened(image);reopened.setLoadHints(QLibrary::ResolveAllSymbolsHint);auto*again=qobject_cast<QQmlExtensionPlugin*>(reopened.instance());require(again!=nullptr,"actual plugin reopen");again->registerTypes("WindowObjectLifetimeV1");
   auto nextEngine=std::make_unique<QQmlEngine>();auto*next=nextEngine->singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");const auto continued=scope(next);require(!continued.contains("error"),"actual reopened scope");require(number(continued,"engineGeneration")>eg&&number(continued,"engineEpoch")>lastEpoch&&number(continued,"providerGeneration")>number(newScope,"providerGeneration"),"process monotonic registry survives actual unload/reopen");nextEngine.reset();require(reopened.unload(),"actual reopened normal unload");require(mapped(image),"retained image persists until process exit");
  }else if(mode=="image-mode"){
   struct stat s{};require(lstat(image.toUtf8().constData(),&s)==0,"fault copy stat");require(chmod(image.toUtf8().constData(),(s.st_mode&07777)^0200)==0,"actual copied image mode change");require(scope(provider).contains("error"),"changed actual image refuses");
   require(chmod(image.toUtf8().constData(),s.st_mode&07777)==0,"restore owned CPU copy mode");engine->clearSingletons();auto*fresh=engine->singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");require(scope(fresh).contains("error"),"new singleton cannot reset source-faulted registry");
  }else if(mode=="config-mode"){
   require(chmod(path.toUtf8().constData(),0644)==0,"actual config permission fault");require(scope(provider).contains("error"),"wrong full config mode refuses");
  }else if(mode=="config-duplicate"){
   QFile f(path);require(f.open(QIODevice::Append),"actual duplicate field write");require(f.write("pid=1\n")==6,"actual duplicate field bytes");f.close();require(scope(provider).contains("error"),"extra duplicate config field refuses");
  }else if(mode=="config-replacement"){
   const auto raw=read(path);require(QFile::rename(path,path+".old"),"actual config inode retirement");QFile f(path);require(f.open(QIODevice::WriteOnly|QIODevice::NewOnly)&&f.write(raw)==raw.size(),"actual byte-identical config replacement");f.setPermissions(QFileDevice::ReadOwner|QFileDevice::WriteOwner);f.close();require(scope(provider).contains("error"),"byte-identical new config inode refuses");
  }else if(mode=="fake-quickshell"){
   QObject fake;QVariantMap row;require(QMetaObject::invokeMethod(provider,"observe",Qt::DirectConnection,Q_RETURN_ARG(QVariantMap,row),Q_ARG(QQuickItem*,nullptr),Q_ARG(QQuickItem*,nullptr),Q_ARG(QObject*,&fake)),"actual observed API method");require(row.contains("error")&&row["error"].toString().contains("frozen Quickshell"),"CPU executable cannot impersonate real Quickshell widget authority");
  }else throw std::runtime_error("unregistered CPU mode");
  std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"mode",QString::fromLatin1(mode)},{"providerLoadedInCPU",true},{"GUI",false},{"nativeWidgetAccepted",false}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
