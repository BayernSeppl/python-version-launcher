import csv
import tempfile
import unittest
from pathlib import Path

import lotto_app


class LottoDataTests(unittest.TestCase):
    def test_csv_parser_with_german_date_and_semicolon(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "draws.csv"
            path.write_text("Datum;Zahl1;Zahl2;Zahl3;Zahl4;Zahl5;Zahl6\n03.01.2025;4;9;17;23;35;41\n", encoding="utf-8-sig")
            rows, skipped = lotto_app.read_csv_draws(path)
            self.assertEqual(rows, [("2025-01-03", [4, 9, 17, 23, 35, 41])])
            self.assertEqual(skipped, 0)

    def test_csv_skips_header_and_extra_numeric_column(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "draws.csv"
            path.write_text("date,n1,n2,n3,n4,n5,n6,bonus\n2025-01-03,4,9,17,23,35,41,7\n", encoding="utf-8")
            rows, skipped = lotto_app.read_csv_draws(path)
            self.assertEqual(rows, [])
            self.assertEqual(skipped, 2)

    def test_number_stats_for_recent_window_and_gap(self):
        draws = [("2025-01-01", [1, 2, 3, 4, 5, 6]), ("2025-01-08", [1, 7, 8, 9, 10, 11])]
        stats = lotto_app.calculate_stats(draws, 1)
        self.assertEqual(stats[1]["total"], 2)
        self.assertEqual(stats[1]["recent"], 1)
        self.assertEqual(stats[2]["gap"], 1)

    def test_ticket_generation_and_validation(self):
        tickets = lotto_app.build_tips([], 5, 90, 190, 1, 5, False)
        self.assertEqual(len(tickets), 5)
        self.assertEqual(len({tuple(ticket) for ticket in tickets}), 5)
        self.assertTrue(all(90 <= sum(ticket) <= 190 for ticket in tickets))

    def test_bad_filter_rejected(self):
        with self.assertRaises(ValueError):
            lotto_app.build_tips([], 1, 200, 100, 1, 5, False)


if __name__ == "__main__":
    unittest.main()
