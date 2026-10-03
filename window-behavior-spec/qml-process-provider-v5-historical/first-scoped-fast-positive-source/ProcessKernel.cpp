#include "ProcessRegistry.hpp"
#include "MappingWitness.hpp"
#include <QCryptographicHash>

#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonArray>
#include <QRegularExpression>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <cerrno>
#include <sstream>
#include <set>
#include <filesystem>
namespace Lifetime {
QByteArray digest(const QByteArray&raw){return QCryptographicHash::hash(raw,QCryptographicHash::Sha256).toHex();}
namespace {thread_local std::chrono::steady_clock::time_point readDeadline=std::chrono::steady_clock::time_point::max();struct ReadFD{int fd;~ReadFD(){if(fd>=0)close(fd);}};}
void setKernelDeadline(std::chrono::steady_clock::time_point value){readDeadline=value;}
void checkKernelBudget(){if(std::chrono::steady_clock::now()>readDeadline)throw Refused("Original absolute kernel observation budget expired");}
QByteArray boundedFile(const QString&name,qint64 cap){checkKernelBudget();ReadFD owned{open(name.toUtf8().constData(),O_RDONLY|O_CLOEXEC)};if(owned.fd<0){const int saved=errno;throw Refused("Actual readonly file unavailable: "+name.toStdString()+" errno="+std::to_string(saved));}QByteArray raw;char buffer[65536];for(;;){checkKernelBudget();auto n=read(owned.fd,buffer,sizeof(buffer));checkKernelBudget();if(n<0){if(errno==EINTR)continue;throw Refused("Actual readonly file read refused");}if(!n)break;if(raw.size()+n>cap)throw Refused("Actual readonly file bound refused");raw.append(buffer,n);}return raw;}
QByteArray guardedRegular(const QString&path,uint32_t mode,uint32_t uid,qint64 cap){
 checkKernelBudget();struct stat before{},opened{},after{},fdAfter{};const auto encoded=path.toUtf8();
 if(QFileInfo(path).canonicalFilePath()!=path||lstat(encoded.constData(),&before)||!S_ISREG(before.st_mode)||(before.st_mode&07777)!=mode||before.st_uid!=uid||before.st_nlink!=1)throw Refused("Exact regular source ownership/mode/path required");
 ReadFD owned{open(encoded.constData(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC)};if(owned.fd<0)throw Refused("Nofollow actual source refused");
 auto same=[](const struct stat&a,const struct stat&b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino&&a.st_mode==b.st_mode&&a.st_uid==b.st_uid&&a.st_nlink==b.st_nlink&&a.st_size==b.st_size&&a.st_mtim.tv_sec==b.st_mtim.tv_sec&&a.st_mtim.tv_nsec==b.st_mtim.tv_nsec;};
 if(fstat(owned.fd,&opened)||!same(before,opened))throw Refused("Opened source identity changed");QByteArray raw;char buffer[65536];for(;;){checkKernelBudget();const auto n=read(owned.fd,buffer,sizeof(buffer));checkKernelBudget();if(n<0){if(errno==EINTR)continue;throw Refused("Actual opened source read refused");}if(!n)break;if(raw.size()+n>cap)throw Refused("Source changed/bound exceeded while read");raw.append(buffer,n);}
 if(fstat(owned.fd,&fdAfter)||!same(before,fdAfter)||lstat(encoded.constData(),&after)||!same(before,after))throw Refused("Source changed/bound exceeded while read");return raw;
}
namespace {
struct JSONScan {
 const QByteArray&raw;qsizetype at=0;int depth=0;
 void space(){while(at<raw.size()&&QByteArray(" \r\n\t").contains(raw[at]))++at;}
 QByteArray string(){const auto start=at;if(raw[at++]!='"')throw Refused("JSON key syntax");while(at<raw.size()){const auto c=raw[at++];if(c=='"')return raw.mid(start,at-start);if(c=='\\'){if(at>=raw.size())throw Refused("JSON escape bound");++at;}}throw Refused("JSON string bound");}
 void value(const QString&field={}){
  space();if(at>=raw.size()||++depth>64)throw Refused("JSON depth/bound");const auto c=raw[at];
  if(c=='{'){++at;space();std::set<QString>keys;if(raw[at]!='}')for(;;){space();const auto key=string();const auto decoded=QJsonDocument::fromJson('['+key+']');if(!decoded.isArray()||!decoded.array()[0].isString()||!keys.insert(decoded.array()[0].toString()).second)throw Refused("Duplicate JSON key refused");space();if(raw[at++]!=':')throw Refused("JSON colon");value(decoded.array()[0].toString());space();if(raw[at]=='}')break;if(raw[at++]!=',')throw Refused("JSON comma");}++at;
  }else if(c=='['){++at;space();if(raw[at]!=']')for(;;){value();space();if(raw[at]==']')break;if(raw[at++]!=',')throw Refused("JSON array comma");}++at;
  }else if(c=='"'){string();}else{const auto start=at;while(at<raw.size()&&!QByteArray(" \r\n\t,]}").contains(raw[at]))++at;const auto token=raw.mid(start,at-start);const std::set<QString>integers={"version","pid","compositorPid","parent","pgid","automaticRetries","nativeWrites","replyBytes"};if(integers.contains(field)&&!QRegularExpression("^(0|[1-9][0-9]*)$").match(QString::fromLatin1(token)).hasMatch())throw Refused("Canonical integer JSON authority field required");}
  --depth;
 }
};
QString proc(int pid,const char*name){return QString("/proc/%1/%2").arg(pid).arg(QString::fromLatin1(name));}
struct ID{int parent,group;QString start;};
ID identity(int pid,QVariantMap*diagnostic=nullptr){
 struct stat s{};const auto selectedStatus=proc(pid,"status");const int rc=stat(selectedStatus.toUtf8().constData(),&s),savedErrno=rc?errno:0;if(diagnostic)diagnostic->insert("statusMetadataBeforeValidation",QVariantMap{{"path",selectedStatus},{"statReturn",rc},{"errno",savedErrno},{"uid",qulonglong(rc?0:s.st_uid)},{"expectedUID",qulonglong(getuid())},{"observedMonotonicNanoseconds",qlonglong(std::chrono::steady_clock::now().time_since_epoch().count())}});if(rc||s.st_uid!=getuid())throw Refused("Actual owned child status required");
 const auto status=boundedFile(proc(pid,"status"));bool uid=false;for(auto line:status.split('\n'))if(line.startsWith("Uid:")){const auto parts=line.mid(4).simplified().split(' ');uid=parts.size()==4;for(const auto&v:parts)uid=uid&&v==QByteArray::number(getuid());}if(!uid)throw Refused("Actual child all UID fields differ");
 const auto raw=boundedFile(proc(pid,"stat"));const auto index=raw.lastIndexOf(')');if(index<0)throw Refused("Actual child stat syntax");const auto fields=raw.mid(index+2).simplified().split(' ');if(fields.size()<20)throw Refused("Actual child stat fields");
 bool a=false,b=false;const auto parent=fields[1].toInt(&a),group=fields[2].toInt(&b);if(!a||!b||parent<=0||group<=0||!QRegularExpression("^[1-9][0-9]*$").match(QString::fromLatin1(fields[19])).hasMatch())throw Refused("Actual child stat integer syntax");return {parent,group,QString::fromLatin1(fields[19])};
}
}
namespace {
QByteArray selectedObserverEnvironment(const KernelExpected&e){const auto raw=boundedFile("/proc/self/environ");std::map<QByteArray,QByteArray>all;for(const auto&part:raw.split('\0')){const auto i=part.indexOf('=');if(i>=0&&!all.emplace(part.left(i),part.mid(i+1)).second)throw Refused("Actual observer duplicate environment key");}QByteArray selected;for(const auto&[key,wanted]:e.observerEnvironment){if(!all.contains(key)||all.at(key)!=wanted)throw Refused("Actual original observer environment differs");selected+=key+'='+wanted+'\0';}return selected;}
void observerExact(const KernelExpected&e){if(e.observerStart.isEmpty())throw Refused("Original observer identity not bound");const auto root=identity(getpid());if(root.start!=e.observerStart||QFileInfo("/proc/self/exe").canonicalFilePath()!=e.observerExecutable||digest(boundedFile("/proc/self/exe",128*1024*1024))!=e.observerSHA256||boundedFile("/proc/self/cmdline")!=e.observerARGV||boundedFile("/proc/self/cgroup")!=e.observerCgroup)throw Refused("Original observer live source identity differs");for(const auto&[name,target]:e.namespaces)if(QString::fromStdString(std::filesystem::read_symlink(("/proc/self/ns/"+name).toStdString()).string())!=target)throw Refused("Original observer namespace differs");selectedObserverEnvironment(e);}
}
QString captureObserverStart(){return identity(getpid()).start;}
void bindObserver(KernelExpected&e){if(e.observerExecutable.isEmpty()||e.observerSHA256.isEmpty()||e.observerARGV.isEmpty()||e.observerCgroup.isEmpty())throw Refused("Complete immutable observer declarations required");observerExact(e);}
QJsonObject strictObject(const QByteArray&raw,qint64 cap){
 if(raw.isEmpty()||raw.size()>cap||!raw.trimmed().startsWith('{'))throw Refused("Strict JSON size");QJsonParseError error;const auto parsed=QJsonDocument::fromJson(raw,&error);if(error.error!=QJsonParseError::NoError||!parsed.isObject())throw Refused("Strict JSON object syntax");JSONScan scan{raw};scan.value();scan.space();if(scan.at!=raw.size())throw Refused("Strict JSON trailing data");return parsed.object();
}
QVariantMap KernelWitness::value()const{return {{"pid",pid},{"start",start},{"parent",parent},{"group",group},{"executable",executable},{"executableSHA256",QString::fromLatin1(executableSHA256)},{"argvSHA256",QString::fromLatin1(digest(argv))},{"cgroupSHA256",QString::fromLatin1(digest(cgroup))},{"selectedEnvironmentSHA256",QString::fromLatin1(digest(environment))},{"mapsSHA256",QString::fromLatin1(digest(maps))}};}
KernelWitness captureStartedRoot(int pid,const KernelExpected&expected,QVariantMap*evidence){const auto before=identity(pid);if(before.parent!=expected.parent||before.group!=expected.group)throw Refused("Actual Started root parent/group differs");KernelWitness r;r.pid=pid;r.start=before.start;r.parent=before.parent;r.group=before.group;if(evidence)*evidence={{"rawStat",QString::fromLatin1(boundedFile(proc(pid,"stat")))},{"rawStatus",QString::fromLatin1(boundedFile(proc(pid,"status")))},{"identity",r.value()}};const auto after=identity(pid);if(after.start!=r.start||after.parent!=r.parent||after.group!=r.group)throw Refused("Actual Started root lifetime changed");return r;}
KernelWitness readKernel(int pid,const KernelExpected&expected,QVariantMap*evidence){
 const auto observerBegin=std::chrono::steady_clock::now();observerExact(expected);if(!expected.aliases)throw Refused("Pre-arm complete frozen reference index required");if(evidence)evidence->insert("observerBeforeMicroseconds",qlonglong(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-observerBegin).count()));if(pid<=0)throw Refused("Exact positive child PID required");const auto before=identity(pid,evidence);KernelWitness r;r.pid=pid;r.start=before.start;r.parent=before.parent;r.group=before.group;
 if((!expected.childStart.isEmpty()&&r.start!=expected.childStart)||r.parent!=expected.parent||r.group!=expected.group)throw Refused("Actual owned parent/group differs");
 r.executable=QFileInfo(proc(pid,"exe")).canonicalFilePath();if(r.executable!=expected.executable)throw Refused("Actual final child executable differs");r.executableSHA256=digest(boundedFile(proc(pid,"exe"),128*1024*1024));if(r.executableSHA256!=expected.executableSHA256)throw Refused("Actual final child executable source differs");
 r.argv=boundedFile(proc(pid,"cmdline"));r.cgroup=boundedFile(proc(pid,"cgroup"));if(r.argv!=expected.argv||r.cgroup!=expected.cgroup)throw Refused("Actual child final argv/cgroup differs");
 for(const auto&[name,target]:expected.namespaces){const auto actual=QString::fromStdString(std::filesystem::read_symlink(proc(pid,("ns/"+name).toUtf8().constData()).toStdString()).string());if(actual!=target||actual.isEmpty())throw Refused("Actual child namespace differs");r.namespaces[name]=actual;}
 const auto env=boundedFile(proc(pid,"environ"));std::map<QByteArray,QByteArray>values;for(const auto&part:env.split('\0')){const auto i=part.indexOf('=');if(i>=0){const auto key=part.left(i);if(!values.emplace(key,part.mid(i+1)).second)throw Refused("Actual child duplicate environment key");}}
 for(const auto&[key,wanted]:expected.environment){const auto found=values.find(key);if(found==values.end()||found->second!=wanted)throw Refused("Actual child selected environment differs");r.environment+=key+'='+found->second+'\0';}
 for(const auto*key:{"LD_PRELOAD","LD_AUDIT","PYTHONPATH","PYTHONHOME","DISPLAY","WAYLAND_SOCKET","SESSION_MANAGER","AT_SPI_BUS_ADDRESS"})if(values.contains(key)&&!values[key].isEmpty())throw Refused("Foreign child inherited handle/import selector");
 r.maps=boundedFile(proc(pid,"maps"),2*1024*1024);if(evidence){evidence->insert("identity",r.value());evidence->insert("rawMaps",QString::fromLatin1(r.maps));}
 for(const auto&line:r.maps.split('\n')){if(line.isEmpty())continue;std::istringstream stream(line.toStdString());std::string range,perms,offset,dev,inode,path;stream>>range>>perms>>offset>>dev>>inode;std::getline(stream,path);const auto index=path.find_first_not_of(' ');if(index==std::string::npos){if(perms.find('x')!=std::string::npos)throw Refused("Anonymous executable child mapping refused");continue;}path.erase(0,index);
  if(path=="[vdso]"||path=="[vsyscall]")continue;if(!path.starts_with('/')){if(perms.find('x')!=std::string::npos)throw Refused("Unknown executable child mapping");continue;}
  if(path.ends_with(" (deleted)"))throw Refused("Deleted child disk mapping refused");const auto name=QString::fromStdString(path);const auto source=expected.code.find(name);if(source==expected.code.end())throw Refused("Missing frozen child mapped code/data source");
  struct stat s{};if(lstat(path.c_str(),&s)||!S_ISREG(s.st_mode)||(s.st_mode&07777)!=source->second.second)throw Refused("Child mapped source mode differs");
  const auto colon=dev.find(':');
  if(colon==std::string::npos)throw Refused("Child maps device syntax differs");

 }
 std::exception_ptr mappingChange;try{verifyOwnedMappings(pid,r.maps,expected.code,*expected.aliases,evidence);}catch(const MappingChanged&){mappingChange=std::current_exception();}
 const auto envAfter=boundedFile(proc(pid,"environ"));std::map<QByteArray,QByteArray>valuesAfter;for(const auto&part:envAfter.split('\0')){const auto i=part.indexOf('=');if(i>=0&&!valuesAfter.emplace(part.left(i),part.mid(i+1)).second)throw Refused("Actual child duplicate environment key after read");}for(const auto&[key,wanted]:expected.environment)if(!valuesAfter.contains(key)||valuesAfter.at(key)!=wanted)throw Refused("Actual child selected environment changed after read");for(const auto*key:{"LD_PRELOAD","LD_AUDIT","PYTHONPATH","PYTHONHOME","DISPLAY","WAYLAND_SOCKET","SESSION_MANAGER","AT_SPI_BUS_ADDRESS"})if(valuesAfter.contains(key)&&!valuesAfter.at(key).isEmpty())throw Refused("Foreign child inherited selector after read");
 for(const auto&[name,target]:expected.namespaces)if(QString::fromStdString(std::filesystem::read_symlink(proc(pid,("ns/"+name).toUtf8().constData()).toStdString()).string())!=target)throw Refused("Actual child namespace changed after read");
 if(digest(boundedFile(proc(pid,"exe"),128*1024*1024))!=expected.executableSHA256)throw Refused("Actual child final executable bytes changed after read");
 const auto after=identity(pid);if(after.start!=r.start||after.parent!=r.parent||after.group!=r.group||QFileInfo(proc(pid,"exe")).canonicalFilePath()!=r.executable||boundedFile(proc(pid,"cmdline"))!=r.argv||boundedFile(proc(pid,"cgroup"))!=r.cgroup)throw Refused("Actual child lifetime changed during read");observerExact(expected);checkKernelBudget();if(mappingChange)std::rethrow_exception(mappingChange);return r;
}
bool kernelGone(const KernelWitness&r){struct stat s{};const auto name=QString("/proc/%1").arg(r.pid).toUtf8();if(stat(name.constData(),&s)<0){if(errno==ENOENT)return true;throw Refused("Actual registered child absence query refused");}const auto actual=identity(r.pid);if(actual.start!=r.start)throw Refused("Registered child PID reused");return false;}
}
