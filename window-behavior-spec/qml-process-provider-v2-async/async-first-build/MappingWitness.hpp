#pragma once
#include "MappingDiagnostic.hpp"
#include <map>
namespace Lifetime {
// Only a compiled owned-child collection may supply this structure at runtime.
// CPU fault fixtures may call the pure validator; no QML/caller fact authority.
class MappingChanged:public Refused {public:using Refused::Refused;};
void verifyFrozenMappingSource(const QVariantMap&,const QByteArray&expectedHash,uint32_t fullMode);
void verifyCapturedMapping(const QVariantMap&,const QByteArray&expectedHash,uint32_t fullMode);
void verifyOwnedMappings(int,const QByteArray&,const std::map<QString,std::pair<QByteArray,uint32_t>>&,QVariantMap*evidence);
}
