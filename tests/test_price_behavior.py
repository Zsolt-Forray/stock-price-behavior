#!/usr/bin/python3


"""
Test for the stock price behavior analyzing tool
"""


__author__  = 'Zsolt Forray'
__license__ = 'MIT'
__version__ = '0.0.1'
__date__    = '18/12/2019'
__status__  = 'Development'


from context import price_behavior
import unittest


class TestQuotesData(unittest.TestCase):
    def setUp(self):
        ticker = "AMAT"
        self.quotes = price_behavior.QuotesData(ticker)

    def test_read_quotes(self):
        self.quotes.read_quotes()
        # Verify the quotes are loaded
        self.assertIsNotNone(self.quotes.raw_intra_quotes_df)

    def test_adjust_trading_time(self):
        self.quotes.adjust_trading_time()
        # Verify the AdjTime column exists
        self.assertIsNotNone(self.quotes.raw_intra_quotes_df.AdjTime)

    def test_create_adjusted_quotes(self):
        self.quotes.create_adjusted_quotes()
        # Verify the adjusted quotes dataframe created
        self.assertIsNotNone(self.quotes.intra_quotes_df)


class TestPriceData(unittest.TestCase):
    def setUp(self):
        ticker = "MU"
        intra_time = "1800"
        self.data = price_behavior.PriceData(ticker, intra_time)

    def test_create_price_arrays(self):
        self.data.create_price_arrays()
        first_open_price = self.data.open_price[0]
        first_prior_close_price = self.data.prior_close_price[0]
        first_close_price = self.data.close_price[0]
        first_intra_open = self.data.intra_open[0]
        first_intra_price = self.data.intra_price[0]
        # Verify the price data values
        self.assertEqual(44.5, first_open_price)
        self.assertEqual(43.66, first_prior_close_price)
        self.assertEqual(44.98, first_close_price)
        self.assertEqual(41.54, first_intra_open)
        self.assertEqual(42.8, first_intra_price)


class TestPriceAnalysis(unittest.TestCase):
    def setUp(self):
        ticker = "MSFT"
        boundary = 0.5
        intra_time = False
        show_chart = False
        self.paobj = price_behavior.PriceAnalysis(ticker, boundary, \
                                                  intra_time, show_chart)

    def test_check_daily_parameters(self):
        # If no exception
        raised = False
        try:
            self.paobj.check_daily_parameters()
        except:
            raised = True
        self.assertFalse(raised)

    def test_open_priorclose_analysis(self):
        result = self.paobj.open_priorclose_analysis()
        self.assertEqual(4.2, result["max_price_change"])

    def test_close_open_analysis(self):
        result = self.paobj.close_open_analysis()
        self.assertEqual(86, result["obs_btw_boundaries"])

    def test_close_priorclose_analysis(self):
        result = self.paobj.close_priorclose_analysis()
        self.assertEqual(-6, result["min_price_change"])

    def test_intraprice_open_analysis(self):
        result = self.paobj.intraprice_open_analysis()
        self.assertIsNone(result)


class TestIntradayPriceAnalysis(unittest.TestCase):
    def setUp(self):
        ticker = "MSFT"
        boundary = 0.5
        intra_time = "1800"
        show_chart = False
        self.paobj = price_behavior.PriceAnalysis(ticker, boundary, \
                                                  intra_time, show_chart)

    def test_intraprice_open_analysis(self):
        result = self.paobj.intraprice_open_analysis()
        self.assertEqual(1.057, result["std"])


class TestPriceAnalysisInvalidParams(unittest.TestCase):
    def test_check_daily_parameters_invalid_ticker(self):
        # Verify the exit if invalid ticker is given
        self.paobj = price_behavior.PriceAnalysis("OXY", 0.5, "1800", False)
        self.assertRaises(SystemExit, self.paobj.check_daily_parameters)

    def test_check_daily_parameters_invalid_boundary(self):
        # Verify the exit if invalid boundary is given
        self.paobj = price_behavior.PriceAnalysis("MU", -0.5, "1800", False)
        self.assertRaises(SystemExit, self.paobj.check_daily_parameters)


class TestIntraPriceAnalysisInvalidParams(unittest.TestCase):
    def test_check_intra_parameters_invalid_time_1(self):
        # Verify the exit if invalid time is given
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, True, False)
        self.assertRaises(SystemExit, self.paobj.check_intra_parameters)

    def test_check_intra_parameters_invalid_time_2(self):
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, False, False)
        self.assertIsNone(self.paobj.intraprice_open_analysis())

    def test_check_intra_parameters_invalid_time_3(self):
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, "18000", False)
        self.assertRaises(SystemExit, self.paobj.check_intra_parameters)

    def test_check_intra_parameters_invalid_time_4(self):
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, "2200", False)
        self.assertRaises(SystemExit, self.paobj.check_intra_parameters)

    def test_check_intra_parameters_invalid_time_5(self):
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, "1803", False)
        self.assertRaises(SystemExit, self.paobj.check_intra_parameters)

    def test_check_intra_parameters_invalid_time_6(self):
        self.paobj = price_behavior.PriceAnalysis("MU", 0.5, "xxxx", False)
        self.assertRaises(SystemExit, self.paobj.check_intra_parameters)

    # def test_check_intra_parameters_invalid_time_7(self):
    #     self.paobj = price_behavior.PriceAnalysis("MU", 0.5, 1800, False)
    #     self.assertRaises(SystemExit, self.paobj.check_intra_parameters)


if __name__ == "__main__":
    unittest.main()
