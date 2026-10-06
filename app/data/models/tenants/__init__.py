from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path

package_path = Path(__file__).resolve().parent

for module_info in iter_modules([str(package_path)]):
    if module_info.name.startswith("_") or module_info.name == "base":
        continue

    import_module(f"{__name__}.{module_info.name}")
