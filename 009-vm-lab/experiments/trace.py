# SPDX-License-Identifier: MIT
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vm", root / "materials/vm.py")
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)
source = Path(sys.argv[1]).read_text(encoding="utf-8")
print(json.dumps(vm.run(source, int(sys.argv[2]) if len(sys.argv) > 2 else 1000), indent=2))
