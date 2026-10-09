from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from human import CHECKPOINT_RE


class HumanTests(unittest.TestCase):
    def test_checkpoint_phrases(self) -> None:
        pattern = re.compile(CHECKPOINT_RE, re.I)
        self.assertTrue(pattern.search("https://www.linkedin.com/checkpoint/challenges"))
        self.assertTrue(pattern.search("We detected unusual activity on your account"))
        self.assertFalse(pattern.search("Lead Lists Black Forest Space"))


if __name__ == "__main__":
    unittest.main()
