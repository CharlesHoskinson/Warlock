"""Fresh tuple adapter for original taskbar journey; static checks are not GUI acceptance."""
import hashlib, importlib.util, json, os, re, shlex, socket, struct, time
from pathlib import Path

REPO = Path('/home/charles/Warlock')
BASE = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
PARENT = BASE/'parent-host/fresh_weston.py'
COLLECTOR = BASE/'taskbar-qa/measured_inspection.py'
COLLECTOR_SHA = '559775d3a39c14b1cea2b5747773665a4817c5b9850d08afc4782d2919a11f9e'
PARENT_SHA = 'e045634bd023f07977c398ef0057b9fdee3a1e1718d51c879e221ee353e28ae9'
TUPLE_SHA = 'bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'
PREFLIGHT_SHA = '56e50f6a488b39fadf72064586422c33d0162d78aa36e9b88e7ca8dee0a83a3e'
REVIEW_SHA = 'c73693f0aa11091b3788e30f5e699f491293f43c005fa4977f03b27e5ff61e6b'
FOUNDATION_SHA = '08b24bd93cbb63ec097900915379b32e90d9dcca7156d04fe8ee959efaff264f'
HELPERS = {
 'qa/session_bus.py':'d8f945a68a8e772ffd26458e8e60beac8c8ad79849f08a2daf4110f5c8178916',
 'qa/system_isolation.py':'029a41bc8aae39936c69dc591857795aabd43df17b1f9a86b02b6c6a83dddc0e',
 'qa/isolation.py':'95e6999ccb1528311e950d95bf855a00bc29327458152eb7943f1f01bce1ceb8',
 'qa/inspection.py':'051d44430a49319389781d12bc0389732d76412ef1cf7f59f352f5e78f67bdd2',
 'qa/input_helper.py':'4599a448fff3a14ff88291acba3b6204882a985be36ef657b11c0acd881a0bf6',
 'fixture.py':'c6628d141b75bb20cc2fa526d85ef2a14025a28b832ebae57f1d996c76552f06'}
RUNTIME=REPO/'implementation/warlock-client-provider-native-v204'
# Exact protected current-source build receipt; frozen old evidence stays intact.
ASSET_REPORT = BASE/'launcher-pending-visibility-fix/assets-build-v1/report.json'
ASSET_REPORT_SHA = 'd31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606'
HOST_REPORT = BASE/'taskbar-host-rebuild-v1/output/report.json'
HOST_REPORT_SHA = '13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'
NEW_HOST_SHA = 'e0a2f0464b090f77c744c7fe7fc8e356a9d0f1ce2ad8a648040379dd2f7c0558'
CURRENT_HOST_SOURCE_SHA = 'f78d1ba337dff920e50e79e7324d5467cfbfe240a3b4d03c7d4239f52b17850a'
OLD_HOST_SOURCE_SHA = 'cde6230199756dfaa193d5e8af5a41470f8b65de3cdd1942e0e0224ab458ccbf'
CURRENT_DESKTOP_SHA = 'a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404'
OLD_DESKTOP_SHA = '1b5b48fc5ca71c6e11bd54ea6ab723f5a37f4d383d6a59c99d14d83b005d5033'


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def checked(path, expected):
    if digest(path)!=expected:raise RuntimeError('Pinned input changed: '+str(path))

def verify_tuple():
    paths=[(BASE/'fresh-pair/tuple.json',TUPLE_SHA), (BASE/'fresh-pair/preflight-report.json',PREFLIGHT_SHA),
           (BASE/'runtime-review/runtime-review.json',REVIEW_SHA), (BASE/'parent-host/foundation-result.json',FOUNDATION_SHA)]
    for p,h in paths:checked(p,h)
    def pinned_json(path, expected):
        body=Path(path).read_bytes()
        if hashlib.sha256(body).hexdigest()!=expected:
            raise RuntimeError('Source-coherence evidence changed: '+str(path))
        return json.loads(body)
    tup=json.loads(paths[0][0].read_text())
    original_pre=pinned_json(paths[1][0],PREFLIGHT_SHA)
    addendum=pinned_json(Path("/home/charles/.local/state/warlock-team/20261028/native-rebuild/source-coherence-20261028/terra-2/addendum-v1.json"),"051cb5c76896ce4db6edc0b94042181d4614fd163a8f36e3239634522f532e63")
    pre=pinned_json(Path("/home/charles/.local/state/warlock-team/20261028/native-rebuild/source-coherence-20261028/terra-2/preflight-v1.json"),"ae8d3fdb03bbbed5e4b42fd91225dfba1891142e1403389d74112d2b0f945b89")
    expected_replacement={'index':3390,'label':'host sourceHashes',
        'path':'/home/charles/Warlock/implementation/warlock/adapter/release_builder.py',
        'previousSHA256':'640b47a214286ca9ec3fcda74d98d895610202befd49e9b8bcce51706e9a9919',
        'currentSHA256':'43dfc887228de8a755964a0aaa8b645d9fb8f4a4a4a288b7ff48d7b1844d630a'}
    if (addendum.get('schema')!=1 or addendum.get('kind')!='one-entry-source-coherence-addendum' or
        addendum.get('version')!='20261028-v1' or addendum.get('replacement')!=expected_replacement or
        addendum.get('originalPreflight')!={'path':str(paths[1][0]),'sha256':PREFLIGHT_SHA} or
        addendum.get('tuple')!={'path':str(paths[0][0]),'sha256':TUPLE_SHA} or
        addendum.get('derivedPreflight')!={'path':"/home/charles/.local/state/warlock-team/20261028/native-rebuild/source-coherence-20261028/terra-2/preflight-v1.json",'sha256':"ae8d3fdb03bbbed5e4b42fd91225dfba1891142e1403389d74112d2b0f945b89"}):
        raise RuntimeError('Invalid source-coherence addendum')
    if len(original_pre.get('checks',[]))!=4721:
        raise RuntimeError('Original preflight inventory changed')
    before=original_pre['checks'][3390]
    if (before.get('label')!=expected_replacement['label'] or before.get('path')!=expected_replacement['path'] or
        before.get('expectedSHA256')!=expected_replacement['previousSHA256'] or
        before.get('actualSHA256')!=expected_replacement['previousSHA256'] or before.get('passed') is not True):
        raise RuntimeError('Unexpected original preflight entry')
    expected_pre=json.loads(json.dumps(original_pre))
    expected_pre['checks'][3390]['expectedSHA256']=expected_replacement['currentSHA256']
    expected_pre['checks'][3390]['actualSHA256']=expected_replacement['currentSHA256']
    if pre!=expected_pre:
        raise RuntimeError('Derived preflight contains unrelated changes')
    for evidence in addendum['evidence']:
        checked(evidence['path'],evidence['sha256'])
    review=json.loads(paths[2][0].read_text()); foundation=json.loads(paths[3][0].read_text())
    if not (tup.get('readyForRootReview') is True and tup.get('sourceBase')=='0ecc8725ae27989da4049ce04d2e6f20add9e080' and tup.get('nativeAcceptance') is False and tup.get('pluginLoaded') is False and pre.get('passed') is True and not pre.get('errors') and pre.get('tupleSHA256')==TUPLE_SHA and review.get('passed') is True and not review.get('errors') and foundation.get('passed') is True and foundation.get('productPluginLoaded') is False):
        raise RuntimeError('Fresh tuple/preflight/review/foundation disposition mismatch')
    if len(pre['checks'])!=4721:raise RuntimeError('Fresh preflight inventory changed')
    allowed_changes={str(REPO/'implementation/warlock/src/Desktop.elm'):(OLD_DESKTOP_SHA,CURRENT_DESKTOP_SHA,{'host sourceHashes'}),str(REPO/'implementation/warlock/native/host.c'):(OLD_HOST_SOURCE_SHA,CURRENT_HOST_SOURCE_SHA,{'host sourceHashes','host compiledDependencyHashes'})}
    seen_changes=set()
    for row in pre['checks']:
        if row.get('passed') is not True:raise RuntimeError('Failed fresh preflight entry')
        path=row.get('path')
        if path in allowed_changes:
            previous,current,labels=allowed_changes[path]
            if row.get('label') not in labels or row.get('expectedSHA256')!=previous or row.get('actualSHA256')!=previous:
                raise RuntimeError('Unexpected historical changed-source row')
            checked(path,current);seen_changes.add(path)
        elif 'expectedSHA256' in row:checked(path,row['expectedSHA256'])
        elif row.get('label')=='aquamarine soname alias':
            p=Path(row['path']); target=row['target']
            if not p.is_symlink() or os.readlink(p)!=target:raise RuntimeError('AQ alias changed')
        else:raise RuntimeError('Unknown fresh preflight entry')
    if seen_changes!=set(allowed_changes):raise RuntimeError('Missing expected source change from frozen inventory')
    for row in tup['reports'].values():checked(row['path'],row['sha256'])
    for name in ('core','aquamarine','authority','host'):
        row=tup['slots'][name];checked(row['path'],row['sha256'])
    aq=tup['slots']['aquamarine'];alias=Path(aq['sonameAlias'])
    if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve():raise RuntimeError('AQ resolution changed')
    for row in tup['slots']['host']['assets'].values():checked(row['path'],row['sha256'])
    checked(COLLECTOR,COLLECTOR_SHA)
    for name,h in HELPERS.items():checked(RUNTIME/name,h)
    checked(REPO/'installed/home/.local/share/hypr-window-controls/qa/virtual-pointer','b092c3369d88b4d61fce80607614a5ec02258e0b774f0b10504a23385cb24434')
    checked(REPO/'window-integration-qa/orca-reader/physical-commands/evdev-keyboard','7bb54790faf1c47ab3a4184d84fa07fc1ab34c44d762ef457696f147777e95c0')
    product_assets=REPO/'implementation/warlock/assets'; built_assets=BASE/'host/assets'
    product={p.relative_to(product_assets):digest(p) for p in product_assets.rglob('*') if p.is_file()}
    built={p.relative_to(built_assets):digest(p) for p in built_assets.rglob('*') if p.is_file()}
    if product!=built:raise RuntimeError('Historical built and canonical assets differ')
    checked(ASSET_REPORT,ASSET_REPORT_SHA)
    receipt=json.loads(ASSET_REPORT.read_bytes())
    if (receipt.get('schema')!=1 or receipt.get('passed') is not True or receipt.get('protectedScope',{}).get('coreLimit')!=1 or receipt.get('protectedScope',{}).get('cgroup')!='0::/user.slice/user-1000.slice/user@1000.service/qa.slice/qa-harness.slice/qa-harness-2ee9b9455c8c44d39b249c8be93bd467.scope'):
        raise RuntimeError('Asset build not qualified')
    previous=json.loads(Path(tup['slots']['host']['report']['path']).read_bytes())
    native=receipt['nativeReuse']
    for name in ('host','core','authority','aquamarine'):
        if native[name]!={k:tup['slots'][name][k] for k in ('path','sha256')}:
            raise RuntimeError('Native reuse slot changed: '+name)
    if native['hostReport']!=tup['slots']['host']['report']:
        raise RuntimeError('Reused host report changed')
    if native['compiledDependencyHashes']!=previous['compiledDependencyHashes'] or len(native['compiledDependencyHashes'])!=1317:
        raise RuntimeError('Native dependency inventory changed')
    for name,h in native['compiledDependencyHashes'].items():
        if name==str(REPO/'implementation/warlock/native/host.c'):
            if h!=OLD_HOST_SOURCE_SHA:raise RuntimeError('Unexpected historical host dependency')
            checked(name,CURRENT_HOST_SOURCE_SHA)
        else:checked(name,h)
    if native['aquamarineAlias']!={'path':aq['sonameAlias'],'target':aq['aliasTarget']}:
        raise RuntimeError('Native AQ alias receipt changed')
    providers=native['linkedProviders']
    if not providers:raise RuntimeError('Empty recorded provider set')
    for row in providers.values():checked(row['path'],row['sha256'])
    product_root=REPO/'implementation/warlock'; source_root=product_root/'src'
    source_paths=sorted(source_root.rglob('*.elm'))
    if len(source_paths)!=96:raise RuntimeError('Elm source inventory changed')
    sources=source_paths+[product_root/'elm.json',product_root/'qa/NewInstanceReplay.elm',product_root/'qa/NativePointerFixture.elm',product_root/'qa/feedback-replay.js']
    expected_sources={str(p):digest(p) for p in sources}
    if receipt['sourceBefore']!=expected_sources or receipt['sourceAfter']!=expected_sources or expected_sources[str(source_root/'Desktop.elm')]!=CURRENT_DESKTOP_SHA:
        raise RuntimeError('Asset source inventory changed')
    old_sources=previous['sourceHashes']
    for p in sources:
        key=str(p.relative_to(REPO)); expected=CURRENT_DESKTOP_SHA if p==source_root/'Desktop.elm' else old_sources[key]
        if expected_sources[str(p)]!=expected:raise RuntimeError('Unreviewed source delta: '+str(p))
    generated={'elm.js','bar.js','popup.js'}
    product_entries=list(product_assets.rglob('*'))
    if any(p.is_symlink() for p in product_entries):raise RuntimeError('Symlink in product assets')
    static={str(p.relative_to(product_assets)):digest(p) for p in product_entries if p.is_file() and str(p.relative_to(product_assets)) not in generated}
    if receipt['staticBefore']!=static or receipt['staticAfter']!=static:
        raise RuntimeError('Static asset source inventory changed')
    out=ASSET_REPORT.parent/'assets'
    found=list(out.rglob('*'))
    if any(p.is_symlink() for p in found):raise RuntimeError('Symlink in new assets')
    actual={str(p.relative_to(out)):digest(p) for p in found if p.is_file()}
    if set(actual)!=set(static)|generated:raise RuntimeError('New asset inventory changed')
    if {k:actual[k] for k in static}!=static:raise RuntimeError('New static asset mismatch')
    expected_assets={'assets/'+k:{'path':str(out/k),'sha256':v} for k,v in actual.items()}
    if receipt['assets']!=expected_assets:raise RuntimeError('New asset receipt mismatch')
    held=REPO/'implementation/warlock-preview-provider-v143'
    manifest=held/'qa/toolchain.json'; manifest_sha='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'
    compiler_sha='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
    checked(manifest,manifest_sha); toolchain=json.loads(manifest.read_bytes())
    if receipt['toolchainManifestSHA256']!=manifest_sha or receipt['compilerSHA256']!=compiler_sha or toolchain['compilerSHA256']!=compiler_sha or len(toolchain['heldFiles'])!=111:
        raise RuntimeError('Held toolchain receipt mismatch')
    for name,row in toolchain['heldFiles'].items():
        p=held/name
        if p.stat().st_size!=row['size']:raise RuntimeError('Held toolchain size changed')
        checked(p,row['sha256'])
    compiler=held/toolchain['compiler'];checked(compiler,compiler_sha)
    if receipt['driver']['sha256']!='1a4394fceb89e49b1be5a13cf744a0df910678b086995bec75fbc72ea68fcb49':raise RuntimeError('Unreviewed asset build driver')
    checked(receipt['driver']['path'],receipt['driver']['sha256']);checked(receipt['node']['path'],receipt['node']['sha256'])
    commands=receipt['commands']; names=[row['name'] for row in commands]
    if names!=['host-ldd','compile-Main','compile-Bar','compile-Popup','compile-NewInstanceReplay','typed-NewInstanceReplay','host-ldd-after']:
        raise RuntimeError('Unexpected build command sequence')
    for row in commands:
        if row['exit']!=0:raise RuntimeError('Asset build command failed')
        checked(row['stdout'],row['stdoutSHA256']);checked(row['stderr'],row['stderrSHA256'])
    for row in commands:
        if row['name'] in ('host-ldd','host-ldd-after') and (row['argv']!=['/usr/bin/ldd',tup['slots']['host']['path']] or row['cwd']!=str(REPO)):
            raise RuntimeError('Unexpected host provider command')
    old_ldd=BASE/'host/host-ldd.stdout';checked(old_ldd,'c0a0bc7fd8063760c81e6421b220c3a11546c00d2af778f3c7412462c466064b')
    def provider_paths(path):
        result={}
        for line in Path(path).read_text().splitlines():
            if 'not found' in line:raise RuntimeError('Missing linked provider')
            pair=re.search(r'^\s*(\S+)\s+=>\s+(/\S+)\s+\(',line)
            direct=re.search(r'^\s*(/\S+)\s+\(',line)
            if pair:result[pair.group(1)]=str(Path(pair.group(2)).resolve(strict=True))
            elif direct:result['loader']=str(Path(direct.group(1)).resolve(strict=True))
        if not result:raise RuntimeError('Empty provider receipt')
        return result
    paths={name:row['path'] for name,row in providers.items()}
    if provider_paths(old_ldd)!=paths or any(provider_paths(row['stdout'])!=paths for row in commands if row['name'] in ('host-ldd','host-ldd-after')):
        raise RuntimeError('Host linked provider mapping changed')
    if receipt['driver']['path']!=str(ASSET_REPORT.parent.parent/'build-assets.py'):
        raise RuntimeError('Unexpected asset build driver')
    for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
        row=next(r for r in commands if r['name']=='compile-'+module)
        if row['argv']!=[str(compiler),'make','src/'+module+'.elm','--optimize','--output='+str(out/target)] or row['cwd']!=str(ASSET_REPORT.parent/'workspace'):
            raise RuntimeError('Asset compilation recipe differs')
    if len(receipt['newInstanceChecks'])!=19 or set(receipt['newInstanceChecks'])!=set(previous['reducerChecks']) or not all(v is True for v in receipt['newInstanceChecks'].values()):
        raise RuntimeError('New instance replay failed')
    for path,h in receipt['replayArtifacts'].items():checked(path,h)
    checked(HOST_REPORT,HOST_REPORT_SHA)
    rebuilt=json.loads(HOST_REPORT.read_bytes()); out_host=HOST_REPORT.parent
    if (rebuilt.get('passed') is not True or rebuilt.get('nativeAcceptance') is not False or rebuilt.get('coreLimit')!=[1,1] or rebuilt.get('cgroup')!='0::/user.slice/user-1000.slice/user@1000.service/qa.slice/qa-harness.slice/qa-harness-bfed7884e7c444c4b75f4f36b63f2d26.scope' or rebuilt.get('reviewedHostSHA256')!=CURRENT_HOST_SOURCE_SHA or rebuilt.get('assetReportSHA256')!=ASSET_REPORT_SHA or rebuilt.get('tupleSHA256')!=TUPLE_SHA or rebuilt.get('historicalReportSHA256')!=tup['slots']['host']['report']['sha256']):
        raise RuntimeError('Rebuilt host qualification mismatch')
    driver=HOST_REPORT.parent.parent/'build-host.py'
    if rebuilt.get('driverSHA256')!='3e393072d4e7c1468884fa2fd1ae345be363df5e86a821107eb3d554f104eac4':raise RuntimeError('Unreviewed host build driver')
    checked(driver,rebuilt['driverSHA256'])
    native_root=product_root/'native'
    current_native={str(p):digest(p) for p in sorted(native_root.rglob('*')) if p.is_file()}
    if rebuilt['nativeSourcesBefore']!=current_native or rebuilt['nativeSourcesAfter']!=current_native:raise RuntimeError('Native sources changed')
    expected_prior=dict(previous['compiledDependencyHashes'])
    host_source=str(native_root/'host.c')
    if expected_prior.get(host_source)!=OLD_HOST_SOURCE_SHA:raise RuntimeError('Unexpected prior native host input')
    expected_prior[host_source]=CURRENT_HOST_SOURCE_SHA
    if rebuilt['historicalDependenciesAdjusted']!=expected_prior:raise RuntimeError('Unreviewed old dependency delta')
    for path,h in expected_prior.items():checked(path,h)
    fresh=rebuilt['freshDependenciesAfterCompile']
    if not fresh:raise RuntimeError('Empty fresh dependency inventory')
    for path,h in fresh.items():checked(path,h)
    for group in ('toolHashes','compilerSupportTools','linkedProviders','outputs'):
        if not rebuilt[group]:raise RuntimeError('Empty rebuilt input group: '+group)
        for path,h in rebuilt[group].items():checked(path,h)
    new_host=out_host/'elm-host';checked(new_host,NEW_HOST_SHA)
    if rebuilt['outputs'].get(str(new_host))!=NEW_HOST_SHA:raise RuntimeError('Rebuilt host output mismatch')
    if rebuilt['assetSources']!=receipt['sourceAfter'] or rebuilt['assets']!={row['path']:row['sha256'] for row in receipt['assets'].values()} or rebuilt['heldManifestSHA256']!=manifest_sha or rebuilt['elmCompilerSHA256']!=compiler_sha:
        raise RuntimeError('Rebuilt host asset/toolchain binding changed')
    if rebuilt['pkgConfigFlags']!=previous['pkgConfigFlags']:raise RuntimeError('Host build flags changed')
    if set(rebuilt['linkedProviders'])!={row['path'] for row in providers.values()}:
        raise RuntimeError('Rebuilt host provider path set changed')
    for row in providers.values():
        if rebuilt['linkedProviders'][row['path']]!=row['sha256']:raise RuntimeError('Rebuilt host provider bytes changed')
    units=['shared-host.c','preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
    required=['cc-version','cxx-version','pkg-version','pkg-modversions','pkg-config','tool-cc1','tool-cc1plus','tool-as','tool-ld','tool-collect2']+['compile-'+name for name in units]+['link-host','host-ldd']
    host_commands=rebuilt['commands']
    if [row['name'] for row in host_commands]!=required:raise RuntimeError('Unexpected native build command sequence')
    expected_env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
    for row in host_commands:
        if row['exit']!=0 or row['cwd']!=str(REPO) or row['env']!=expected_env:raise RuntimeError('Host build command failed or context changed')
        checked(out_host/(row['name']+'.stdout'),row['stdoutSHA256']);checked(out_host/(row['name']+'.stderr'),row['stderrSHA256'])
    flags=rebuilt['pkgConfigFlags']; objs=[]
    for i,name in enumerate(units):
        obj=out_host/(name+'.o');dep=out_host/(name+'.d');objs.append(str(obj))
        argv=[('/usr/bin/cc' if i==0 else '/usr/bin/g++'),('-std=c11' if i==0 else '-std=c++20'),'-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(dep),'-c',str(native_root/name),'-o',str(obj),*flags]
        if next(row for row in host_commands if row['name']=='compile-'+name)['argv']!=argv:raise RuntimeError('Host translation unit recipe changed: '+name)
        if str(obj) not in rebuilt['outputs'] or str(dep) not in rebuilt['outputs']:raise RuntimeError('Missing host object or depfile')
    expected_outputs={str(new_host)}|{str(out_host/(name+suffix)) for name in units for suffix in ('.o','.d')}
    if set(rebuilt['outputs'])!=expected_outputs:raise RuntimeError('Host build output inventory differs')
    dep_paths=set()
    for name in units:
        raw=(out_host/(name+'.d')).read_text().replace('\\\n',' ')
        _,separator,body=raw.partition(':')
        if not separator:raise RuntimeError('Malformed host dependency file')
        for namepart in shlex.split(body):
            path=Path(namepart);dep_paths.add(str(path if path.is_absolute() else REPO/path))
    if dep_paths!=set(fresh):raise RuntimeError('Fresh host dependency file coverage differs')
    if next(row for row in host_commands if row['name']=='link-host')['argv']!=['/usr/bin/g++',*objs,'-o',str(new_host),*flags]:raise RuntimeError('Host link recipe changed')
    if next(row for row in host_commands if row['name']=='host-ldd')['argv']!=['/usr/bin/ldd',str(new_host)]:raise RuntimeError('Host ldd recipe changed')
    tup['slots']['host']['historicalHostReport']=dict(tup['slots']['host']['report'])
    tup['slots']['host']['historicalHostBinary']={'path':tup['slots']['host']['path'],'sha256':tup['slots']['host']['sha256']}
    tup['slots']['host']['path']=str(new_host);tup['slots']['host']['sha256']=NEW_HOST_SHA
    tup['slots']['host']['report']={'path':str(HOST_REPORT),'sha256':HOST_REPORT_SHA}
    tup['slots']['host']['assets']={k:expected_assets[k] for k in ('assets/elm.js','assets/bar.js','assets/popup.js')}
    tup['sourceQualification']={'kind':'Current Desktop and native host rebuilt; old tuple retained as history','assetReportSHA256':ASSET_REPORT_SHA,'hostReportSHA256':HOST_REPORT_SHA,'desktopSHA256':CURRENT_DESKTOP_SHA,'hostSourceSHA256':CURRENT_HOST_SOURCE_SHA,'historicalTupleSHA256':TUPLE_SHA}
    return tup

checked(PARENT,PARENT_SHA)
spec=importlib.util.spec_from_file_location('fresh_weston_parent',PARENT)
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
original.qa.require_qa_scope()
tuple_data=verify_tuple()
collector_spec=importlib.util.spec_from_file_location("measured_taskbar_collector",COLLECTOR)
collector_module=importlib.util.module_from_spec(collector_spec);collector_spec.loader.exec_module(collector_module)
Collector=collector_module.Collector

class ReviewedWestonHost(original.PrivateWestonHost):
    def verify(self):
        super().verify(); verify_tuple()
        self.evidence['freshTupleSHA256']=TUPLE_SHA
    def launch(self,name,command,env=None):
        if name=='weston':
            packet=original.verify_fresh();module=packet['module']
            checked(module,packet['moduleSHA256'])
            for path,h in packet['owningModuleFiles'].items():checked(path,h)
            if not command or str(command[0])!=str(original.PREFIX/'usr/bin/weston') or '--backend=headless' not in command or '--fake-seat' not in command:raise RuntimeError('Parent input requires exact headless/fake-seat')
            selected=dict(self.env if env is None else env);selected['ELM_PARENT_INPUT_QA']='1'
            self.evidence['parentInputProbe']={'module':module,'moduleSHA256':packet['moduleSHA256']}
            return super().launch(name,[*command,'--modules='+module],selected)
        if name=='hyprland':
            tup=verify_tuple();core=tup['slots']['core'];aq=tup['slots']['aquamarine']
            if not command or str(command[0])!='/usr/bin/Hyprland' or env is None or env.get('AQ_BACKENDS')!='wayland':raise RuntimeError('Child requires reviewed Wayland backend')
            selected=dict(env);selected['WAYLAND_DEBUG']='client';selected['LD_LIBRARY_PATH']=str(Path(aq['path']).parent)+':'+selected.get('LD_LIBRARY_PATH','')
            self.evidence['privateAquamarine']={'path':aq['path'],'sha256':aq['sha256'],'childLibraryPath':selected['LD_LIBRARY_PATH']}
            return super().launch(name,[core['path'],*command[1:]],selected)
        return super().launch(name,command,env)

    def wait_socket(self,name,proc):
        # Leave the parent/Wayland readiness protocol unchanged. Never guess an IPC target.
        parts=Path(name).parts
        if not parts or parts[-1]!='.socket.sock':
            return super().wait_socket(name,proc)
        original.qa.require_qa_scope()
        runtime=original.qa.verify_runtime(self.runtime)
        if len(parts)!=3 or parts[0]!='hypr' or not re.fullmatch(r'[A-Za-z0-9_]+',parts[1]) or Path(name).is_absolute():
            raise RuntimeError('Invalid private IPC readiness path')
        records=[row for owned,row in self.processes if owned is proc and row.get('name')=='hyprland' and row.get('command',[None])[0]==tuple_data['slots']['core']['path']]
        if len(records)!=1:
            raise RuntimeError('IPC readiness requires exact registered child')
        expected=records[0]
        def live():
            if proc.poll() is not None or not original.same_process(expected):
                raise RuntimeError('Private IPC child exited or changed identity')
        live()
        path=runtime/name
        deadline=time.monotonic()+12
        while True:
            live()
            if time.monotonic()>=deadline:raise RuntimeError('Private IPC readiness timed out')
            try:
                before=original.socket_identity(path,runtime)
                # Every intermediate path must remain inside the owned runtime without symlinks.
                if any(part.is_symlink() for part in (path.parent,path.parent.parent)):
                    raise RuntimeError('Private IPC path contains symlink')
                connection=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                try:connection.connect(str(path))
                except (ConnectionRefusedError,FileNotFoundError):
                    connection.close();time.sleep(.03);continue
                except BaseException:
                    connection.close();raise
            except FileNotFoundError:
                time.sleep(.03);continue
            # Once connected, a bad peer/protocol response is terminal; never retry it.
            with connection:
                pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
                if pid!=expected['pid'] or uid!=os.getuid():raise RuntimeError('Private IPC peer identity mismatch')
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced')
                live();connection.sendall(b'j/version')
                reply=bytearray()
                while True:
                    connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                    chunk=connection.recv(4096)
                    if not chunk:break
                    reply.extend(chunk)
                    if len(reply)>65536:raise RuntimeError('Private IPC version reply too large')
                    if time.monotonic()>=deadline:raise RuntimeError('Private IPC reply timed out')
                version=json.loads(reply.decode('utf-8'))
                if not isinstance(version,dict) or not version:raise RuntimeError('Private IPC version reply must be a nonempty JSON object')
                live()
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced after reply')
                self.evidence.setdefault('ipcReadiness',[]).append({'path':str(path),'socket':before,'peer':{'pid':pid,'uid':uid,'gid':gid},'request':'j/version','replyBytes':len(reply),'replySHA256':hashlib.sha256(reply).hexdigest(),'completeServerEOF':True,'version':version})
                return


class PrivateHyprSession(original.PrivateHyprSession):
    def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
        # Match the hardware renderer verified by the fresh parent foundation.
        dri_prime=dri_prime or 'pci-0000_00_02_0'
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
        self.evidence=self.host.evidence
    def __enter__(self):
        super().__enter__()
        try:
            aq=verify_tuple()['slots']['aquamarine']
            selected={path:value for path,value in self.evidence['hyprlandMaps']['files'].items() if Path(path).name.startswith('libaquamarine.so')}
            if selected!={str(Path(aq['path']).resolve()):aq['sha256']}:raise RuntimeError('Mapped AQ differs from reviewed tuple: '+repr(selected))
            self.evidence['privateAquamarine']['mappedVerified']=True
            self.evidence['privateAquamarine']['mappedFiles']=selected
            return self
        except BaseException:
            self.host.close();raise
