#pragma once
#include "preview-provider-bootstrap.h"
#include "preview_uri.hpp"
namespace preview::bridge {
class Native;
// Trusted C transaction helpers. Preflight is read-only; release is invoked
// only after the original strict C closure and Native claim completion pass.
bool bootstrapCanReleaseImported(WarlockPreviewBootstrap*,Native*,uri::Endpoint*,uint64_t popup,uint64_t epoch);
bool bootstrapHasImportedDelivery(const WarlockPreviewBootstrap*)noexcept;
void bootstrapReleaseImported(WarlockPreviewBootstrap*)noexcept;
}
