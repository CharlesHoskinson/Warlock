#!/usr/bin/env python3
"""Local, source-bound BGE retrieval; CUDA indexes and CPU worker queries share data."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
BASE = Path.home() / '.local/share/warlock-graph'
GPU = BASE / 'gpu'
GRAPH = BASE / 'graphify-out/graph.json'
GRAPH_PY = Path.home() / '.local/share/uv/tools/graphifyy/bin/python'
STATE = 'docs/warlock-build-loop/v2/STATE.json'
EXCLUDED = {'elm-stuff', 'dist-newstyle', 'build', 'node_modules', '.git', 'vendor'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.gpu-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def graph():
    raw = GRAPH.read_bytes()
    obj = json.loads(raw)
    active = json.loads((ROOT / STATE).read_bytes())['activeContributorRecord']
    if not isinstance(active, str) or not active.startswith('.warlock-contributor/') or '..' in Path(active).parts:
        raise RuntimeError('Invalid active contributor record')
    current_paths = {p.relative_to(ROOT).as_posix()
                     for p in (ROOT / 'implementation/warlock').rglob('*')
                     if p.is_file() and p.suffix in {'.elm', '.hs', '.hsc', '.qnt'}
                     and not EXCLUDED.intersection(p.parts)}
    current_paths.update({'docs/elm-roadmap/requirements.json', active, STATE})
    if current_paths != set(obj['graph']['input_sha256']):
        raise RuntimeError('Graph input set changed; run warlock-ctx update first')
    for name, expected in obj['graph']['input_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha(path.read_bytes()) != expected:
            raise RuntimeError('Graph stale: ' + name + '; run warlock-ctx update first')
    if sha((ROOT / 'tools/warlock_ctx.py').read_bytes()) != obj['graph']['extractor_sha256']:
        raise RuntimeError('Graph extractor changed; run warlock-ctx update first')
    return raw, obj


def verified_model(lock_bytes):
    lock = json.loads(lock_bytes)
    model_path = Path(lock['path'])
    expected = {item['path'] for item in lock['files']}
    actual = {p.relative_to(model_path).as_posix() for p in model_path.rglob('*') if p.is_file()}
    if actual != expected or any(p.is_symlink() for p in model_path.rglob('*')):
        raise RuntimeError('Model directory contains unpinned files or symlinks')
    for item in lock['files']:
        if sha((model_path / item['path']).read_bytes()) != item['sha256']:
            raise RuntimeError('Model hash mismatch: ' + item['path'])
    return lock, model_path


def encoder(device, lock_bytes):
    import torch
    from transformers import AutoModel, AutoTokenizer
    torch.set_num_threads(2)
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable in this process; root can index, workers may query with --device cpu')
    lock, model_path = verified_model(lock_bytes)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=False)
    model = AutoModel.from_pretrained(model_path, local_files_only=True, trust_remote_code=False).eval().to(device)

    def encode(texts):
        batches = []
        with torch.inference_mode():
            for start in range(0, len(texts), 16):
                batch = tokenizer(texts[start:start + 16], padding=True, truncation=True,
                                  max_length=256, return_tensors='pt').to(device)
                result = model(**batch).last_hidden_state[:, 0].float()
                batches.append(torch.nn.functional.normalize(result, p=2, dim=1))
        vectors = torch.cat(batches)
        if not torch.isfinite(vectors).all():
            raise RuntimeError('Nonfinite embeddings')
        return vectors
    return torch, lock, encode


def index(device):
    from safetensors.torch import save
    raw, obj = graph()
    helper_bytes = Path(__file__).read_bytes()
    lock_bytes = (GPU / 'model-lock.json').read_bytes()
    nodes = [n for n in obj['nodes'] if n.get('kind') in
             {'file', 'module', 'declaration', 'import', 'requirement', 'scenario'}]
    texts = [' '.join(str(n.get(k, '')) for k in ('label', 'text', 'source_file')) for n in nodes]
    started = time.monotonic()
    torch, lock, encode = encoder(device, lock_bytes)
    vectors = encode(texts)
    torch.testing.assert_close(vectors.norm(dim=1), torch.ones(len(nodes), device=device))
    encoded = save({'embeddings': vectors.cpu().contiguous()})
    fingerprint = sha(encoded)
    output = GPU / (fingerprint + '.safetensors')
    if graph()[0] != raw:
        raise RuntimeError('Graph changed during embedding; refusing publication')
    if (Path(__file__).read_bytes() != helper_bytes or
            (GPU / 'model-lock.json').read_bytes() != lock_bytes):
        raise RuntimeError('Helper or model lock changed during embedding')
    verified_model(lock_bytes)
    report = {'graphSha256': sha(raw), 'helperSha256': sha(helper_bytes),
              'modelLockSha256': sha(lock_bytes),
              'revision': lock['revision'], 'device': device,
              'gpu': torch.cuda.get_device_name(0) if device == 'cuda' else None,
              'torch': torch.__version__, 'cuda': torch.version.cuda,
              'count': len(nodes), 'dimensions': vectors.shape[1], 'seconds': time.monotonic() - started,
              'tensorFile': output.name, 'tensorSha256': fingerprint,
              'nodeIds': [n['id'] for n in nodes]}
    atomic(output, encoded)
    atomic(GPU / 'index.json', (json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps({k: v for k, v in report.items() if k != 'nodeIds'}, indent=2))


def rank(question, device):
    from safetensors.torch import load
    raw, obj = graph()
    helper_bytes = Path(__file__).read_bytes()
    lock_bytes = (GPU / 'model-lock.json').read_bytes()
    report = json.loads((GPU / 'index.json').read_bytes())
    if (report['graphSha256'] != sha(raw) or
            report['helperSha256'] != sha(helper_bytes) or
            report['modelLockSha256'] != sha(lock_bytes)):
        raise RuntimeError('Embedding index stale; root must run warlock-gpu index')
    torch, _, encode = encoder(device, lock_bytes)
    encoded = (GPU / report['tensorFile']).read_bytes()
    if sha(encoded) != report['tensorSha256']:
        raise RuntimeError('Embedding tensor hash mismatch')
    vectors = load(encoded)['embeddings'].to(device)
    query = encode(['Represent this sentence for searching relevant passages: ' + question])
    scores, positions = (vectors @ query[0]).topk(min(8, len(vectors)))
    by_id = {n['id']: n for n in obj['nodes']}
    rows = []
    for value, position in zip(scores.tolist(), positions.tolist()):
        nid = report['nodeIds'][position]
        n = by_id[nid]
        rows.append({'id': nid, 'score': value, 'label': n['label'],
                     'source': n.get('source_file'), 'location': n.get('source_location')})
    if (graph()[0] != raw or Path(__file__).read_bytes() != helper_bytes or
            (GPU / 'model-lock.json').read_bytes() != lock_bytes):
        raise RuntimeError('Inputs changed during query; refusing stale results')
    verified_model(lock_bytes)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    parser.add_argument('--budget', type=int, default=1500)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('index')
    for name in ('rank', 'hq'):
        sub.add_parser(name).add_argument('question')
    args = parser.parse_args()
    if args.command == 'index':
        GPU.mkdir(parents=True, exist_ok=True)
    # Workers need only read access; CPU queries can share the published index.
    # CUDA operations remain serialized. No daemon, privilege or sandbox changes.
    mode = 'a' if args.command == 'index' else 'rb'
    with (GPU / 'operation.lock').open(mode) as guard:
        shared = args.device == 'cpu' and args.command != 'index'
        fcntl.flock(guard, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        if args.command == 'index':
            index(args.device)
            return
        rows = rank(args.question, args.device)
        if args.command == 'rank':
            print(json.dumps(rows, indent=2))
            return
        code = '''import hashlib,json,sys
from pathlib import Path
from graphify.paths import load_node_link_graph
from graphify.serve import _query_graph_text
p=json.loads(sys.stdin.read())
raw=Path(p['graph']).read_bytes()
if hashlib.sha256(raw).hexdigest()!=p['graphSha256']:
    raise SystemExit('Graph changed after semantic ranking; rerun query')
g=load_node_link_graph(json.loads(raw)).to_undirected()
print(_query_graph_text(g,p['question'],depth=2,token_budget=p['budget'],seeds=p['seeds'],graph_path=p['graph']))
'''
        report = json.loads((GPU / 'index.json').read_bytes())
        payload = {'graph': str(GRAPH), 'question': args.question,
                   'graphSha256': report['graphSha256'],
                   'budget': max(100, min(args.budget, 4000)), 'seeds': [n['id'] for n in rows[:3]]}
        result = subprocess.run([str(GRAPH_PY), '-c', code], input=json.dumps(payload),
                                text=True, check=True, capture_output=True)
        if (sha(graph()[0]) != report['graphSha256'] or
                sha(Path(__file__).read_bytes()) != report['helperSha256'] or
                sha((GPU / 'model-lock.json').read_bytes()) != report['modelLockSha256']):
            raise RuntimeError('Inputs changed during traversal; refusing stale output')
        verified_model((GPU / 'model-lock.json').read_bytes())
        print('BGE semantic seeds on ' + args.device + '; Graphify traversal on CPU. Verify source.')
        print(result.stdout, end='')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as error:
        print('warlock-gpu: ' + str(error), file=sys.stderr)
        sys.exit(1)
