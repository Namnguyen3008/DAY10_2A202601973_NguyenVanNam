from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pipelines.phase1 import main


if __name__ == "__main__":
    main()

