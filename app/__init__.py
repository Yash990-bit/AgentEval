import importlib, sys
import os

# Package initialization for test imports
# Extend this package's __path__ to include the actual implementation located in backend/app
backend_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
if os.path.isdir(backend_app_path):
    __path__.append(backend_app_path)

# Load the actual backend app package
_backend = importlib.import_module('backend.app')
# Expose its path so submodule imports work
__path__ = _backend.__path__
# Populate globals with the backend app's attributes
globals().update(_backend.__dict__)
# Ensure the module name resolves to the backend app package

