#include "Lifetime.hpp"
#include "KnownQuickshell.hpp"
#include <QCoreApplication>
#include <QCryptographicHash>
#include <QDir>
#include <QPluginLoader>
#include <QQmlExtensionPlugin>
#include <QFile>
#include <QFileInfo>
#include <QRegularExpression>
#include <dlfcn.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/resource.h>
#include <fstream>
#include <optional>
#include <sstream>
#include <mutex>
#include <set>

namespace Lifetime {
namespace {
const unsigned char imageMarker=0;
std::optional<ImageSeal> pinned;
void*retainedHandle=nullptr;
std::mutex imageMutex;
std::mutex configMutex;
std::optional<Authority>configAnchor;
QByteArray readBounded(const QString&path,qint64 cap){QFile f(path);if(!f.open(QIODevice::ReadOnly))throw Refused("Readonly source unavailable");const auto raw=f.read(cap+1);if(raw.size()>cap)throw Refused("Readonly source bound exceeded");return raw;}
QByteArray hash(const QByteArray&raw){return QCryptographicHash::hash(raw,QCryptographicHash::Sha256).toHex();}
bool pathSafe(const QString&p){return p.startsWith('/')&&!p.contains(QRegularExpression("[\\s\\\\]"))&&QFileInfo(p).canonicalFilePath()==p;}
struct stat source(const QString&path){struct stat s{};if(!pathSafe(path)||lstat(path.toUtf8().constData(),&s)||!S_ISREG(s.st_mode)||s.st_nlink!=1)throw Refused("Exact canonical regular source required");return s;}
QByteArray sourceHash(const QString&path){
 const auto before=source(path);int fd=open(path.toUtf8().constData(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)throw Refused("Readonly nofollow source refused");
 QFile f;if(!f.open(fd,QIODevice::ReadOnly,QFileDevice::AutoCloseHandle)){close(fd);throw Refused("Readonly opened source refused");}
 struct stat opened{};if(fstat(fd,&opened)||opened.st_dev!=before.st_dev||opened.st_ino!=before.st_ino)throw Refused("Opened source inode changed");
 const auto raw=f.read(64*1024*1024+1);if(raw.size()>64*1024*1024||f.error()!=QFileDevice::NoError)throw Refused("Source hash bound/read failed");
 const auto after=source(path);
 if(before.st_dev!=after.st_dev||before.st_ino!=after.st_ino||before.st_size!=after.st_size||before.st_mtim.tv_sec!=after.st_mtim.tv_sec||before.st_mtim.tv_nsec!=after.st_mtim.tv_nsec||before.st_mode!=after.st_mode)throw Refused("Source changed while hashing");
 return hash(raw);
}
void directory(const QString&p){struct stat s{};if(!pathSafe(p)||lstat(p.toUtf8().constData(),&s)||!S_ISDIR(s.st_mode)||s.st_uid!=getuid()||(s.st_mode&07777)!=0700)throw Refused("Exact owned canonical0700 directory required");}
void privatePath(const QString&p,const QString&runtime){if(!pathSafe(p)||!p.startsWith(runtime+'/'))throw Refused("Selected private path required");for(QString parent=QFileInfo(p).absolutePath();parent!=runtime;parent=QFileInfo(parent).absolutePath()){directory(parent);if(!parent.startsWith(runtime+'/'))throw Refused("Foreign parent path");}directory(runtime);}
uint64_t decimal(const QByteArray&v){if(!QRegularExpression("^(0|[1-9][0-9]*)$").match(QString::fromLatin1(v)).hasMatch())throw Refused("Canonical integer required");bool ok=false;auto n=v.toULongLong(&ok);if(!ok)throw Refused("Integer range refused");return n;}
QByteArray digestField(const QByteArray&v){if(!QRegularExpression("^[0-9a-f]{64}$").match(QString::fromLatin1(v)).hasMatch())throw Refused("Exact source digest required");return v;}
QByteArray selected(const char*key){const char*v=getenv(key);return v?QByteArray(v):QByteArray();}
}
QString processStart(){const auto raw=readBounded("/proc/self/stat",65536);const auto at=raw.lastIndexOf(')');if(at<0)throw Refused("Actual process identity unavailable");const auto values=raw.mid(at+2).simplified().split(' ');if(values.size()<20)throw Refused("Actual process fields incomplete");const auto n=decimal(values[19]);if(!n)throw Refused("Actual process start missing");return QString::number(n);}
ImageSeal actualImage(){
 Dl_info info{};if(!dladdr(&imageMarker,&info)||!info.dli_fname)throw Refused("Actual provider image unavailable");const QString path=QFileInfo(QString::fromLocal8Bit(info.dli_fname)).canonicalFilePath();const auto s=source(path);return {path,sourceHash(path),uint64_t(s.st_dev),uint64_t(s.st_ino),uint32_t(s.st_mode&07777)};
}
void verifyImage(const ImageSeal&expected){
 const auto actual=actualImage();if(actual!=expected)throw Refused("Provider image source changed");
 const auto imageSize=source(expected.path).st_size;std::set<QString>checkedCopies;
 bool executable=false;std::ifstream f("/proc/self/maps");std::string line;if(!f)throw Refused("Actual provider maps unavailable");
 while(std::getline(f,line)){
  std::istringstream stream(line);std::string range,perms,offset,device,inode,path;stream>>range>>perms>>offset>>device>>inode;std::getline(stream,path);const auto at=path.find_first_not_of(' ');if(at==std::string::npos)continue;path.erase(0,at);
  unsigned long long node=0;try{node=std::stoull(inode);}catch(...){throw Refused("Malformed actual map inode");}
  const auto colon=device.find(':');if(colon==std::string::npos)throw Refused("Malformed actual map device");
  unsigned long long maj=0,min=0;try{maj=std::stoull(device.substr(0,colon),nullptr,16);min=std::stoull(device.substr(colon+1),nullptr,16);}catch(...){throw Refused("Malformed actual map device");}
  const bool same=node==expected.inode&&maj==major(expected.device)&&min==minor(expected.device);
  if(same&&path!=expected.path.toStdString())throw Refused("Provider image mapped through alias");
  if(!same&&perms.find('x')!=std::string::npos&&path.starts_with('/')&&!path.ends_with(" (deleted)")){
   const auto candidate=QString::fromStdString(path);
   if(checkedCopies.insert(candidate).second){
    struct stat s{};if(lstat(path.c_str(),&s))throw Refused("Mapped executable source stat unavailable");
    if(S_ISREG(s.st_mode)){
     if(s.st_size==imageSize&&sourceHash(candidate)==expected.sha)throw Refused("Duplicate provider executable image mapped");
     // Public Qt metadata query reads the already-mapped code file; it does not
     // load a replacement library or instantiate its plugin. Also reject an
     // older differently hashed provider bearing the same actual plugin class.
     QPluginLoader metadata(candidate);const auto row=metadata.metaData();
     if(row.value("className").toString()=="ObjectLifetimePlugin"&&row.value("IID").toString()==QQmlExtensionInterface_iid)throw Refused("Different provider image with same plugin class mapped");
    }
   }
  }
  if(path==expected.path.toStdString()){
   if(!same)throw Refused("Provider mapped inode differs");
   if(perms.find('x')!=std::string::npos)executable=true;
  }
 }
 if(!f.eof()||!executable)throw Refused("Exact executable provider mapping unavailable");
}
void pinImage(const ImageSeal&seal){
 std::lock_guard lock(imageMutex);if(pinned){if(*pinned!=seal)throw Refused("Provider pinning source changed");verifyImage(seal);return;}
 verifyImage(seal);void*handle=dlopen(seal.path.toUtf8().constData(),RTLD_NOW|RTLD_NOLOAD|RTLD_NODELETE);
 if(!handle)throw Refused("Actual already-loaded NODELETE pin failed");
 try{verifyImage(seal);}catch(...){dlclose(handle);throw;}
 retainedHandle=handle;pinned=seal;
}
void verifyQuickshellProcess(){
 struct stat running{};if(stat("/proc/self/exe",&running))throw Refused("Actual process executable inode unavailable");
 const auto exe=QFileInfo("/proc/self/exe").canonicalFilePath();const auto named=source(exe);
 if(uint64_t(running.st_dev)!=KnownQuickshell::device||uint64_t(running.st_ino)!=KnownQuickshell::inode||uint32_t(running.st_mode&07777)!=KnownQuickshell::mode||running.st_dev!=named.st_dev||running.st_ino!=named.st_ino||exe!=QString::fromUtf8(KnownQuickshell::path)||sourceHash(exe)!=KnownQuickshell::sha)throw Refused("Actual frozen Quickshell process required for widget authority");
}
Authority authority(){
 if(QByteArray(qVersion())!=QT_VERSION_STR)throw Refused("Installed Qt runtime ABI version differs");
 const auto path=QString::fromLocal8Bit(selected("WINDOW_OBJECT_LIFETIME_CONFIG"));const auto runtime=QString::fromLocal8Bit(selected("XDG_RUNTIME_DIR"));const auto home=QString::fromLocal8Bit(selected("HOME"));
 const auto pattern=QString("^/run/user/%1/wqa/[0-9a-f]{4}$").arg(getuid());if(!QRegularExpression(pattern).match(runtime).hasMatch())throw Refused("Exact private runtime required");directory(runtime);directory(home);if(!home.startsWith(runtime+'/'))throw Refused("Private HOME required");privatePath(path,runtime);if(!path.startsWith(home+'/'))throw Refused("Private HOME config required");
 const auto before=source(path);if(before.st_uid!=getuid()||(before.st_mode&07777)!=0600)throw Refused("Exact owned600 config required");
 int configFD=open(path.toUtf8().constData(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(configFD<0)throw Refused("Nofollow configuration unavailable");
 QFile configFile;if(!configFile.open(configFD,QIODevice::ReadOnly,QFileDevice::AutoCloseHandle)){close(configFD);throw Refused("Opened configuration unavailable");}
 struct stat opened{};if(fstat(configFD,&opened)||opened.st_dev!=before.st_dev||opened.st_ino!=before.st_ino||opened.st_mode!=before.st_mode||opened.st_uid!=before.st_uid||opened.st_nlink!=before.st_nlink||opened.st_size!=before.st_size||opened.st_mtim.tv_sec!=before.st_mtim.tv_sec||opened.st_mtim.tv_nsec!=before.st_mtim.tv_nsec)throw Refused("Configuration opened inode/mode differs");
 const auto raw=configFile.read(65537);if(raw.size()>65536||configFile.error()!=QFileDevice::NoError)throw Refused("Configuration read bound failed");if(raw.contains('\r')||!raw.endsWith('\n'))throw Refused("Exact config line protocol required");const auto lines=raw.split('\n');
 const QList<QByteArray>keys={"pid","start","executable","executableSHA256","argvSHA256","cgroupSHA256","runtime","home","image","imageSHA256","imageMode","imageDevice","imageInode"};
 if(lines.size()!=keys.size()+2||lines[0]!="qml-object-lifetime-config-v1"||!lines.back().isEmpty())throw Refused("Exact config schema/field count required");
 std::map<QByteArray,QByteArray>fields;for(qsizetype i=0;i<keys.size();++i){const auto prefix=keys[i]+'=';if(!lines[i+1].startsWith(prefix))throw Refused("Exact unique ordered config field required");fields.emplace(keys[i],lines[i+1].mid(prefix.size()));}
 const auto pid=decimal(fields["pid"]);if(pid!=uint64_t(getpid())||pid>2147483647||QString::fromLatin1(fields["start"])!=processStart())throw Refused("Exact actual process PID/start required");
 if(fields["runtime"]!=runtime.toUtf8()||fields["home"]!=home.toUtf8())throw Refused("Actual selected environment differs");
 const auto exe=QFileInfo("/proc/self/exe").canonicalFilePath();if(exe!=QString::fromUtf8(fields["executable"])||sourceHash(exe)!=digestField(fields["executableSHA256"])||hash(readBounded("/proc/self/cmdline",65536))!=digestField(fields["argvSHA256"]))throw Refused("Actual final executable/argv differs");
 const auto group=readBounded("/proc/self/cgroup",65536);if(!group.contains("/qa-harness.slice/qa-harness-")||hash(group)!=digestField(fields["cgroupSHA256"]))throw Refused("Actual private QA process scope differs");
 struct rlimit limit{};if(getrlimit(RLIMIT_CORE,&limit)||limit.rlim_cur!=1||limit.rlim_max!=1)throw Refused("Exact private core limit required");
 for(const char*key:{"LD_PRELOAD","LD_AUDIT","DISPLAY","WAYLAND_SOCKET"})if(!selected(key).isEmpty())throw Refused("Foreign inherited loader/display handles refused");
 ImageSeal seal{QString::fromUtf8(fields["image"]),digestField(fields["imageSHA256"]),decimal(fields["imageDevice"]),decimal(fields["imageInode"]),uint32_t(decimal(fields["imageMode"]))};
 if(decimal(fields["imageMode"])>07777)throw Refused("Exact image mode range required");
 pinImage(seal);
 const auto after=source(path);if(before.st_dev!=after.st_dev||before.st_ino!=after.st_ino||before.st_uid!=after.st_uid||before.st_mode!=after.st_mode||before.st_nlink!=after.st_nlink||before.st_size!=after.st_size||before.st_mtim.tv_sec!=after.st_mtim.tv_sec||before.st_mtim.tv_nsec!=after.st_mtim.tv_nsec||hash(readBounded(path,65536))!=hash(raw)||QString::fromLatin1(fields["start"])!=processStart())throw Refused("Source/process changed during config observation");
 Authority result{seal,path,hash(raw),uint64_t(before.st_dev),uint64_t(before.st_ino),int(pid),QString::fromLatin1(fields["start"])};
 {std::lock_guard lock(configMutex);if(configAnchor){if(result.config!=configAnchor->config||result.configSHA!=configAnchor->configSHA||result.configDevice!=configAnchor->configDevice||result.configInode!=configAnchor->configInode||result.pid!=configAnchor->pid||result.start!=configAnchor->start||result.image!=configAnchor->image)throw Refused("Selected source/config/process anchor changed");}else configAnchor=result;}
 return result;
}
void Authority::verify()const{const auto current=authority();if(current.image!=image||current.config!=config||current.configSHA!=configSHA||current.configDevice!=configDevice||current.configInode!=configInode||current.pid!=pid||current.start!=start)throw Refused("Actual process/image/config changed");}
}
