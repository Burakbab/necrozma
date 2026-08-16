import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importing the bundle registers core.*, agents.*, loop.*, constitution as
# real importable modules via its custom meta-path finder (see
# evotrader_bundle.py's _install()). Every test file needs this to have
# happened before it can `from core.genome import Genome` etc. Doing it once
# here, at collection time, is enough for the whole session.
import evotrader_bundle  # noqa: E402,F401
