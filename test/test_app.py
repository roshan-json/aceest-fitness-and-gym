import os
import sys

# Ensure src is importable during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import app

def test_dummy():
    assert 1 == 1
