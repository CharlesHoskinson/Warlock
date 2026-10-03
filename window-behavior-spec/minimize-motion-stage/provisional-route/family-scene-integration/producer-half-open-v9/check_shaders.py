"""Offline GLSL parser/compiler check; never creates EGL/GPU/Wayland resources."""
import ast
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent


def main():
    header=(HERE/'QuantizedOver.hpp').read_text()
    fragment=re.search(r'fragment=R"GLSL\((.*?)\)GLSL";',header,re.S)[1]
    vertex=ast.literal_eval(re.search(r'copyVertex=("[^"\n]*");',header)[1])
    copy=ast.literal_eval(re.search(r'copyFragment=("[^"\n]*");',header)[1])
    with tempfile.TemporaryDirectory(prefix='owned-coverage-glsl-') as directory:
        for name,source in (('coverage.frag',fragment),('fullscreen.vert',vertex),('copy.frag',copy)):
            path=Path(directory)/name;path.write_text('#version 100\n'+source+'\n')
            result=subprocess.run(['glslangValidator',str(path)],capture_output=True,text=True,timeout=15)
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print('3 complete ES100 coverage/vertex/copy shaders validated offline; no GPU execution')


if __name__=='__main__':main()
