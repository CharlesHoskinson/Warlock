# Native client campaign — fixture dispatch failure retained

The exact owning plugin loaded and root commit/seven stale-context checks
passed. The overlap fixture then failed because its legacy Hyprland dispatch
syntax was parsed as Lua. No client image was captured. Ordered fixture exit,
empty clients, plugin unload and private runtime cleanup passed.
Fresh v3 uses the same typed Lua dispatcher constructors as installed Omarchy;
all source, context, original deadlines and pixel oracles remain unchanged.
