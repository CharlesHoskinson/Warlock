from pathlib import Path
import shutil
old=Path('implementation/elm-keyboard-focus-cancellation-v154');root=Path('implementation/elm-keyboard-focus-cancellation-v155')
shutil.copytree(old,root,ignore=lambda path,names:[n for n in names if n.startswith(('build-','hooks-','keys-','cancel-','model-','replay-')) and (Path(path)/n).is_dir()])
p=root/'candidate/src/backend/Wayland.cpp';s=p.read_text();a='struct PrivateParentKeyboard {';assert a in s;s=s.replace(a,'''static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;
static void forgetKeyboardOutputSurface(CWaylandOutput* output) {
    std::erase_if(keyboardOutputSurfaces, [output](const auto& entry) { return entry.second == output; });
}

'''+a)
a='''        const bool owned = std::ranges::any_of(parent->outputs, [surface](const auto& output) {
            return output && output->waylandState.surface &&
                static_cast<wl_proxy*>(output->waylandState.surface->resource()) == surface;
        });''';assert a in s;s=s.replace(a,'''        const auto nativeSurface = keyboardOutputSurfaces.find(surface);
        const bool owned = nativeSurface != keyboardOutputSurfaces.end() &&
            std::ranges::any_of(parent->outputs, [target = nativeSurface->second](const auto& output) { return output.get() == target; });''')
a='''    outputViewport[this] = makeShared<CCWpViewport>''';assert a in s;s=s.replace(a,'''    keyboardOutputSurfaces[static_cast<wl_proxy*>(waylandState.surface->resource())] = this;
    outputViewport[this] = makeShared<CCWpViewport>''')
a='Aquamarine::CWaylandOutput::~CWaylandOutput() {\n';assert a in s;s=s.replace(a,a+'    forgetKeyboardOutputSurface(this);\n')
a='bool Aquamarine::CWaylandOutput::destroy() {\n';assert a in s;s=s.replace(a,a+'    forgetKeyboardOutputSurface(this);\n');p.write_text(s)
# Actual private map/helper, without pretending the keyboard is a CWaylandOutput friend.
p=root/'qa/hooks-template.cpp';s=p.read_text().replace('@@HELPER@@','@@SURFACE_MAP@@\n@@HELPER@@')
a='World(){output->waylandState.surface=makeShared<Surface>();parent->outputs.push_back(output);}';assert a in s;s=s.replace(a,'World(){output->waylandState.surface=makeShared<Surface>();parent->outputs.push_back(output);keyboardOutputSurfaces[surface()]=output.get();}\n ~World(){forgetKeyboardOutputSurface(output.get());}')
s=s.replace('keyboardState.empty()&&failedParentTransports.empty()','keyboardState.empty()&&failedParentTransports.empty()&&keyboardOutputSurfaces.empty()');p.write_text(s)
p=root/'qa/hooks.py';s=p.read_text();a="ctor=text[text.index('Aquamarine::CWaylandKeyboard::CWaylandKeyboard('");i=s.index(a);s=s[:i]+"surface_map=text[text.index('static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;'):text.index('struct PrivateParentKeyboard {')]\n"+s[i:];s=s.replace("template.replace('@@HELPER@@',h)","template.replace('@@SURFACE_MAP@@',surface_map).replace('@@HELPER@@',h)");p.write_text(s)
p=root/'qa/template.cpp';s=p.read_text();a='using namespace Aquamarine;';assert a in s;s=s.replace(a,a+'\nstruct wl_proxy;\n@@KEYBOARD_SURFACE_MAP@@');p.write_text(s)
p=root/'qa/replay3.py';s=p.read_text();a="parts=bodies(candidate.read_text());result=evaluate('candidate',parts,0)";assert a in s;s=s.replace(a,"parts=bodies(candidate.read_text());result=evaluate('candidate',parts,0)")
a="  source=template\n";assert a in s;s=s.replace(a,"  actual=candidate.read_text();surface_map=actual[actual.index('static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;'):actual.index('struct PrivateParentKeyboard {')]\n  source=template.replace('@@KEYBOARD_SURFACE_MAP@@',surface_map)\n")
# The old negative body does not use the new map helper; annotate that extracted static helper only in the CPU adapter.
s=s.replace("surface_map=actual[actual.index('static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;'):actual.index('struct PrivateParentKeyboard {')]","surface_map=actual[actual.index('static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;'):actual.index('struct PrivateParentKeyboard {')].replace('static void forgetKeyboardOutputSurface','[[maybe_unused]] static void forgetKeyboardOutputSurface')")
p.write_text(s)
p=root/'SPEC.md';p.write_text(p.read_text()+'''\nV155 retains154 failed full library compile: keyboard callbacks cannot read private CWaylandOutput state.155 adds a private nonowning surface-to-output index populated by output construction and forgotten by destroy/destructor. Enter requires both index identity and current parent output membership; no public header/friend change and no pointer-focus dependency. Typed constructor28 and key2737/model16/1000x40/10 controls passed154 before that full-build failure;155 requalifies actual map, callbacks, output retirement and complete owning library.\n''')
print(root)
