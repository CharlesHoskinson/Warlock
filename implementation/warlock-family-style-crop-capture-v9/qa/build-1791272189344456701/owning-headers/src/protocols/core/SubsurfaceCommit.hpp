#pragma once
#include "../../helpers/memory/Memory.hpp"
class CWLSurfaceResource;
namespace Warlock {
// Called after a native mode transition; applies cached states only where
// effective synchronization no longer requires a parent's application.
void flushDesynchronizedSurface(SP<CWLSurfaceResource> surface);
}

class CWLSubsurfaceResource;
namespace Warlock {
// Requests update display-owned pending layout; false means allocation refusal.
bool queueSubsurfacePosition(SP<CWLSubsurfaceResource> sub,int32_t x,int32_t y);
bool queueSubsurfaceOrder(SP<CWLSubsurfaceResource> sub,SP<CWLSurfaceResource> sibling,bool above);
}
