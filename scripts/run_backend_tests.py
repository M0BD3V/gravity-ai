from __future__ import annotations

import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND_SRC = ROOT / "backend" / "src"

sys.path.insert(0, str(BACKEND_SRC))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests" / "backend"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

