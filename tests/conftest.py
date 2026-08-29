"""Test-path setup for the ASOC correctness gate."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"

# Put the repository root first so imports such as
# ``src.generate_phase6_artifacts`` always resolve to this checkout, while
# keeping direct historical imports from modules inside ``src/`` working.
for path in (SRC_ROOT, ROOT):
    value = str(path)
    if value in sys.path:
        sys.path.remove(value)
    sys.path.insert(0, value)
