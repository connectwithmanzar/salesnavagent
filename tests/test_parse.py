from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from parse import company_mix, list_id, page_url, safe_filename, sn_lead_id, split_name, to_public_url


class ParseTests(unittest.TestCase):
    def test_list_id(self) -> None:
        url = "https://www.linkedin.com/sales/lists/people/7514252219261751296?sortCriteria=LAST_ACTIVITY"
        self.assertEqual(list_id(url), "7514252219261751296")

    def test_rejects_search_url(self) -> None:
        with self.assertRaises(ValueError):
            list_id("https://www.linkedin.com/sales/search/people?query=retail")

    def test_page_url_adds_page(self) -> None:
        url = "https://www.linkedin.com/sales/lists/people/123"
        out = page_url(url, 2)
        self.assertIn("page=2", out)
        self.assertIn("sortCriteria=LAST_ACTIVITY", out)

    def test_split_name(self) -> None:
        self.assertEqual(split_name("Ada Lovelace"), ("Ada", "Lovelace"))
        self.assertEqual(split_name("Prince"), ("Prince", ""))
        self.assertEqual(split_name(""), ("", ""))

    def test_safe_filename(self) -> None:
        self.assertEqual(safe_filename("Black Forest Space"), "Black_Forest_Space")
        self.assertEqual(safe_filename("???"), "SN_people_list")

    def test_to_public_url(self) -> None:
        self.assertEqual(
            to_public_url("https://www.linkedin.com/in/fabian-kohler?miniProfile=1"),
            "https://www.linkedin.com/in/fabian-kohler",
        )
        self.assertEqual(
            to_public_url("https://www.linkedin.com/sales/lead/ACwAADMuhsQB,NAME_SEARCH,E2cm"),
            "",
        )

    def test_sn_lead_id(self) -> None:
        self.assertEqual(
            sn_lead_id("https://www.linkedin.com/sales/lead/ACwAADMuhsQB,NAME_SEARCH,E2cm"),
            "ACwAADMuhsQB",
        )

    def test_company_mix(self) -> None:
        leads = [
            {"company": "dm"},
            {"company": "EDEKA"},
            {"company": "dm"},
        ]
        mix = company_mix(leads)
        self.assertIn("dm (2)", mix)
        self.assertIn("EDEKA (1)", mix)


if __name__ == "__main__":
    unittest.main()
