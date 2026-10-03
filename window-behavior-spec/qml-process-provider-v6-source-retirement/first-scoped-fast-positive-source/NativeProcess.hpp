#pragma once
#include "ProcessRegistry.hpp"
namespace Lifetime {
ProcessArm nativeProcessArm(QQmlEngine*,QObject*,QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QString&role,const QString&originalJSON,const Authority&);
}
