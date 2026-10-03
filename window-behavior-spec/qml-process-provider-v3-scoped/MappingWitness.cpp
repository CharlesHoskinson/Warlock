#include "MappingWitness.hpp"
#include "ProcessRegistry.hpp"
#include <QRegularExpression>
#include <fcntl.h>
#include <linux/magic.h>
#include <sys/stat.h>
#include <unistd.h>
namespace Lifetime {
namespace {
void require(bool value,const char*why){if(!value)throw Refused(why);}
qulonglong number(const QVariantMap&m,const char*key){const auto v=m.value(QString::fromLatin1(key));const auto t=v.metaType().id();require(t==QMetaType::ULongLong||t==QMetaType::UInt||t==QMetaType::LongLong||t==QMetaType::Int,"Mapping metadata exact integer required");bool ok=false;const auto n=v.toULongLong(&ok);require(ok&&!(t==QMetaType::LongLong&&v.toLongLong()<0)&&!(t==QMetaType::Int&&v.toInt()<0),"Mapping metadata nonnegative integer required");return n;}
bool boolean(const QVariantMap&m,const char*key){const auto v=m.value(QString::fromLatin1(key));require(v.metaType()==QMetaType::fromType<bool>(),"Mapping metadata exact boolean required");return v.toBool();}
QString string(const QVariantMap&m,const char*key){const auto v=m.value(QString::fromLatin1(key));require(v.metaType()==QMetaType::fromType<QString>(),"Mapping metadata exact string required");return v.toString();}
qulonglong token(const QString&s,int base=10){require(QRegularExpression(base==16?"^[0-9a-f]+$":"^(0|[1-9][0-9]*)$").match(s).hasMatch(),"Mapping numeric syntax refused");bool ok=false;const auto n=s.toULongLong(&ok,base);require(ok,"Mapping numeric range refused");return n;}
struct Mount{qulonglong id,major,minor,subvol;QString filesystem;};
Mount mount(const QString&line){require(!line.contains('\n')&&!line.contains('\r'),"Mount line syntax refused");const auto halves=line.split(" - ");require(halves.size()==2,"Mount line separator ambiguous");const auto before=halves[0].split(' '),after=halves[1].split(' ');require(before.size()>=6&&after.size()==3,"Mount line fields refused");const auto dev=before[2].split(':');require(dev.size()==2,"Mount device syntax refused");Mount r{token(before[0]),token(dev[0]),token(dev[1]),0,after[0]};require(r.id>0,"Mount ID positive required");int count=0;for(const auto&option:after[2].split(','))if(option.startsWith("subvolid=")){++count;r.subvol=token(option.mid(9));}if(r.filesystem=="btrfs")require(count==1&&r.subvol>0,"Btrfs exact subvolume option required");return r;}
QVariantMap fdinfo(const QString&raw){QVariantMap r;for(const auto&line:raw.split('\n')){if(line.isEmpty())continue;const auto i=line.indexOf(':');require(i>0,"FDInfo syntax refused");const auto key=line.left(i),value=line.mid(i+1).trimmed();require(!r.contains(key),"Duplicate FDInfo field refused");r[key]=value;}return r;}
void statxMatches(const QVariantMap&x,const QVariantMap&s){require(number(x,"errno")==0,"FD statx unavailable");const auto mask=number(x,"mask");require((mask&STATX_BASIC_STATS)==STATX_BASIC_STATS&&(mask&STATX_MNT_ID),"FD statx mandatory result fields unavailable");for(const auto*key:{"major","minor","inode","mode","uid","gid","nlink","size","mtimeSeconds","mtimeNanoseconds"})require(number(x,key)==number(s,key),"FD statx and fstat disagree");}
}
void verifyFrozenMappingSource(const QVariantMap&r,const QByteArray&expectedHash,uint32_t fullMode){
 require(boolean(r,"diagnosticCompleted")&&boolean(r,"identityUnchanged")&&boolean(r,"sourceFDUnchanged")&&boolean(r,"namedUnchanged")&&boolean(r,"selectedMountUnchanged"),"Owned mapping before/after observation changed/incomplete");
 require(r.value("identityBefore")==r.value("identityAfter"),"Owned mapping identity snapshots differ");
 const auto row=string(r,"rawLine"),path=string(r,"path");const auto parsed=QRegularExpression("^([0-9a-f]+)-([0-9a-f]+) ([r-][w-][x-][ps]) ([0-9a-f]+) ([0-9a-f]+):([0-9a-f]+) ([1-9][0-9]*) +(/[^\\n\\r]+)$").match(row);require(parsed.hasMatch()&&parsed.captured(8)==path&&!path.endsWith(" (deleted)"),"Exact selected raw mapping syntax/path required");const auto start=token(parsed.captured(1),16),end=token(parsed.captured(2),16);require(start<end,"Selected VMA bounds refused");token(parsed.captured(4),16);const auto mapMajor=token(parsed.captured(5),16),mapMinor=token(parsed.captured(6),16),mapInode=token(parsed.captured(7));
 const auto before=r.value("fdBefore").toMap(),after=r.value("fdAfter").toMap();require(before==after,"Actual source FD changed");const auto s=before.value("stat").toMap(),x=before.value("statx").toMap();require(r.value("namedBefore").toMap()==s&&r.value("namedAfter").toMap()==s,"Named and opened source stamps disagree");require((number(s,"mode")&S_IFMT)==S_IFREG&&(number(s,"mode")&07777)==fullMode&&number(s,"nlink")==1&&number(s,"inode")==mapInode,"Actual mapped source full mode/inode/regular identity differs");statxMatches(x,s);
 require(string(before,"fdTarget")==path,"Actual kernel mapping/FD paths disagree");require(string(r,"selectedBackingSHA256").toLatin1()==expectedHash,"Frozen mapped disk source bytes differ");
 const auto flags=number(before,"descriptorFlags"),fdflags=number(before,"descriptorFDFlags");require((flags&O_ACCMODE)==O_RDONLY&&!(flags&O_PATH)&&(flags&O_NOFOLLOW)&&fdflags==FD_CLOEXEC,"Actual source descriptor access flags refused");const auto info=fdinfo(string(before,"rawFDInfo"));require(info.contains("flags")&&info.contains("ino")&&info.contains("mnt_id"),"Actual descriptor FDInfo fields unavailable");const auto infoFlags=string(info,"flags");require(QRegularExpression("^[0-7]+$").match(infoFlags).hasMatch(),"FDInfo flag syntax refused");bool flagOK=false;const auto fullFlags=infoFlags.toULongLong(&flagOK,8);require(flagOK&&fullFlags==(flags|O_CLOEXEC)&&token(string(info,"ino"))==mapInode&&token(string(info,"mnt_id"))==number(x,"mountID"),"Actual descriptor flags/inode/mount identity differs");
 const auto ns=string(r,"observerMountNamespace");require(ns==string(r,"childMountNamespace")&&r.value("identityBefore").toMap().value("namespaces").toMap().value("mnt").toString()==ns,"Exact consumer/observer mount namespace differs");
 const auto line=string(r,"observerSelectedMount");require(line==string(r,"childSelectedMount")&&line==string(r,"observerSelectedMountAfter")&&line==string(r,"childSelectedMountAfter"),"Selected actual mount line changed/disagrees");const auto m=mount(line);require(m.id==number(x,"mountID"),"Selected descriptor mount ID differs");
 if(number(before,"filesystemType")==BTRFS_SUPER_MAGIC){require(m.filesystem=="btrfs"&&(number(x,"mask")&STATX_SUBVOL)&&number(x,"subvolumeID")>0&&number(x,"subvolumeID")==m.subvol,"Actual Btrfs filesystem/subvolume evidence differs");require(mapMajor==m.major&&mapMinor==m.minor,"Actual Btrfs mapped superblock device differs");}
 else require(mapMajor==number(s,"major")&&mapMinor==number(s,"minor"),"Non-Btrfs mapping requires exact direct source device");
}

void verifyCapturedMapping(const QVariantMap&r,const QByteArray&expectedHash,uint32_t fullMode){
 verifyFrozenMappingSource(r,expectedHash,fullMode);
 require(boolean(r,"mapFilesUnchanged")&&boolean(r,"selectedRowBeforePresent")&&boolean(r,"selectedRowAfterPresent"),"Exact selected VMA disappeared/replaced");
 const auto path=string(r,"path");require(string(r.value("mapFilesBefore").toMap(),"link")==path&&string(r.value("mapFilesAfter").toMap(),"link")==path,"Actual kernel mapping/FD paths disagree");
}

}
