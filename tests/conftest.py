import os
import sys

# Ensure project src is on sys.path so tests can import modules as 'models', 'gui', etc.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def pytest_configure(config):
    # optional: expose the src root to tests
    config.src_root = ROOT
