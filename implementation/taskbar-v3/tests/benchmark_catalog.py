"""Isolated fixture benchmark; no installed desktop or compositor calls."""
import importlib.util
import json
from pathlib import Path
import statistics
import tempfile
import time
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'taskbar_catalog.py'
spec = importlib.util.spec_from_file_location('taskbar_catalog', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as temp:
    base = Path(temp)
    root = base / 'data'
    applications = root / 'applications'
    applications.mkdir(parents=True)
    for index in range(1000):
        (applications / f'app-{index:04}.desktop').write_text(f'[Desktop Entry]\nType=Application\nName=App {index}\nExec=app-{index} %U\n')
    inventory, groups = module._inventory([root])
    cold, warm = [], []
    module.load_catalog(root, [], base / 'cache')
    for _ in range(10):
        start = time.perf_counter()
        module._parse(groups)
        cold.append(time.perf_counter() - start)
    with patch.object(module, '_parse', wraps=module._parse) as parser:
        for _ in range(10):
            start = time.perf_counter()
            result = module.load_catalog(root, [], base / 'cache')
            warm.append(time.perf_counter() - start)
            assert len(result) == 1000
        parse_calls = parser.call_count
    print(json.dumps({'fixture_entries': 1000, 'iterations': 10, 'warm_parse_calls': parse_calls, 'uncached_parse_median_ms': statistics.median(cold) * 1000, 'warm_full_load_median_ms': statistics.median(warm) * 1000, 'scope': 'synthetic fixture; warm includes two recursive inventories and cache JSON; no compositor/GUI performance claim'}, indent=2))
    assert parse_calls == 0
