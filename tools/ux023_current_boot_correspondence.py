"""Read-only current-boot identity correspondence; historical reports stay immutable."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
BOOT=Path('/proc/sys/kernel/random/boot_id')
REGULAR_FIELDS={'path','sha256','device','inode','size','mode'}
DEVICE_FIELDS={'device','inode','rdev','mode','uid','gid'}

def same_boot(expected,actual):
    if not isinstance(expected,str) or not expected or expected!=actual:raise ValueError('current boot identity differs')

def regular_transition(old,current):
    if set(old)!=REGULAR_FIELDS or set(current)!=REGULAR_FIELDS:raise ValueError('exact regular identity fields required')
    if any(old[k]!=current[k] for k in REGULAR_FIELDS-{'device'}):raise ValueError('only filesystem device numbering may differ')
    if any(type(current[k]) is not int or current[k]<0 for k in ('device','inode','size','mode')):raise ValueError('invalid current regular tuple')

def device_transition(old,current):
    if set(old)!=DEVICE_FIELDS or set(current)!=DEVICE_FIELDS:raise ValueError('exact device identity required')
    if any(old[k]!=current[k] for k in DEVICE_FIELDS-{'inode'}):raise ValueError('only device-node inode may differ')
    if not stat.S_ISCHR(current['mode']):raise ValueError('current graphics node is not character device')

def regular_identity(path):
    path=Path(path)
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        a=os.fstat(fd)
        if not stat.S_ISREG(a.st_mode) or a.st_size>256*1024*1024:raise ValueError('bounded regular artifact required')
        h=hashlib.sha256();total=0
        while True:
            chunk=os.read(fd,min(1024*1024,a.st_size+1-total))
            if not chunk:break
            total+=len(chunk)
            if total>a.st_size:raise ValueError('artifact grew beyond initial size')
            h.update(chunk)
        if total!=a.st_size:raise ValueError('artifact length differs from initial size')
        b=os.fstat(fd)
        if any(getattr(a,k)!=getattr(b,k) for k in ('st_dev','st_ino','st_size','st_mode','st_mtime_ns','st_ctime_ns')):raise ValueError('artifact changed while hashing')
        c=path.lstat()
        if (a.st_dev,a.st_ino)!=(c.st_dev,c.st_ino):raise ValueError('artifact pathname changed')
        return dict(path=str(path),sha256=h.hexdigest(),device=a.st_dev,inode=a.st_ino,size=a.st_size,mode=stat.S_IMODE(a.st_mode))
    finally:os.close(fd)

def device_identity(path):
    s=Path(path).lstat()
    if not stat.S_ISCHR(s.st_mode):raise ValueError('graphics character device required')
    return dict(device=s.st_dev,inode=s.st_ino,rdev=s.st_rdev,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid)

class CurrentBoot:
    def __init__(self,reference,pinned):
        self.reference=reference;self.pinned=pinned
        self.document=json.loads(pinned(reference,4*1024*1024))
        self.check()
    def check(self):
        p=json.loads(self.pinned(self.reference,4*1024*1024))
        if p!=self.document or p.get('schema')!=1 or p.get('disposition')!='accepted' or p.get('scope')!='current-boot-artifact-identity-correspondence' or p.get('reviewer') in (None,'Root','root','build_audit'):raise ValueError('independent current-boot correspondence required')
        same_boot(p.get('currentBootId'),BOOT.read_text().strip())
        scan=json.loads(self.pinned(p['currentScan'],4*1024*1024))
        if scan.get('passed') is not True or scan.get('currentBootId')!=p['currentBootId'] or scan.get('regularArtifacts')!=p['regularArtifacts'] or scan.get('graphicsDevices')!=p['graphicsDevices']:raise ValueError('actual fresh scan does not match independent correspondence')
        return p
    def regular(self,image,source_report):
        p=self.check();path=image['path'];row=p['regularArtifacts'].get(path)
        if row is None or row.get('sourceReport')!=source_report:raise ValueError('artifact absent from source-bound correspondence')
        original=json.loads(self.pinned(source_report,32*1024*1024))
        for part in row['selector']:original=original[part]
        if original!=image:raise ValueError('historical image tuple differs from original report')
        old=dict(path=path,sha256=image['sha256'],device=int(image['device']),inode=int(image['inode']),size=int(image['size']),mode=int(image.get('mode',row['current']['mode'])))
        if row['original']!=old:raise ValueError('original normalized image tuple differs')
        regular_transition(old,row['current'])
        if regular_identity(path)!=row['current']:raise ValueError('current artifact tuple/hash differs')
        self.check()
        return row['current']
    def devices(self,graphics):
        p=self.check()
        if p['originalGraphics']!=graphics or set(p['graphicsDevices'])!=set(graphics['devices']):raise ValueError('exact historical graphics source differs')
        for path,old in graphics['devices'].items():
            row=p['graphicsDevices'][path]
            if row['original']!=old:raise ValueError('historical graphics tuple differs')
            device_transition(old,row['current'])
            if device_identity(path)!=row['current']:raise ValueError('current graphics tuple differs')
        self.check()
        return {k:v['current'] for k,v in p['graphicsDevices'].items()}
    def keyboard_view(self,packet,report):
        p=self.check();value=report['virtualKeyboardBuild'];proof=p['keyboardMetadataCorrespondence']
        if proof.get('report')!=packet['keyboardBuildReport'] or proof.get('compiledSourcePins')!=value['sourcePins']:raise ValueError('full keyboard source correspondence differs')
        current={k:packet['sourceHashes'].get(k) for k in value['sourcePins']}
        if proof.get('currentSourcePins')!=current:raise ValueError('current keyboard source correspondence differs')
        delta=[k for k in current if current[k]!=value['sourcePins'][k]]
        if proof.get('metadataPaths')!=delta or any(not k.startswith('plugins/warlock-contributor/') or '..' in k.split('/') or not k.endswith(('.py','.json','.md')) for k in delta):raise ValueError('keyboard compiled C/XML/tool source changed')
        result=copy.deepcopy(report);result['virtualKeyboardBuild']['sourcePins']=current
        return result

def verify_graphics(current,base,graphics,inventory):
    expected={k:v for k,v in base.GRAPHICS.items() if k!='renderer'}
    expected['files']={k:v for k,v in expected['files'].items() if k!=base.GRAPHICS['renderer']}
    if graphics!=expected or any(inventory.get(k)!=v for k,v in graphics['files'].items()):raise ValueError('explicit unchanged NVIDIA tuple required')
    current.devices(graphics)
    base.regular(graphics['driver']['path'],graphics['driver']['sha256'])
    for path,target in graphics['aliases'].items():
        if str(Path(path).resolve(strict=True))!=target:raise ValueError('graphics alias drift')
    for path,pin in graphics['files'].items():base.regular(path,pin)
    current.devices(graphics)

def graphics_fds(current,base,graphics,proc,birth,image):
    base.check_process(proc,birth,image);devices=current.devices(graphics);result={}
    for fd in Path('/proc/'+str(proc.pid)+'/fd').iterdir():
        try:
            target=os.readlink(fd)
            if target.startswith('/dev/dri/') or target.startswith('/dev/nvidia'):
                if target not in devices:raise ValueError('unqualified graphics device opened')
                s=fd.stat();actual=dict(device=s.st_dev,inode=s.st_ino,rdev=s.st_rdev,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid)
                if actual!=devices[target]:raise ValueError('current graphics descriptor identity differs')
                result[target]=actual
        except FileNotFoundError:continue
    base.check_process(proc,birth,image);current.devices(graphics);return result

def verify_build(current,collector,base,p):
    h=p['host'];report=collector.regular_ref(base,h['buildReport']);collector.validate_build_report(report)
    build=report.get('labwcBuild',{})
    if build.get('target')!='labwc' or build.get('xwayland') is not False or build.get('executed') is not False:raise ValueError('Xwayland-disabled Labwc build binding absent')
    image=build.get('image',{})
    if image.get('path')!=h['labwc'] or image.get('sha256')!=p['hostInputs'][h['labwc']]:raise ValueError('Labwc image/source differs')
    current.regular(image,h['buildReport']);base.regular(h['labwc'],p['hostInputs'][h['labwc']])
    raw=Path(h['labwc']).read_bytes()[:20]
    if raw[:7]!=b'\x7fELF\x02\x01\x01' or raw[18:20]!=b'\xb7\x00':raise ValueError('built host not ELF64LE AArch64')
    inspection=Path(h['labwc']).parent.parent/'inspect.stdout';base.regular(inspection,build['dynamicInspectionSha256']);dynamic=inspection.read_text()
    if '(RPATH)' in dynamic:raise ValueError('DT_RPATH may bypass explicit private loader order')
    runpaths=re.findall(r'\(RUNPATH\).*\[([^]]*)\]',dynamic)
    if len(runpaths)>1 or any(not x or x not in h['libraryDirs'] for value in runpaths for x in value.split(':')):raise ValueError('unqualified runtime loader search path')
    source=collector.regular_ref(base,h['outputToolSource'])
    if source.get('tool')!='wlr-randr' or source.get('version')!='0.5.0' or source.get('jsonCurrentModeReviewed') is not True:raise ValueError('primary output-manager JSON/control correspondence missing')
    if source.get('binary')!={'path':h['outputTool'],'sha256':p['hostInputs'][h['outputTool']]}:raise ValueError('output-manager source correspondence bound to another image')
    base.regular(source['mainSource']['path'],source['mainSource']['sha256']);collector.regular_ref(base,source['signedPackageReceipt']);current.regular(image,h['buildReport']);return report


def provider_qa_ast_correspondence(old_body, new_body, observation=False):
    """Prove the entire old dispatch AST survives exact disjoint menu additions."""
    import ast
    class RemoveMenuAdditions(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name in {'menu_tab_dom_mode', 'menu_tab_dom_inputs', 'menu_focus_build_mode', 'menu_focus_build_spec'} or (observation and node.name in {'observation_elm_variant','observation_inputs'}):
                return None
            return self.generic_visit(node)
        def visit_Assign(self, node):
            if any(isinstance(target, ast.Name) and (target.id.startswith('MENU_FOCUS_BUILD_') or target.id in {'menu_focus_build', 'menu_focus_spec'} or (observation and target.id in {'OBSERVATION_SUPPORT','OBSERVATION_TARGETS'})) for target in node.targets):
                return None
            return self.generic_visit(node)
        def visit_If(self, node):
            if isinstance(node.test, ast.Name) and node.test.id == 'menu_focus_build':
                return None
            if isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name) and (node.test.func.id == 'menu_tab_dom_mode' or (observation and node.test.func.id == 'observation_elm_variant')):
                return None
            return self.generic_visit(node)
        def visit_BoolOp(self, node):
            node = self.generic_visit(node)
            node.values = [value for value in node.values if not (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not) and isinstance(value.operand, ast.Name) and value.operand.id == 'menu_focus_build')]
            return node
        def visit_IfExp(self, node):
            if isinstance(node.test, ast.Name) and node.test.id == 'menu_focus_build':
                return self.visit(node.orelse)
            return self.generic_visit(node)
    old_tree = ast.parse(old_body)
    new_tree = RemoveMenuAdditions().visit(ast.parse(new_body))
    if ast.dump(old_tree, include_attributes=False) != ast.dump(new_tree, include_attributes=False):
        raise ValueError('provider QA dispatch changed outside disjoint reviewed menu additions')


def provider_source_pin(current, reference, build_report, relative, historical_sha):
    """One reviewed QA-dispatch correspondence; no compiled/provider input override."""
    fixed_path = 'tools/qa_cpu.py'
    old_sha = '02e1739d85a75210b70702ed269d11a84c498755e8fc0b567bfe42492a656804'
    new_sha = 'efbd361b826826d9a87681ec9cfcd8ce3ed4b0779d6bf52702f2329eb53e10d8'
    if reference is None or str(relative) != fixed_path:
        return historical_sha
    proof = json.loads(current.pinned(reference, 4*1024*1024))
    if proof.get('schema')==2:new_sha='33c8c99c9810542fda561f883d11fc038c990790ceb123168466c0aeac582ee7'
    if (type(proof.get('schema')) is not int or proof.get('schema') not in (1,2) or proof.get('disposition') != 'accepted'
            or proof.get('scope') != 'ux024-provider-qa-dispatch-source-correspondence'
            or proof.get('reviewer') != 'build_audit'
            or proof.get('buildReport') != build_report
            or build_report.get('sha256') != 'e9ced42313e67a46c1e5f9fa0058b6661b82d2ef3c47ab81925815a9acf23938'
            or historical_sha != old_sha
            or proof.get('historicalSource', {}).get('sha256') != old_sha
            or proof.get('currentSource') != {'path': str(Path('/home/hoskinson/Projects/Warlock') / fixed_path), 'sha256': new_sha}):
        raise ValueError('exact independently reviewed provider QA source correspondence required')
    old_body = current.pinned(proof['historicalSource'], 4*1024*1024)
    new_body = current.pinned(proof['currentSource'], 4*1024*1024)
    if hashlib.sha256(old_body).hexdigest() != old_sha or hashlib.sha256(new_body).hexdigest() != new_sha:
        raise ValueError('actual provider QA source bytes differ')
    provider_qa_ast_correspondence(old_body, new_body, observation=proof['schema']==2)
    current.pinned(proof['correspondenceEvidence'], 4*1024*1024)
    return new_sha


def verify_private_provider(current, collector, base, nested, source_correspondence=None):
    report = collector.regular_ref(base, nested['buildReport'])
    review = collector.regular_ref(base, nested['sourceReview'])
    baseline = collector.regular_ref(base, {'path': str(collector.OVERLAY_BASE_REPORT), 'sha256': collector.OVERLAY_BASE_REPORT_SHA})
    pin = collector.overlay_provider_binding(nested, report, baseline)
    if review.get('disposition') != 'accepted' or review.get('scope') != 'arm-mandatory-wayland-warn-overlay-provider' or review.get('inputs') != nested['inputs'] or (review.get('buildReport') != nested['buildReport']) or (review.get('loggerOverlaySha256') != collector.OVERLAY_SHA):
        raise ValueError('matching independent WARN overlay provider readiness missing')
    base.regular(collector.ROOT / (collector.OVERLAY_SOURCE_REL.removesuffix('/source') + '/inputs.json'), collector.OVERLAY_MANIFEST_SHA)
    for name, pin_sha in report['sourceHashes'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('physical baseline path escaped repository')
        base.regular(collector.ROOT / relative, provider_source_pin(current, source_correspondence, nested['buildReport'], relative, pin_sha))
    for name, pin_sha in report['sourceInputs'].items():
        if not Path(name).is_absolute():
            raise ValueError('overlay build input must be absolute')
        base.regular(name, pin_sha)
    base.regular(collector.OVERLAY_ACTIVE, collector.OVERLAY_SHA)
    for name, pin_sha in nested['inputs'].items():
        base.regular(name, pin_sha)
    image = base.regular(pin['path'], pin['sha256'])
    current.regular(pin,nested['buildReport'])
    root = Path(pin['path']).parent.parent
    actual = report['aquamarineBuild']
    if {p.name for p in (root / 'protocols').iterdir()} != collector.OVERLAY_PROTOCOL_NAMES:
        raise ValueError('generated protocol output membership changed')
    for name, pin_sha in actual['generatedProtocols'].items():
        base.regular(root / 'protocols' / name, pin_sha)
    compile_path = root / 'build/compile_commands.json'
    base.regular(compile_path, actual['compileCommandsSha256'])
    entries = json.loads(compile_path.read_text(), object_pairs_hook=collector.unique)
    if [x for x in entries if x.get('file') == str(collector.ROOT / collector.OVERLAY_LOGGER_REL)] != [actual['loggerCompileEntry']]:
        raise ValueError('actual Logger compilation entry changed')
    inspect = report['commands'][-1]['stdout']
    if inspect['path'] != str(root / 'inspect.stdout'):
        raise ValueError('static inspection path changed')
    base.regular(inspect['path'], inspect['sha256'])
    text = Path(inspect['path']).read_text()
    if 'Library soname: [libaquamarine.so.15]' not in text or '(RPATH)' in text or '(RUNPATH)' in text:
        raise ValueError('fixed static SONAME/search policy changed')
    base.private_soname(nested['libraryDir'], nested['backend'])
    return pin


def derive_schema(packet,historical,live,reuse,pinned):
    reference=reuse['currentSchemaCorrespondence']
    proof=json.loads(pinned(reference,4*1024*1024))
    if (proof.get('schema')!=1 or proof.get('disposition')!='accepted'
            or proof.get('scope')!='ux023-current-foundation-schema-correspondence'
            or proof.get('historicalFoundationPacket')!=packet['foundationPacket']):
        raise ValueError('independent exact current schema correspondence required')
    qualification=json.loads(pinned(proof['qualification'],4*1024*1024))
    schema='/usr/share/glib-2.0/schemas/gschemas.compiled'
    if (qualification.get('disposition')!='accepted'
            or qualification.get('scope')!='ux023-current-foundation-glib-schema-qualification'
            or qualification.get('historicalFoundationSchemaSha256')!=historical['nested']['inputs'].get(schema)
            or qualification.get('currentSchema',{}).get('path')!=schema
            or qualification.get('exactCurrentBytesReproduced') is not True
            or qualification.get('currentSourcesAndCompilerUnchanged') is not True):
        raise ValueError('qualified schema derivation differs from historical/current inputs')
    report=json.loads(pinned(qualification['actualReport'],4*1024*1024))
    inputs=json.loads(pinned(qualification['sourceManifest'],4*1024*1024))
    expected=qualification['currentSchema']['sha256']
    if (report.get('passed') is not True or report.get('kind')!='current-glib-schema-reproducibility'
            or type(report.get('exitCode')) is not int or report['exitCode']!=0
            or report.get('inputManifestSha256')!=qualification['sourceManifest']['sha256']
            or report.get('currentInstalledSha256')!=expected or report.get('reproducedSha256')!=expected
            or report.get('exactCurrentBytesReproduced') is not True or report.get('inputsUnchanged') is not True
            or report.get('sourceFileCount')!=len(inputs['sourceFiles'])):
        raise ValueError('actual current schema compilation not qualified')
    pinned(qualification['actualProtectedTerminal'],4*1024*1024)
    pinned(qualification['qualifiedRecipe'],4*1024*1024)
    pinned(qualification['reproducedImage'],4*1024*1024)
    pinned(qualification['currentSchema'],4*1024*1024)
    if report.get('compiler')!=inputs['compiler']:raise ValueError('schema compiler differs')
    pinned(inputs['compiler'],4*1024*1024)
    directory=Path(inputs['sourceDirectory'])
    if str(directory)!='/usr/share/glib-2.0/schemas':raise ValueError('schema source directory differs')
    actual={str(p) for p in directory.iterdir() if p.is_file() and p.name!='gschemas.compiled'}
    if actual!=set(inputs['sourceFiles']):raise ValueError('schema source membership differs')
    for name,pin in inputs['sourceFiles'].items():pinned({'path':name,'sha256':pin},4*1024*1024)
    result=copy.deepcopy(live)
    if schema not in result['nested']['inputs']:raise ValueError('schema absent from live foundation')
    result['nested']['inputs'][schema]=expected
    provider=json.loads(pinned(proof['currentProviderReadiness'],4*1024*1024))
    if (provider.get('disposition')!='accepted'
            or provider.get('scope')!='arm-mandatory-wayland-warn-overlay-provider'
            or provider.get('inputs')!=result['nested']['inputs']
            or provider.get('buildReport')!=result['nested']['buildReport']):
        raise ValueError('current schema provider readiness is not exact')
    result['nested']['sourceReview']=proof['currentProviderReadiness']
    return result


def generated_context_mapped(current, collector, base, proc, birth, role, image, inventory, required, clock, packet, source_correspondence=None):
    collector.require_generated_role(role, image)
    verify_graphics(current, base, packet['graphics'], packet['hostInputs'])
    if role == 'nested':
        verify_private_provider(current, collector, base, packet['nested'], source_correspondence)
    context_before = collector.owned_context(base, proc, birth, image, clock)
    before, first, first_sha = collector.generated_snapshot(base, proc, clock)
    seen = strict_snapshot_files(current, base, packet['graphics'], before, inventory, required, first, clock)
    middle = collector.owned_context(base, proc, birth, image, clock)
    after, second, second_sha = collector.generated_snapshot(base, proc, clock)
    seen_after = strict_snapshot_files(current, base, packet['graphics'], after, inventory, required, second, clock)
    if first is not None or second is not None:
        nvidia = {str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()), '/usr/lib/libnvidia-eglcore.so.615.78.08'}
        if not nvidia <= set(seen) & set(seen_after):
            raise ValueError('generated object lacks the exact mapped NVIDIA context')
    context_after = collector.owned_context(base, proc, birth, image, clock)
    collector.require_generated_stability(context_before, middle, first, second)
    collector.require_generated_stability(context_before, context_after, first, second)
    verify_graphics(current, base, packet['graphics'], packet['hostInputs'])
    base.left(clock)
    return dict(role=role, identity=context_before, completeBeforeSha256=first_sha, completeAfterSha256=second_sha, mapCountBefore=len(before), mapCountAfter=len(after), staticMappings=seen, staticMappingsAfter=seen_after, generatedObject=second, firstGeneratedObservation=first, ownedBeforeAndAfter=True, generatedContentsRead=False, creatorAttested=False, legacyAnonymousPolicyUnchanged=True)


def strict_snapshot_files(current, base, graphics, rows, inventory, required, generated, clock):
    # Same ordinary file/device checks as frozen base.mapped. Only the already
    # classified exact two ranges are separate. Hash each distinct body per snapshot.
    import mmap
    devices=current.devices(graphics)
    seen = set()
    checked = {}
    exempt = generated['mappings'] if generated is not None else []
    for row in rows:
        base.left(clock)
        if row in exempt:
            continue
        path = row['pathname']
        if path is None or not path.startswith('/'):
            continue  # Preserve legacy anonymous/bracket-map policy; no new allowance.
        device = tuple(int(x,16) for x in row['device'].split(':'))
        if path in devices:
            info = base.device_identity(path)
            if (info != devices[path] or row['inode'] != info['inode']
                    or device != (os.major(info['device']),os.minor(info['device']))):
                raise ValueError('mapped graphics device identity differs')
            seen.add(path)
            continue
        if path.endswith(' (deleted)') or path not in inventory:
            raise ValueError('unqualified mapped file: '+path)
        if path not in checked:
            info = base.regular(path,inventory[path])
            with open(path,'rb') as stream:
                with mmap.mmap(stream.fileno(),min(4096,info.st_size),access=mmap.ACCESS_READ):
                    local = [line.split(maxsplit=5) for line in Path('/proc/self/maps').read_text().splitlines()]
                    if not any(len(x)==6 and x[5]==path
                               and tuple(int(y,16) for y in x[3].split(':'))==device
                               and int(x[4])==row['inode'] for x in local):
                        raise ValueError('mapped device/inode differs')
            checked[path] = (info, device)
        info, verified_map_device = checked[path]
        if row['inode']!=info.st_ino or device!=verified_map_device:
            raise ValueError('mapped regular-file identity differs')
        seen.add(path)
    if not set(required)<=seen:
        raise ValueError('required pinned provider not mapped')
    current.devices(graphics)
    base.left(clock)
    return sorted(seen)
