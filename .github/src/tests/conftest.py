import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / ".github" / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

