# -*- coding: utf-8 -*-
import sys
import os
import importlib.util

_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.join(_this_dir, 'backend')

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

os.chdir(_backend_dir)

_backend_app_path = os.path.join(_backend_dir, 'app.py')
_spec = importlib.util.spec_from_file_location('backend_main_app', _backend_app_path)
_backend_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_backend_mod)

app = _backend_mod.app
serve_frontend = _backend_mod.serve_frontend
health_check = _backend_mod.health_check

if __name__ == '__main__':
    import uvicorn
    from config import settings
    uvicorn.run('app:app', host='0.0.0.0', port=settings.PORT, reload=settings.DEBUG)
