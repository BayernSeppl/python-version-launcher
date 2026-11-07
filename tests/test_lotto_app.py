import tempfile
import unittest
from pathlib import Path

import lotto_app


class LottoAppTests(unittest.TestCase):
    def test_stats_frequency_and_last_seen(self):
        draws = [[1, 2, 3, 4, 5, 6], [1, 7, 8, 9, 10, 11], [2, 12, 13, 14, 15, 16]]
        stats = lotto_app.number_statistics(draws)
        self.assertEqual(stats[1]["count"], 2)
        self.assertEqual(stats[1]["draws_ago"], 1)
        self.assertEqual(stats[6]["draws_ago"], 2)

    def test_csv_import_skips_header_and_reads_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draws.csv"
            path.write_text("Datum;A;B;C;D;E;F\n2025-01-01;1;2;3;4;5;49\n", encoding="utf-8")
            self.assertEqual(lotto_app.parse_draw_csv(path), [[1, 2, 3, 4, 5, 49]])

    def test_csv_rejects_bad_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draws.csv"
            path.write_text("1;2;3;4;5;5\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                lotto_app.parse_draw_csv(path)

    def test_tickets_are_unique_and_respect_filters(self):
        tickets = lotto_app.create_tickets([], 8, 90, 190, 1, 5, "Zufällig")
        self.assertEqual(len(tickets), 8)
        self.assertEqual(len({tuple(ticket) for ticket in tickets}), 8)
        for ticket in tickets:
            self.assertTrue(lotto_app.ticket_is_valid(ticket, 90, 190, 1, 5))

    def test_rejects_invalid_ticket_count(self):
        with self.assertRaises(ValueError):
            lotto_app.create_tickets([], 0, 90, 190, 1, 5, "Zufällig")


if __name__ == "__main__":
    unittest.main()
