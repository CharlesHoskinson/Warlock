#pragma once
#include "Lifetime.hpp"
#include <QProcess>
#include <QJsonObject>
#include <QMetaProperty>
#include <functional>
#include <memory>
#include <chrono>
#include <mutex>
#include <deque>
namespace Lifetime {
struct KernelExpected {
 int parent=0,group=0;QString childStart,observerStart;QString executable;QByteArray executableSHA256,argv,cgroup;
 std::map<QString,QString>namespaces;std::map<QByteArray,QByteArray>environment;
 QString observerExecutable;QByteArray observerSHA256,observerARGV,observerCgroup;std::map<QByteArray,QByteArray>observerEnvironment;
 std::map<QString,std::pair<QByteArray,uint32_t>>code;std::map<QString,QString>links;
};
struct KernelWitness {
 int pid=0,parent=0,group=0;QString start,executable;QByteArray executableSHA256,argv,cgroup,maps,environment;
 std::map<QString,QString>namespaces;
 bool operator==(const KernelWitness&)const=default;
 QVariantMap value()const;
};
void bindObserver(KernelExpected&);
QString captureObserverStart();
KernelWitness captureStartedRoot(int,const KernelExpected&,QVariantMap*evidence=nullptr);
void setKernelDeadline(std::chrono::steady_clock::time_point);
void checkKernelBudget();
KernelWitness readKernel(int,const KernelExpected&,QVariantMap*evidence=nullptr);
bool kernelGone(const KernelWitness&);
QByteArray boundedFile(const QString&,qint64 cap=65536);
QByteArray digest(const QByteArray&);
QByteArray guardedRegular(const QString&,uint32_t mode,uint32_t uid,qint64 cap);
QJsonObject strictObject(const QByteArray&,qint64 cap=1048576);
struct ProcessArm {
 QQmlEngine*engine=nullptr;QObject*provider=nullptr;QObject*menu=nullptr;QObject*row=nullptr;QObject*popup=nullptr;QObject*process=nullptr;QObject*out=nullptr;QObject*err=nullptr;
 QString processClass,collectorClass,role;QStringList command;KernelExpected kernel;
 // Compiled production callbacks derive observations from sealed sources and
 // actual lexical objects. No QML success/kernel/EOF flags are accepted.
 std::function<void()>sourceGuard,currentGuard;
 std::function<void(const QByteArray&,const QByteArray&,const KernelWitness&,int)>receiptGuard;
};
class ProcessRegistry {
 struct Invocation;
 Registry&base;QObject*context;QThread*thread;uint64_t nextLease=1;
 std::map<QObject*,std::shared_ptr<Invocation>>rows;
 std::vector<std::shared_ptr<Invocation>>history;
 std::mutex faultMutex;std::deque<std::pair<QObject*,uint64_t>>queuedFaults;std::atomic_bool faultOverflow{false};
 void drainFaults();
 std::shared_ptr<Invocation>find(QObject*,uint64_t);
 void event(QObject*,uint64_t,int,int code=0,QProcess::ExitStatus=QProcess::NormalExit);
 void finishJob(const std::shared_ptr<Invocation>&);
 void stable(const std::shared_ptr<Invocation>&,bool current);
 bool lifecycle(const std::shared_ptr<Invocation>&);
public:
 explicit ProcessRegistry(Registry&);
 ~ProcessRegistry();
 uint64_t arm(ProcessArm);
 QVariantMap state(QObject*);
 QVariantMap terminalInventory();
 void cancel(QObject*);
 static ProcessRegistry&shared();
 // Readonly callback used by the native Qt signal relay. Exact mismatched
 // leases are inert, including preservation of accepted snapshots.
 void callback(QObject*,uint64_t,int,int code=0,QProcess::ExitStatus=QProcess::NormalExit);
};
}
