"""Compile exact owning CWindow min/max methods; characterize hint handling."""
import hashlib
import json
import resource
import shlex
import shutil
import subprocess
import time
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE = REPO / 'implementation/elm-core-parent-first-anchor-v89/build-1791107301396755104/inputs/candidate/src/desktop/view/Window.cpp'
PAIR = REPO / 'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json'
OUT = ROOT / 'qa' / ('characterization-' + str(time.time_ns()))
OUT.mkdir()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE) == 'ef8e7fc7f2bd9ffa8f0b99b486ca9ea3bc80f8906aa214277ab7b16faf0b445d'
pair = json.loads(PAIR.read_text())
assert pair['passed'] is True
for path, digest in pair['dependencies'].items():
    if '/hyprutils/math/' in path:
        assert sha(Path(path)) == digest, path
library = Path('/usr/lib/libhyprutils.so.0.14.2')
assert sha(library) == pair['linkedLibraries'][str(library)]
source = SOURCE.read_text()
def extract(signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]
methods = '\n\n'.join(extract('std::optional<Vector2D> CWindow::' + name + '()') for name in ('minSize', 'maxSize'))
shutil.copy2(SOURCE, OUT / 'owning-Window.cpp')
(OUT / 'methods.cpp.inc').write_text(methods + '\n')
prefix = r'''
#include <hyprutils/math/Vector2D.hpp>
#include <cmath>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
using Hyprutils::Math::Vector2D;
template<class T> struct Rule { std::optional<T> v; bool hasValue() const {return v.has_value();} T value() const {return v.value();} T valueOrDefault() const {return v.value_or(T{});} };
struct Rules {Rule<Vector2D> minimum,maximum; Rule<bool> disabled; auto minSize(){return minimum;} auto maxSize(){return maximum;} auto noMaxSize(){return disabled;}};
// Already converted protocol observations are stub inputs; conversion is tested
// separately in V162. These methods themselves are verbatim owning source.
struct Top {Vector2D minimum{},maximum{}; Vector2D layoutMinSize(){return minimum;} Vector2D layoutMaxSize(){return maximum;}};
struct Xdg {std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();};
struct Hints {int min_width=0,min_height=0,max_width=0,max_height=0;};
struct Xwayland {std::shared_ptr<Hints> m_sizeHints=std::make_shared<Hints>();};
struct CWindow {
 bool m_isX11=false;
 std::shared_ptr<Rules> m_ruleApplicator=std::make_shared<Rules>();
 std::shared_ptr<Xdg> m_xdgSurface=std::make_shared<Xdg>();
 std::shared_ptr<Xwayland> m_xwaylandSurface=std::make_shared<Xwayland>();
 std::optional<Vector2D> minSize(); std::optional<Vector2D> maxSize();
};
'''
tests = r'''
int main(){
 int checks=0;
 auto check=[&](const char* name,bool value){std::cout<<name<<" "<<value<<"\n";if(!value)throw std::runtime_error(name);++checks;};
 const double unlimited=std::numeric_limits<double>::max();
 CWindow w;
 check("absent-protocol-min-clamped-to-one",w.minSize()==std::optional<Vector2D>{{1,1}});
 check("zero-protocol-max-normalized-unlimited",w.maxSize()==std::optional<Vector2D>{{unlimited,unlimited}});
 w.m_xdgSurface->m_toplevel->minimum={108,42};
 check("GTK-minimum-preserved",w.minSize()==std::optional<Vector2D>{{108,42}});
 w.m_ruleApplicator->minimum.v=Vector2D{130,64};
 check("minimum-rule-overrides-protocol",w.minSize()==std::optional<Vector2D>{{130,64}});
 w.m_ruleApplicator->minimum.v=Vector2D{-8,2};
 check("invalid-rule-minimum-not-validated-by-core",w.minSize()==std::optional<Vector2D>{{-8,2}});
 w.m_ruleApplicator->minimum.v.reset();
 w.m_xdgSurface->m_toplevel->maximum={1,4};
 check("positive-tiny-max-lost-to-layout-sentinel",w.maxSize()==std::optional<Vector2D>{{unlimited,unlimited}});
 w.m_xdgSurface->m_toplevel->maximum={5,100};
 check("five-is-finite-boundary",w.maxSize()==std::optional<Vector2D>{{5,100}});
 w.m_ruleApplicator->maximum.v=Vector2D{900,700};
 w.m_xdgSurface->m_toplevel->maximum={400,300};
 check("rule-can-widen-protocol-maximum",w.maxSize()==std::optional<Vector2D>{{900,700}});
 w.m_ruleApplicator->maximum.v=Vector2D{3,4};
 check("tiny-rule-maximum-bypasses-normalization",w.maxSize()==std::optional<Vector2D>{{3,4}});
 w.m_ruleApplicator->maximum.v=Vector2D{std::numeric_limits<double>::quiet_NaN(),4};
 check("nonfinite-rule-maximum-preserved",std::isnan(w.maxSize()->x));
 w.m_ruleApplicator->maximum.v.reset();w.m_ruleApplicator->disabled.v=true;
 check("noMaxSize-rule-suppresses-protocol-limit",!w.maxSize());
 w.m_ruleApplicator->disabled.v=false;w.m_xdgSurface->m_toplevel.reset();
 check("missing-toplevel-min-is-unavailable",!w.minSize());
 check("missing-toplevel-max-is-unavailable",!w.maxSize());
 std::cout<<"checks="<<checks<<"\n";
}
'''
cpp = OUT / 'characterization.cpp'
cpp.write_text(prefix + '\n' + methods + '\n' + tests)
flags = shlex.split(subprocess.check_output(['pkg-config', '--cflags', '--libs', 'hyprutils'], text=True))
command = ['c++', '-std=c++23', '-Wall', '-Wextra', '-Werror', '-MD', '-MF', str(OUT / 'dependencies.d'), str(cpp), '-o', str(OUT / 'characterization'), *flags]
compile_result = subprocess.run(command, capture_output=True, text=True, timeout=60)
(OUT / 'compile.stdout').write_text(compile_result.stdout)
(OUT / 'compile.stderr').write_text(compile_result.stderr)
report = dict(passed=False, compileExit=compile_result.returncode, command=command, owningSourceSHA256=sha(SOURCE), extractedMethodsSHA256=sha(OUT / 'methods.cpp.inc'), linkedLibrarySHA256=sha(library), scope='Actual extracted owning CWindow bound-hint behavior with stub hint/rule inputs; no eligibility/model/native/release acceptance', nativeAcceptance=False)
if compile_result.returncode == 0:
    result = subprocess.run([str(OUT / 'characterization')], capture_output=True, text=True, timeout=10)
    (OUT / 'checks.stdout').write_text(result.stdout)
    (OUT / 'checks.stderr').write_text(result.stderr)
    report.update(passed=result.returncode == 0, testExit=result.returncode, checks=result.stdout.count(' 1\n'))
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(passed=report['passed'], report=str(OUT / 'report.json'))))
raise SystemExit(0 if report['passed'] else 1)
