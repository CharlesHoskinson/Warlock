import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('owned_activation_supervisor',Path(__file__).with_name('activation-supervisor.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
identity=module.identity
live=module.live
