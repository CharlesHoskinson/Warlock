"""Read retained images; never runs renderer, EGL, Wayland, or alters evidence."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ATTEMPT=Path('/home/hoskinson/window-integration-qa/family-raster-default-readback-v10/attempt-1')
sys.dont_write_bytecode=True
sys.path.insert(0,str(ATTEMPT.parent))
from raster_oracle import png_rgba,premultiply,render,compare
from verify_quantized_over import coverage_geometry


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target=HERE/'retained-v10-coverage-attribution.json'
    if target.exists():raise SystemExit('fresh attribution destination required')
    paths=[ATTEMPT/'fixture-1-ORACLE-SECOND.json',ATTEMPT/'causal-1-ORACLE-SECOND-0.json',ATTEMPT/'causal-1-ORACLE-SECOND-1.json',ATTEMPT/'causal-1-ORACLE-SECOND-2.json',ATTEMPT/'report.json',ATTEMPT/'producer-events.jsonl',ATTEMPT.parent/'raster_oracle.py']
    fixture=json.loads(paths[0].read_text())
    observed=json.loads(paths[2].read_text());record=observed['observation']
    members=[]
    for source,member in zip(fixture['members'],record['members'],strict=True):
        path=Path(source['path']);paths.append(path)
        decoded=png_rgba(path,source['digest'],tuple(source['pixels']))
        members.append({'pixels':source['pixels'],'premultiplied':premultiply(decoded),'rectangle':member['rectangle']})
    output=fixture['output'];width,height=output['bufferWidth'],output['bufferHeight']
    expected=render(output,members[:2],background=(0,0,0,0))
    previous_record=json.loads(paths[1].read_text())['observation']
    current_path=ATTEMPT/'owned-readbacks'/record['rgbaFilename']
    previous_path=ATTEMPT/'owned-readbacks'/previous_record['rgbaFilename']
    paths.extend([current_path,previous_path,ATTEMPT/'owned-readbacks'/record['nativeRGBAFilename']])
    def decode(path):return subprocess.check_output(['magick',str(path),'-depth','8','rgba:-'])
    actual,previous=decode(current_path),decode(previous_path)
    comparison=compare(actual,expected,width,height,fixture['channelTolerance'])
    assert comparison==observed['comparison']['RGBA']
    bad=[i//4 for i in range(0,len(actual),4) if max(abs(actual[i+c]-expected[i+c]) for c in range(4))>fixture['channelTolerance']]
    assert len(bad)==83 and {i//width for i in bad}=={157}
    assert min(i%width for i in bad)==20 and max(i%width for i in bad)==102
    assert all(actual[i*4:i*4+4]==previous[i*4:i*4+4] for i in bad)
    logical={k:output[k] for k in ('x','y','width','height')}
    coverage,sample=coverage_geometry(record['members'][1]['rectangle'],logical,[width,height])
    assert coverage==[20,157,103,215] and sample[1]==157.5
    result={'scope':'read-only immutable V10 first-divergent-prefix attribution; no native/GPU launch or new pixel acceptance',
        'comparison':comparison,'firstDivergentPrefix':2,'firstDivergentOutput':'ORACLE-SECOND','progress':.35,
        'badRows':dict(Counter(i//width for i in bad)),'badXRange':[20,102],'allBadPixelsEqualPreviousPrefix':True,
        'childRectangle':record['members'][1]['rectangle'],'childProjectedTopEdge':sample[1],
        'candidateCoverageBounds':coverage,'originalOracleUnchanged':True,'originalToleranceUnchanged':True,
        'conclusion':'child top half-center row omitted by polygon raster coverage; all other prefix2 pixels satisfy original tolerance',
        'remaining':'fresh actual unchanged full 44-image native campaign for explicit coverage candidate',
        'inputs':{str(path):sha(path) for path in paths}}
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'report':str(target),'sha256':sha(target),'badPixels':len(bad),'allPreviousPrefix':True}))


if __name__=='__main__':main()
