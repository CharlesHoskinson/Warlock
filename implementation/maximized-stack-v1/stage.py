from pathlib import Path
import subprocess,hashlib,json,difflib
root=Path(__file__).resolve().parent;repo=Path('/home/hoskinson/src/hyprland-motion-audit');commit='efb50993780079460b0cbed1363e2166a2de1d9f'
if subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()!=commit:raise ValueError('wrong owning core')
files=['src/render/Renderer.cpp','src/desktop/state/ViewHitTester.cpp','src/desktop/state/WindowState.cpp','src/desktop/view/Window.cpp','src/managers/fullscreen/FullscreenController.cpp']
manifest={'owning_core':commit,'original_repo':str(repo),'files':[],'deployment':'not built or loaded'}
for path in files:
 data=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path]);destination=root/'original'/path;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
 manifest['files'].append({'path':path,'sha256':hashlib.sha256(data).hexdigest()})
path=files[0];original=(root/'original'/path).read_text()
old='''    // then render windows over fullscreen.
    for (auto const& w : Desktop::windowState()->windows()) {
        const bool shouldSkipWindow'''
new='''    // Native floating MAX participates in the same bottom-to-top stack as
    // ordinary floats. Do not draw a previously raised float above it after
    // MAX is raised again. Keep true fullscreen and pinned priority unchanged.
    const bool respectFloatingMaxStack = pWorkspaceWindow->m_isFloating &&
        Fullscreen::controller()->getFullscreenModes(pWorkspaceWindow).internal == Fullscreen::FSMODE_MAXIMIZED;
    bool floatingMaxSeen = false;

    // then render windows over fullscreen.
    for (auto const& w : Desktop::windowState()->windows()) {
        if (w == pWorkspaceWindow)
            floatingMaxSeen = true;

        if (respectFloatingMaxStack && !floatingMaxSeen && !w->m_pinned)
            continue; // already drawn below MAX by the ordinary floating pass

        const bool shouldSkipWindow'''
if original.count(old)!=1:raise ValueError('exact renderer insertion boundary missing')
candidate=original.replace(old,new);destination=root/'candidate'/path;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(candidate)
(root/'floating-max-stack.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),fromfile='a/'+path,tofile='b/'+path)))
manifest['candidate']={'path':path,'sha256':hashlib.sha256(candidate.encode()).hexdigest(),'changed_lines':15,'policy':'render order only; no input, alpha, allowedOverFullscreen or geometry mutations'}
(root/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
