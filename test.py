import unittest
import price_behavior as pb
import pandas

class TestPriceBehavior(unittest.TestCase):
    def test_read_quotes(self):
        self.assertIsInstance(pb.read_quotes("C"), pandas.DataFrame)

    def test_invalid_ticker(self):
        data = ("TWTR1", "intraprice_open", 0.5, "1900", True)
        self.assertEqual(pb.run(*data), None)

    def test_invalid_range(self):
        data = ("TWTR", "intra_open", 0.5, "1900", True)
        self.assertEqual(pb.run(*data), None)

    def test_invalid_boundary(self):
        data = ("TWTR", "intraprice_open", -0.5, "1900", True)
        self.assertEqual(pb.run(*data), None)

    def test_invalid_intra_time_before(self):
        data = ("MSFT", "intraprice_open", 0.5, "1200", True)
        self.assertEqual(pb.run(*data), None)

    def test_invalid_intra_time_after(self):
        data = ("TWTR", "intraprice_open", 0.5, "2300", True)
        self.assertEqual(pb.run(*data), None)

    def test_intra_time_false(self):
        data = ("AMAT", "open_priorclose", 0.5, False, False)
        self.assertEqual(pb.run(*data)["min_price_change"], -3.81)

    def test_open_priorclose(self):
        data = ("AMAT", "open_priorclose", 0.5, "1755", False)
        self.assertEqual(pb.run(*data)["min_price_change"], -3.81)

    def test_close_open(self):
        data = ("MU", "close_open", 0.5, "1800", False)
        self.assertEqual(pb.run(*data)["std"], 1.252)

    def test_close_priorclose(self):
        data = ("C", "close_priorclose", 1.0, "2130", True)
        self.assertEqual(pb.run(*data)["obs_btw_boundaries"], 181)

    def test_intraprice_open(self):
        data = ("JD", "intraprice_open", 0.5, "1835", False)
        self.assertEqual(pb.run(*data)["mean"], -0.069)

    def test_valid_params(self):
        data = ("TWTR", "intraprice_open", 0.5, "1900", True)
        self.assertEqual(pb.run(*data)["all_obs_number"], 248)


if __name__ == "__main__":
    unittest.main()
