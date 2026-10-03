#pragma once
#include <QByteArray>
#include <QCoreApplication>
#include <QPointer>
#include <QThread>
#include <QVariantMap>
#include <QQmlEngine>
#include <QQmlContext>
#include <QQuickItem>
#include <atomic>
#include <cstdint>
#include <map>
#include <stdexcept>

namespace Lifetime {
constexpr uint64_t SAFE_MAX=(uint64_t{1}<<53)-1;
constexpr size_t CAPACITY=65536;
class Refused:public std::runtime_error {public:using std::runtime_error::runtime_error;};
struct ImageSeal {QString path;QByteArray sha;uint64_t device=0,inode=0;uint32_t mode=0;bool operator==(const ImageSeal&)const=default;};
struct Authority {ImageSeal image;QString config;QByteArray configSHA;uint64_t configDevice=0,configInode=0;int pid=0;QString start;void verify()const;};
Authority authority();
ImageSeal actualImage();
void verifyImage(const ImageSeal&);
void pinImage(const ImageSeal&);
void verifyQuickshellProcess();
QString processStart();
void requireOwnerThread();
struct EngineToken {uint64_t generation=0,epoch=0,provider=0;bool operator==(const EngineToken&)const=default;};
struct WidgetToken {
 EngineToken engine;uint64_t widget=0,delegate=0,widgetContext=0,delegateContext=0,window=0;
 bool visualDescendant=false,windowBound=false;
 bool operator==(const WidgetToken&)const=default;
 QVariantMap value()const;
};
uint64_t checkedNext(uint64_t&counter);
void checkedCapacity(size_t current,size_t limit);
class Registry {
 struct Object {QPointer<QObject> weak;uint64_t generation=0;bool faulted=false;};
 struct Engine {QPointer<QQmlEngine> weak;uint64_t generation=0,epoch=0;QPointer<QObject>provider,core;uint64_t providerGen=0,coreGen=0;QMetaObject::Connection completed,failed,coreDestroyed;QObject*relay=nullptr;};
 QThread*owner=nullptr;QPointer<QCoreApplication>application;QObject*context=nullptr;
 std::map<QObject*,Object>objects;std::map<QQmlEngine*,Engine>engines;
 uint64_t nextEngine=1,nextEpoch=1,nextObject=1;
 std::atomic_bool refused{false};
 uint64_t allocate(uint64_t&);
 void thread();
 Engine& engine(QQmlEngine*);
 uint64_t object(QObject*);
 void retireObject(QObject*,uint64_t);
 void retireEngine(QQmlEngine*,uint64_t);
 void retireProvider(QQmlEngine*,uint64_t);
 void retireCore(QQmlEngine*,uint64_t);
 void coreBoundary(QQmlEngine*,uint64_t);
 void faultObject(QObject*);
public:
 Registry();
 ~Registry();
 EngineToken registerProvider(QQmlEngine*,QObject*);
 EngineToken scope(QQmlEngine*,QObject*);
 void bindCore(QQmlEngine*,QObject*,QObject*);
 WidgetToken sample(QQmlEngine*,QObject*,QQuickItem*,QQuickItem*);
 bool current(QQmlEngine*,QObject*,QQuickItem*,QQuickItem*,const WidgetToken&);
 void refuse(){refused.store(true);}
 bool permanentlyRefused()const{return refused.load();}
 static Registry& shared();
};
}
