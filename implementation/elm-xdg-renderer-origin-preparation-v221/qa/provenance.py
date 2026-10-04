"""Read-only archive/source identity preparation, not compilation or native proof."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
CORE=REPO/'implementation/elm-core-parent-first-anchor-v89/build-1791107301396755104'
GEOM=REPO/'implementation/elm-geometry-monitor-core-v73/core/build-1791106255338249967'
ELEMENT=REPO/'implementation/elm-surface-facts-v20/build-1791065974847738580'
ORIGINAL=REPO/'implementation/maximized-stack-v1/native-core-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'qa'/('provenance-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[],'inputs':{},'members':{},'sourceByteUncertainty':[]}
    def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
    def bind(p):report['inputs'][str(p)]=sha(p);return p
    try:
        reports={name:json.loads(bind(path/'report.json').read_text()) for name,path in [('89',CORE),('73',GEOM),('20',ELEMENT)]}
        payloads=json.loads(bind(CORE/'new-archive-payloads.json').read_text())
        archive=bind(CORE/'libhyprland_lib.a');check('exact-owning-archive',sha(archive)==reports['89']['archiveSHA256'])
        for member in ('Renderer.cpp.o','ElementRenderer.cpp.o','SurfacePassElement.cpp.o'):
            row=next(r for r in payloads if r['name']==member)
            data=subprocess.run(['/usr/bin/ar','p',str(archive),member],check=True,capture_output=True).stdout
            actual=hashlib.sha256(data).hexdigest();check('actual-archive-payload-'+member,actual==row['sha256'])
            report['members'][member]=row
        source=bind(GEOM/'owning-headers/src/render/Renderer.cpp');object_path=bind(GEOM/'Renderer.cpp.o')
        check('Renderer-exact-captured-object',sha(object_path)==report['members']['Renderer.cpp.o']['sha256'])
        origin=reports['73']['sourceOrigins']['src/render/Renderer.cpp']
        check('Renderer-captured-source-origin',sha(source)==origin['selectedSourceSHA256'])
        source2=bind(ELEMENT/'inputs/src/render/ElementRenderer.cpp');object2=bind(ELEMENT/'ElementRenderer.cpp.o')
        check('ElementRenderer-exact-captured-object',sha(object2)==report['members']['ElementRenderer.cpp.o']['sha256'])
        check('ElementRenderer-captured-source',sha(source2)==reports['20']['sources']['src/render/ElementRenderer.cpp'])
        surface_object=bind(ORIGINAL/'build/CMakeFiles/hyprland_lib.dir/src/render/pass/SurfacePassElement.cpp.o')
        surface_source=bind(ORIGINAL/'src/render/pass/SurfacePassElement.cpp')
        check('SurfacePass-original-object-identity',sha(surface_object)==report['members']['SurfacePassElement.cpp.o']['sha256'])
        report['sourceByteUncertainty'].append({'member':'SurfacePassElement.cpp.o','currentSource':str(surface_source),'currentSHA256':sha(surface_source),'historicalSourceBytesProven':False,'policy':'fresh source+owning dependency capture/rebuild required, not historical source identity claim'})
        report['commands']={name:[r for r in reports[version]['commands'] if r['name']==command][0] for name,version,command in [('Renderer','73','Renderer-compile'),('ElementRenderer','20','ElementRenderer-compile')]}
        for name,version in [('Renderer','73'),('ElementRenderer','20')]:
            current_matches=0;changed=[];missing=[]
            for path,value in reports[version]['dependencies'].items():
                p=Path(path)
                if not p.exists():missing.append(path)
                elif sha(p)!=value:changed.append(path)
                else:current_matches+=1
            report.setdefault('historicalDependencyAvailability',{})[name]={'recorded':len(reports[version]['dependencies']),'unchangedCurrent':current_matches,'changedCurrent':changed,'missingCurrent':missing,'qualification':'historical recorded closure only; changed current paths must not be substituted into a claim of historical source qualification'}
        database=bind(ORIGINAL/'build/compile_commands.json');commands=json.loads(database.read_text())
        report['SurfacePassOriginalCompileEntry']=next(c for c in commands if c['file'].endswith('/src/render/pass/SurfacePassElement.cpp'))
        report['compileDatabaseMatchesCurrent89Recorded']=sha(database)==reports['89']['compileDatabaseSHA256']
        for name in ('src/render/ElementRenderer.hpp','src/render/Renderer.hpp','src/render/pass/SurfacePassElement.hpp','src/desktop/view/WLSurface.hpp','src/protocols/core/Compositor.hpp','src/version.h'):
            p=bind(CORE/'owning-headers'/name);check('actual-owning-header-'+name,sha(p)==reports['89']['owningHeaders'][name])
        prior=bind(REPO/'implementation/elm-draw-identity-v19/build-1791065098491183126/ElementRenderer.cpp.o')
        check('V19-object-not-current-owning',sha(prior)!=report['members']['ElementRenderer.cpp.o']['sha256'])
        for path in (ROOT/'REQUIREMENTS.md',ROOT/'PROPOSAL.md',Path(__file__),REPO/'implementation/elm-xdg-coordinate-design-held-v465/HANDOFF.md'):bind(path)
        context=json.loads(bind(ROOT/'context-snapshot.json').read_text())
        for name,value in context['files'].items():
            path=bind(Path(name));check('captured-primary-context-'+path.name,sha(path)==value)
        bind(Path('/usr/bin/ar'))
        report['passed']=True
    except Exception as error:report['error']=repr(error)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
