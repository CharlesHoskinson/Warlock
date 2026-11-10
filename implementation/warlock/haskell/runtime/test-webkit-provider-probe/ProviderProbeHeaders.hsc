module ProviderProbeHeaders
  (compiledVersion, compiledLayout, compiledWidths, compiledAarch64) where
#include <webkit/webkit.h>
#include <glib-object.h>
#include <stddef.h>

compiledVersion :: (Int,Int,Int)
compiledVersion = (#{const WEBKIT_MAJOR_VERSION}, #{const WEBKIT_MINOR_VERSION}, #{const WEBKIT_MICRO_VERSION})

compiledLayout :: (Int,Int,Int)
compiledLayout = (#{size GValue}, #{alignment GValue}, #{offset GEnumValue, value})

compiledWidths :: (Int,Int,Int,Int)
compiledWidths = (#{size int}, #{size unsigned int}, #{size unsigned long}, #{size size_t})

compiledAarch64 :: Bool
#if defined(__aarch64__) && defined(__LP64__) && (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)
compiledAarch64 = True
#else
compiledAarch64 = False
#endif
