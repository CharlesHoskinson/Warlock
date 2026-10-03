from pathlib import Path
import difflib,hashlib,json,re,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
V=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v7-fault-projection')
P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/widget_v66')
def record(p):
    return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def span(s,needle):
    start=s.index(needle);brace=s.index('{',start);depth=0
    # This bounded source reconstruction skips quoted literals and comments.
    for m in re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/|[{}]',s[brace:]):
        if m.group()=='{':depth+=1
        elif m.group()=='}':
            depth-=1
            if depth==0:return start,brace+m.end()
    raise AssertionError('Unclosed source body')
def remove(s,needle):
    a,b=span(s,needle);return s[:a]+s[b+int(s[b:b+1]=='\n'):]
def body(s,needle):
    a,b=span(s,needle);return s[a:b]
def main():
    require_qa_scope();checks={};inputs={};diffs=B/'revised-diffs';diffs.mkdir(exist_ok=True)
    sources={}
    for p in sorted((B/'revised-desired').iterdir()):
        old=(P if p.suffix=='.qml' else V)/p.name
        sources[p.name]=(old.read_text(),p.read_text());inputs[str(old)]=record(old);inputs[str(p)]=record(p)
        (diffs/(p.name+'.diff')).write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=str(old),tofile=str(p))))
    old,new=sources['ProcessRegistry.cpp'];inverse=remove(remove(new,'void ProcessRegistry::changed('),'QVariantMap ProcessRegistry::retire(').replace('#include <algorithm>\n','')
    inverse=inverse.replace('if(r)changed(r);','').replace('r->failure="Original worker delivery deadline expired";changed(r);return;','r->failure="Original worker delivery deadline expired";return;').replace('if(r->fault){changed(r);return;}','if(r->fault)return;').replace('r->kernel=false;changed(r);return;','r->kernel=false;return;').replace('\n changed(r);\n}', '\n}')
    inverse=inverse.replace('auto invalidate=[this](const std::shared_ptr<Invocation>&r)', 'auto invalidate=[](const std::shared_ptr<Invocation>&r)').replace('r->evidence.insert("failure",r->failure);changed(r);};if(faultOverflow', 'r->evidence.insert("failure",r->failure);};if(faultOverflow')
    checks['RegistryFullInverseExact']=inverse==old
    for name in ['arm','event','stable','state','cancel','lifecycle','terminalInventory']:
        needle='ProcessRegistry::'+name+'('
        checks['Registry_'+name+'_Exact']=body(old,needle)==body(new,needle)
    old,new=sources['NativeProcess.cpp'];inverse=remove(new,'ProcessRetireScope nativeProcessRetireScope(').replace('#include <set>\n','')
    a=inverse.index('a.changed=');b=inverse.index('a.sourceGuard=',a);inverse=inverse[:a]+inverse[b:]
    checks['NativeProcessFullInverseExact']=inverse==old
    old,new=sources['Provider.cpp'];checks['ProviderFullInverseExact']=remove(new,'QVariantMap ObjectLifetimeProvider::retireProcess(')==old
    old,new=sources['NativeProcess.hpp'];checks['NativeHeaderInverseExact']='\n'.join(x for x in new.split('\n')if not x.startswith('ProcessRetireScope nativeProcessRetireScope('))==old
    old,new=sources['Provider.hpp'];inverse='\n'.join(x for x in new.split('\n')if not x.startswith(' Q_INVOKABLE QVariantMap retireProcess(')and x!='signals:'and not x.startswith(' void processLifecycleChanged('));checks['ProviderHeaderInverseExact']=inverse==old
    old,new=sources['ProcessRegistry.hpp'];inverse=new.replace(' // Optional owning-thread non-authoritative change hint; never a kernel proof.\n std::function<void(uint64_t)>changed;\n','')
    a=inverse.index('struct ProcessRetireScope ');b=inverse.index('class ProcessRegistry ',a);inverse=inverse[:a]+inverse[b:]
    inverse=inverse.replace(' void changed(const std::shared_ptr<Invocation>&);\n','').replace(' QVariantMap retire(const ProcessRetireScope&);\n','');checks['RegistryHeaderInverseExact']=inverse==old
    old,new=sources['PinWindowMenu.qml'];inverse=new
    for name in ['close','openWindow','captureFinished','toggle','actionFinished']:
        a,b=span(inverse,'function '+name+'(');inverse=inverse[:a]+body(old,'function '+name+'(')+inverse[b:]
    for name in ['retirePrevious','armActual','actualState']:
        a,b=span(inverse,'    function '+name+'(');inverse=inverse[:a]+inverse[b+1:]
    inverse=remove(inverse,'    Connections {')
    inverse=inverse.replace('import WindowObjectLifetimeV1 1.0 as NativeLifetime\n','').replace('        id:pinPopup\n','')
    for line in ['    property real captureLease: 0\n','    property real actionLease: 0\n','    property bool capturePublished: false\n','    property bool actionPublished: false\n']:inverse=inverse.replace(line,'')
    checks['QmlFullInverseExact']=inverse==old
    baseline=json.loads((B.parent/'SOURCE_BASELINE.json').read_text())['inputs']
    checks['KnownV7AndFrontendBaselineExact']=all(record(Path(p))['sha256']==h for p,h in baseline.items())
    checks['PolicyFileNotProposedForModification']=not (B/'revised-desired/PinMenu.js').exists();inputs[str(P/'PinMenu.js')]=record(P/'PinMenu.js')
    checks['NoUnapprovedPrivateRegistryCall']='Registry::shared().object('not in sources['NativeProcess.cpp'][1]
    assert all(checks.values()),checks
    result={'result':'pass','checks':checks,'inputs':inputs,'sourceReconstructionOnly':True,'compiled':False,'runtimeExecuted':False,'installedQS':False,'GUI':False,'reliabilityAccepted':False}
    (B/'revised-source-inverses.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':'pass','checks':len(checks),'report':str(B/'revised-source-inverses.json')}))
if __name__=='__main__':main()
