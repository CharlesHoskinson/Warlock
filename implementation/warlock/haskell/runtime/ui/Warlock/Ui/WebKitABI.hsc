module Warlock.Ui.WebKitABI (gValueSize, gValueAlignment, enumValueOffset) where
#include <glib-object.h>
gValueSize, gValueAlignment, enumValueOffset :: Int
gValueSize = #{size GValue}
gValueAlignment = #{alignment GValue}
enumValueOffset = #{offset GEnumValue, value}
