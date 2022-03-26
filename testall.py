import importlib
import pkgutil
import tests

modules = [i.name for i in pkgutil.iter_modules(['tests'])]
[importlib.import_module(f'tests.{m}') for m in modules]
[eval(f'tests.{m}.test()') for m in modules]
