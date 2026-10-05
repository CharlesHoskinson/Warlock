#pragma once
#include "../../helpers/memory/Memory.hpp"
class CWLSurfaceResource;
namespace Warlock {
// Called after a native mode transition; applies cached states only where
// effective synchronization no longer requires a parent's application.
void flushDesynchronizedSurface(SP<CWLSurfaceResource> surface);
}
