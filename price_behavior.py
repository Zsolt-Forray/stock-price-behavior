#!/usr/bin/python3


"""
--------------------------------------------------------------------------------
                    STOCK PRICE BEHAVIOR ANALYZING TOOL
--------------------------------------------------------------------------------

This script reveals stock price daily and intraday fluctuations.
Valid Ticker Symbols (AMAT, C, JD, MSFT, MU, TWTR)

| Input parameter(s):
|           Ticker Symbol, Boundary, IntraTime, Chart
|           e.g. "MU", 0.5, "1600", True

/Available Methods/
open_priorclose_analysis:  the difference of the daily open price and
                           the previous day's close price.
close_open_analysis:       the difference of the daily close and open price.
close_priorclose_analysis: the difference of the daily close price and
                           the previous day's close price.
intraprice_open_analysis:  the difference of a selected intraday price
                           e.g. current trading price at 16:30 (CET) and
                           the daily open price.

Boundary:   Positive number. Specifies 'price range' boundaries to calculate
            the number of data fall into that boundaries (+/- boundary).
            e.g. 'boundary = 0.5' means that the lower boundary of 'price range'
            is -0.5, the upper boundary is +0.5, exclusive.

IntraTime: Set according to Hungarian trading time (CET) from 15:30 - 22:00.
As 5-minutes trading data are used, you must enter minutes
with 5 minute increment eg.: from 1530, 1535 ... to 2155.
e.g.:  1530 -> the first vald time -> close price of the first 5 minutes
       2155 -> the last valid time -> close price of the last 5 minutes ->
       (= daily close price)

Chart: If 'True', the 'Histogram' is shown. The default is 'False'.

Remark: Input parameters must be separated by comma(s).
--------------------------------------------------------------------------------
"""


__author__  = 'Zsolt Forray'
__license__ = 'MIT'
__version__ = '0.0.1'
__date__    = '09/12/2019'
__status__  = 'Development'


import pandas as pd
import numpy as np
import os
import re
import sys
import matplotlib.pyplot as plt
from user_defined_exceptions import InvalidBoundaryError
from user_defined_exceptions import InvalidTickersError
from user_defined_exceptions import InvalidIntratimeError


class QuotesData:
    def __init__(self, ticker):
        self.ticker = ticker

    @staticmethod
    def define_path():
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "IntraQuotes/{}.txt")

    def read_quotes(self):
        """Read the 5-min intraday quotes from text file as pandas dataframe"""
        db_path = QuotesData.define_path()
        self.raw_intra_quotes_df = pd.read_csv(db_path.format(self.ticker), header=None)
        cols = ("Date", "Time", "Open", "High", "Low", "Close", "Volume")
        self.raw_intra_quotes_df.columns = cols

    def adjust_trading_time(self):
        """
        Time column in intraday quotes are based on local Hungarian (CET) time.
        In Hungary, in 2018 the Daylight Saving Time (forward) started 2 weeks later
        and ended (back) 1 week earlier compared to New York time.
        It means that on 15 trading days, the trading started at 14:30:00
        in Hungarian time. These values are adjusted by adding 1 hour.
        """
        self.read_quotes()
        different_time_rows = \
        self.raw_intra_quotes_df[self.raw_intra_quotes_df.Time=="14:30:00"]
        different_time_days = different_time_rows.Date.tolist()

        # Create temporary bool column:
        # value is True, in case of time should be adjusted.
        self.raw_intra_quotes_df["TZ_Bool"] = \
        self.raw_intra_quotes_df.Date.isin(different_time_days)
        # Create new AdjTime column to store the adjusted time values,
        # but also keep the original Time column
        self.raw_intra_quotes_df["AdjTime"] = self.raw_intra_quotes_df.Time

        # Time adjustement
        self.adj_time = [re.sub(k[:2], str(int(k[:2])+1), k, 1) \
        if self.raw_intra_quotes_df.TZ_Bool[i]==True \
        else k for i, k in enumerate(self.raw_intra_quotes_df.AdjTime)]
        # '1' shall be added in the sub, otherwise 15:15:00->16:16:00 & 20:20:00->21:21:00

    def create_adjusted_quotes(self):
        self.adjust_trading_time()
        # Create finalized & time-adjusted dataframe
        self.raw_intra_quotes_df.AdjTime = self.adj_time
        self.intra_quotes_df = self.raw_intra_quotes_df.drop("TZ_Bool", 1)


class PriceData(QuotesData):
    def __init__(self, ticker, intra_time):
        QuotesData.__init__(self, ticker)
        self.intra_time = intra_time

    def create_price_arrays(self):
        self.create_adjusted_quotes()
        PRIOR_DAY = 1
        OPEN_TIME = "15:30:00"

        # Open Price
        # because of prior close, slicing [1:] used for open price too
        open_price_series = \
                self.intra_quotes_df.Open[self.intra_quotes_df.AdjTime==OPEN_TIME]
        self.open_price = np.array(open_price_series[1:])

        # Prior Close Price
        # = Close Price of the Previous Day
        # (eg. not the close price of 2 days ago)
        prior_close_price_index = (open_price_series.index - PRIOR_DAY)
        prior_close_price_series = \
                (self.intra_quotes_df.loc[prior_close_price_index[1:]]).Close
        self.prior_close_price = np.array(prior_close_price_series)

        # Close Price
        self.close_price = np.roll(self.prior_close_price, -1)
        # change the last close price with the one from the intraday quotes
        # belongs to 20181231, 21:55:00
        self.close_price[-1] = self.intra_quotes_df.Close.iloc[-1]

        # Intraday Price
        # Intraday price is the close price of every 5 minutes trading range
        if isinstance(self.intra_time, str):
            mod_intra_time = self.intra_time
            mod_intra_time = ":".join([self.intra_time[:2], self.intra_time[2:4], "00"])
            intra_price_series = \
                    self.intra_quotes_df.Close[self.intra_quotes_df.AdjTime==mod_intra_time]
            # There were 3 short trading days in 2018.
            # If the specified 'intra_time' is greater than the last trading time of the day,
            # these short days are not considered for analysis.
            intra_date_series = self.intra_quotes_df.Date[self.intra_quotes_df.AdjTime==mod_intra_time]
            intra_open_series = self.intra_quotes_df.Open[(self.intra_quotes_df.AdjTime==OPEN_TIME) \
                                & (self.intra_quotes_df.Date.isin(intra_date_series))]
            self.intra_price = np.array(intra_price_series)
            self.intra_open = np.array(intra_open_series)


class PriceAnalysis(PriceData):
    def __init__(self, ticker, boundary, intra_time=False, show_chart=False):
        PriceData.__init__(self, ticker, intra_time)
        self.boundary = boundary
        self.show_chart = show_chart

    def open_priorclose_analysis(self):
        "Open-Prior Close Price Difference"
        self.check_daily_parameters()
        self.create_price_arrays()
        doc = self.open_priorclose_analysis.__doc__
        open_priorclose_diff = self.open_price - self.prior_close_price
        statistics_data = PriceAnalysis.calc_statistics(open_priorclose_diff, \
                                                        self.boundary)
        PriceAnalysis.display_result(open_priorclose_diff, doc, \
                                     self.ticker, self.show_chart)
        return statistics_data

    def close_open_analysis(self):
        "Close-Open Price Difference"
        self.check_daily_parameters()
        self.create_price_arrays()
        doc = self.close_open_analysis.__doc__
        close_open_diff = self.close_price - self.open_price
        statistics_data = PriceAnalysis.calc_statistics(close_open_diff, \
                                                        self.boundary)
        PriceAnalysis.display_result(close_open_diff, doc, \
                                     self.ticker, self.show_chart)
        return statistics_data

    def close_priorclose_analysis(self):
        "Close-Prior Close Price Difference"
        self.check_daily_parameters()
        self.create_price_arrays()
        doc = self.close_priorclose_analysis.__doc__
        close_priorclose_diff = self.close_price - self.prior_close_price
        statistics_data = PriceAnalysis.calc_statistics(close_priorclose_diff, \
                                                        self.boundary)
        PriceAnalysis.display_result(close_priorclose_diff, doc, \
                                     self.ticker, self.show_chart)
        return statistics_data

    def intraprice_open_analysis(self):
        if self.intra_time:
            self.check_daily_parameters()
            self.check_intra_parameters()
            self.create_price_arrays()
            doc = "Intraday Price @{} - Open Price Difference".format(self.intra_time)
            intraprice_open_diff = self.intra_price - self.intra_open
            statistics_data = PriceAnalysis.calc_statistics(intraprice_open_diff, \
                                                            self.boundary)
            PriceAnalysis.display_result(intraprice_open_diff, doc, \
                                         self.ticker, self.show_chart)
            return statistics_data
        else:
            print("Specify the 'intra_time'")

    def check_daily_parameters(self):
        try:
            valid_tickers = ("AMAT", "C", "JD", "MSFT", "MU", "TWTR")
            ticker = str.upper(self.ticker)
            if ticker not in valid_tickers:
                raise InvalidTickersError()
            if self.boundary <= 0:
                raise InvalidBoundaryError()
        except InvalidBoundaryError:
            print("Boundary must be positiv value")
            sys.exit()
        except InvalidTickersError:
            print("Check the available ticker symbols: AMAT, C, JD, MSFT, MU, TWTR")
            sys.exit()

    def check_intra_parameters(self):
        try:
            if isinstance(self.intra_time, bool):
                if self.intra_time:
                    raise InvalidIntratimeError()
            elif isinstance(self.intra_time, str):
                if len(self.intra_time) != 4:
                    raise InvalidIntratimeError()
                elif not 1530 <= int(self.intra_time) <= 2155:
                    raise InvalidIntratimeError()
                elif self.intra_time[-1] not in ["0", "5"]:
                    raise InvalidIntratimeError()
        except InvalidIntratimeError:
            print("Check the value and format of 'intra_time'")
            sys.exit()
        except ValueError:
            print("Check the value and format of 'intra_time'")
            sys.exit()

    @staticmethod
    def calc_statistics(data, boundary):
        obs_btw_data = len(data) - len(data[data > boundary]) \
                       - len(data[data < -boundary])
        obs_btw_data_perc = obs_btw_data / len(data) * 100
        result_dict = {
                        "min_price_change": round(np.min(data),2),
                        "max_price_change": round(np.max(data),2),
                        "all_obs_number": len(data),
                        "obs_btw_boundaries": obs_btw_data,
                        "obs_btw_boundaries_perc": round(obs_btw_data_perc,1),
                        "mean": round(np.mean(data),3),
                        "std": round(np.std(data, ddof=1),3),
                        }
        return result_dict

    @staticmethod
    def display_result(data, doc, ticker, chart):
        min_val = np.floor(np.min(data)) - 0.5
        max_val = np.ceil(np.max(data)) + 0.5
        step = 0.25
        b = np.arange(min_val, max_val + step, step)
        # Drawing Chart
        if chart:
            _ = plt.hist(data, bins=b, rwidth=0.9)[0]
            plt.title("Histogram of Stock {}\nTicker Symbol: {}".format(doc, ticker))
            plt.ylabel("Frequency")
            plt.xlabel("{}".format(doc))
            plt.grid(True)
            plt.show()
