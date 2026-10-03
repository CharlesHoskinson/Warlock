#!/usr/bin/env python3
"""Stage additive, read-only taskbar diagnostics without touching the source."""
import argparse, difflib, pathlib, re

def transform(text):
    pattern = r'^    function state\(\): string \{ return JSON.stringify\((\{.*\})\) \}$'
    found = list(re.finditer(pattern, text, re.M))
    if len(found) != 1:
        raise ValueError('Expected exactly one original state IPC method')
    obj = found[0].group(1)
    obj = obj.replace('{fileDragActive:', '{screenName:root.barScreen ? root.barScreen.name : "", monitorGeometry:monitor ? {x:monitor.x,y:monitor.y,width:monitor.width/monitor.scale,height:monitor.height/monitor.scale} : null, barOffset:{x:bx,y:by}, barSize:{width:root.barWindow ? root.barWindow.width : 0,height:root.barWindow ? root.barWindow.height : 0}, fileDragActive:', 1)
    obj = obj.replace('width:root.widthFor(g),windows:', 'width:root.widthFor(g),height:item ? item.height : 0,windows:', 1)
    helper = '''  // Diagnostics only: inspecting other outputs must not move focus or activate a window.
  function diagnosticState() {
    var monitor=root.monitors.find(function(m) { return m.id===root.currentMonitor })
    var bx=root.bar && root.bar.position==="right" && root.barScreen && root.barWindow ? root.barScreen.width-root.barWindow.width : 0
    var by=root.bar && root.bar.position==="bottom" && root.barScreen && root.barWindow ? root.barScreen.height-root.barWindow.height : 0
    return ''' + obj + '''
  }
  function diagnosticStates() {
    var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
    return items.filter(function(item) { return item && typeof item.diagnosticState==="function" }).map(function(item) { return item.diagnosticState() })
  }
'''
    methods = '''    function state(): string { return JSON.stringify(root.diagnosticState()) }
    function stateAll(): string { return JSON.stringify(root.diagnosticStates()) }
    function stateForMonitor(monitor: int): string {
      var states=root.diagnosticStates()
      return JSON.stringify(states.find(function(item) { return item.currentMonitor===monitor }) || null)
    }'''
    result = text[:found[0].start()] + methods + text[found[0].end():]
    return result.replace('  IpcHandler {', helper + '  IpcHandler {', 1)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('destination', type=pathlib.Path)
    args=parser.parse_args()
    if args.source.resolve()==args.destination.resolve():
        parser.error('Source and destination must differ')
    old=args.source.read_text();new=transform(old)
    args.destination.parent.mkdir(parents=True,exist_ok=True)
    args.destination.write_text(new)
    args.destination.with_suffix('.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(args.source),tofile=str(args.destination))))
