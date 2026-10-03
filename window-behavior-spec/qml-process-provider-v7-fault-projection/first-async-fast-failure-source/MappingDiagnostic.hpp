#pragma once
#include <QVariantMap>
#include <QByteArray>
#include <QString>
namespace Lifetime {
// Bounded readonly attribution only. This supplies no mapping authority and
// never changes the caller's retained device/inode refusal.
QVariantMap mappingDiagnostic(int pid,const QString&path,const QByteArray&row);
}
