import hashlib,json,pathlib,subprocess,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'qa'/('map-test-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'scope':'Exact official owning method body with real Qt QPointF/QMargins value objects; mock margin supplier, no display/QWaylandWindow construction.'}
 try:
  source=ROOT/'qa/owning-qt-source/qwaylandwindow.cpp';text=source.read_text();start=text.index('QPointF QWaylandWindow::mapFromWlSurface(');end=text.index('\n}',start)+2;method=text[start:end];(out/'owning-method.cpp').write_text(method+'\n');(out/'qwaylandwindow.cpp').write_bytes(source.read_bytes())
  fixture='''#include <QPointF>
#include <QMargins>
#include <cassert>
class QWaylandWindow { QMargins m; public: explicit QWaylandWindow(QMargins v):m(v){} QMargins clientSideMargins()const{return m;} QPointF mapFromWlSurface(const QPointF&)const; };
'''+method+'''
int main(){int count=0;for(auto m:{QMargins(0,0,0,0),QMargins(6,30,7,8),QMargins(1,2,3,4),QMargins(256,512,1024,32)}){QWaylandWindow w(m);auto t=w.mapFromWlSurface(QPointF(0,0));assert(t==QPointF(-m.left(),-m.top()));for(auto p:{QPointF(0,0),QPointF(18,28),QPointF(-0.5,100.25),QPointF(1000,500)}){auto surface=p-t;assert(w.mapFromWlSurface(surface)==p);count++;}}return count==16?0:1;}
'''
  flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core'],text=True).split();controls={}
  for name,body in [('actual',fixture),('unsafe-zero',fixture.replace('surfacePosition.x() - margins.left(), surfacePosition.y() - margins.top()','surfacePosition.x(), surfacePosition.y()')),('unsafe-wrong-sign',fixture.replace('surfacePosition.x() - margins.left(), surfacePosition.y() - margins.top()','surfacePosition.x() + margins.left(), surfacePosition.y() + margins.top()'))]:
   p=out/(name+'.cpp');p.write_text(body);binary=out/name;args=['/usr/bin/c++','-std=c++20','-fPIC','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(binary),*flags]
   # Unsafe zero control keeps the production margins declaration; explicitly use it to compile.
   if name=='unsafe-zero':p.write_text(body.replace('const QMargins margins = clientSideMargins();','const QMargins margins = clientSideMargins();\n    (void)margins;'))
   c=subprocess.run(args,capture_output=True,text=True);(out/(name+'.compile.stderr')).write_text(c.stderr);assert c.returncode==0,name
   run=subprocess.run([str(binary)],capture_output=True,text=True);controls[name]={'returncode':run.returncode,'sha256':sha(binary)};assert (run.returncode==0)==(name=='actual'),name
  report.update(passed=True,owningSourceSHA256=sha(source),methodSHA256=hashlib.sha256(method.encode()).hexdigest(),actualValueCases=16,compiledControls=controls)
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
 (out/'map-test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
