#pragma once
namespace Aquamarine {
class IPointer;
class IOutput;
enum class ParentInputStatus { Unsupported, Inactive, Ready };
// Opaque boundary keeps client protocol generated headers out of the owning server.
ParentInputStatus parentPointerInputStatus(const IPointer* pointer, const IOutput* output);
}
