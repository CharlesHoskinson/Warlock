local commands, callbacks = {}, {}
hl={exec_cmd=function(command)table.insert(commands,command)end,unbind=function()end}
o={bind=function(key,label,callback)callbacks[key]=callback end}
local source=arg[1]
dofile(source)
assert(commands[1]:match('switcher%-barrier'),"reload publishes generation barrier")
commands={}
callbacks["ALT + TAB"]()
callbacks["ALT + SHIFT + TAB"]()
callbacks["ALT + ALT_L"]()
callbacks["ALT + ALT_R"]()
assert(#commands==3,"duplicate modifier releases must not repeat commit")
local generation=commands[1]:match("switcher%-step [%w_.-]+ (%d+)")
assert(generation,"generation created before asynchronous launch")
assert(commands[1]:match(" 1 1$"),"first step ordinal")
assert(commands[2]:match(" "..generation.." 2 %-1$"),"repeat shares chord with unique ordinal")
assert(commands[3]:match("switcher%-release [%w_.-]+ "..generation.." 2$"),"release final ordinal")
callbacks["ALT + TAB"]()
local newer=commands[4]:match("switcher%-step [%w_.-]+ (%d+)")
assert(tonumber(newer)>tonumber(generation),"next chord advances generation")
dofile(source)
assert(commands[5]:match('switcher%-barrier'),"reload publishes new barrier")
callbacks["ALT + TAB"]()
local reloaded=commands[6]:match("switcher%-step [%w_.-]+ (%d+)")
assert(tonumber(reloaded)>tonumber(newer),"reload retains monotonic serial")
print("SWITCHER_LUA_PASS 8")
