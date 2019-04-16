"""
--------------------------------------------------------------------------------
                    STOCK PRICE BEHAVIOR ANALYZING TOOL
--------------------------------------------------------------------------------

This script reveals stock price daily and intraday fluctuations.
Valid Ticker Symbols (AMAT, C, JD, MSFT, MU, TWTR)

|
| Input parameter(s):
|           Ticker Symbol, Price Range, Boundary, IntraTime, Chart
|           eg. "MU", "close_priorclose", 0.5, "1600", True
|

Parameters to analyze (select 'Price Range')

"open_priorclose":  the difference of the daily open price and
                    the previous day's close price.
"close_open":       the difference of the daily close and open price.
"close_priorclose": the difference of the daily close price and
                    the previous day's close price.
"intraprice_open":  the difference of a selected intraday price
                    (e.g. current trading price at 16:30 - Hungarian time) and
                    the daily open price.

Boundary:   Positive number. Specifies 'price range' boundaries to calculate
            the number of data fall into that boundaries (+/- boundary).
            E.g. 'boundary = 0.5' means that the lower boundary of 'price range'
            is -0.5, the upper boundary is +0.5, exclusive.

IntraTime: Set according to Hungarian trading time from 15:30 - 22:00.
As 5-minutes trading data are used, you must enter minutes
with 5 minute increment eg.: from 1530, 1535 ... to 2155.
Eg.:  1530 -> the first vald time -> close price of the first 5 minutes
      2155 -> the last valid time -> close price of the last 5 minutes ->
      (= daily close price)

Chart: If 'True', the 'Histogram' is shown. The default is 'False'.

Remark: Input parameters must be separated by comma(s).

--------------------------------------------------------------------------------
"""

import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt

# Path settings
base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, "IntraQuotes/{}.txt")

def read_quotes(ticker):
    raw_intra_quotes_df = pd.read_csv(db_path.format(ticker), header=None)
    cols = ("Date", "Time", "Open", "High", "Low", "Close", "Volume")
    raw_intra_quotes_df.columns = cols
    return raw_intra_quotes_df

def get_trading_days(quotes_date):
    trading_days = list(set(quotes_date))
    trading_days.sort()
    return trading_days

def adjust_time(raw_intra_quotes_df):
    # Time values in intraday quotes are based on local (Hungarian time).
    # In Hungary, in 2018 the Daylight Saving Time started 2 weeks later and
    # ended 1 week earlier compared to New York time.
    # It means that on 15 trading days, the trading started at 14:30:00
    # in Hungarian time. These values are adjusted by adding 1 hour.
    different_time_rows = raw_intra_quotes_df[raw_intra_quotes_df.Time=="14:30:00"]
    different_time_days = different_time_rows.Date.tolist()

    # True, in case of different time
    raw_intra_quotes_df["TZ_Bool"] = raw_intra_quotes_df.Date.isin(different_time_days)
    raw_intra_quotes_df["AdjTime"] = raw_intra_quotes_df.Time

    # Faster execution
    adj_time = [re.sub(k[:2], str(int(k[:2])+1), k, 1) if raw_intra_quotes_df.TZ_Bool[i]==True \
        else k for i, k in enumerate(raw_intra_quotes_df.AdjTime)]
    # '1' shall be added in the sub, otherwise 15:15:00->16:16:00 & 20:20:00->21:21:00

    # Slower execution
    # adj_time = raw_intra_quotes_df.apply(lambda row: \
    #             re.sub(row["AdjTime"][:2], str(int(row["AdjTime"][:2])+1), row["AdjTime"], 1)\
    #             if row["TZ_Bool"]==True else row["AdjTime"], axis=1)

    raw_intra_quotes_df["AdjTime"] = adj_time

    intra_quotes_df = raw_intra_quotes_df.drop("TZ_Bool", 1)
    return intra_quotes_df

def create_price_arrays(intra_quotes_df, trading_days, prior_day, intra_time):
    # Open Price
    open_price_series = intra_quotes_df.Open[intra_quotes_df.AdjTime=="15:30:00"]
    open_price = np.array(open_price_series[1:])

    # Prior Close Price = Close Price of the Previous Day
    # (eg. not the close price of 2 days ago)
    prior_close_price_index = (open_price_series.index - prior_day)
    prior_close_price_series = (intra_quotes_df.loc[prior_close_price_index[1:]]).Close
    # FutureWarning:
    # Passing list-likes to .loc or [] with any missing label will raise
    # KeyError in the future, you can use .reindex() as an alternative.
    # because of pror close, slicing [1:] used for open price too
    prior_close_price = np.array(prior_close_price_series)

    # Close Price
    close_price = np.roll(prior_close_price, -1)
    close_price[-1] = intra_quotes_df.Close.iloc[-1]

    # Intraday Price
    # Intraday price is the close price of every 5 minutes trading range
    intra_price_series = intra_quotes_df.Close[intra_quotes_df.AdjTime==intra_time]
    # There were 3 short trading days in 2018.
    # If the specified 'intra_time' is greater than the last trading time of the day,
    # these short days are not considered for analysis.
    intra_date_series = intra_quotes_df.Date[intra_quotes_df.AdjTime==intra_time]
    intra_open_series = intra_quotes_df.Open[(intra_quotes_df.AdjTime=="15:30:00") \
                        & (intra_quotes_df.Date.isin(intra_date_series))]

    intra_price = np.array(intra_price_series)
    intra_open = np.array(intra_open_series)

    return open_price, close_price, prior_close_price, intra_price, intra_open

# For Analyzing
def open_priorclose_analysis(open_price, prior_close_price):
    "Open-Prior Close Price Difference"
    doc = open_priorclose_analysis.__doc__
    open_priorclose_diff = open_price - prior_close_price
    return open_priorclose_diff, doc

def close_open_analysis(close_price, open_price):
    "Close-Open Price Difference"
    doc = close_open_analysis.__doc__
    close_open_diff = close_price - open_price
    return close_open_diff, doc

def close_priorclose_analysis(close_price, prior_close_price):
    "Close-Prior Close Price Difference"
    doc = close_priorclose_analysis.__doc__
    close_priorclose_diff = close_price - prior_close_price
    return close_priorclose_diff, doc

def intraprice_open_analysis(intra_price, intra_open, intra_time):
    doc = f"Intraday Price @{intra_time} - Open Price Difference"
    intraprice_open_diff = intra_price - intra_open
    return intraprice_open_diff, doc

def display_result(data, doc, ticker, boundary, chart):
    min_val = np.floor(np.min(data)) - 0.5
    max_val = np.ceil(np.max(data)) + 0.5
    step = 0.25
    b = np.arange(min_val, max_val + step, step)

    ndata = len(data)

    obs_btw_data = ndata - len(data[data > boundary]) - len(data[data < -boundary])
    obs_btw_data_perc = obs_btw_data / ndata *100

    res_dict = {
                "min_price_change": round(np.min(data),2),
                "max_price_change": round(np.max(data),2),
                "all_obs_number": ndata,
                "obs_btw_boundaries": obs_btw_data,
                "obs_btw_boundaries_perc": round(obs_btw_data_perc,1),
                "mean": round(np.mean(data),3),
                "std": round(np.std(data, ddof=1),3),
                }

    # Drawing Chart
    if chart == True:
        _ = plt.hist(data, bins=b, rwidth=0.9)[0]
        plt.title(f"Histogram of Stock {doc}\nTicker Symbol: {ticker}")
        plt.ylabel("Frequency")
        plt.xlabel(f"{doc}")
        plt.grid(True)
        plt.show()

    return res_dict

def run(ticker, price_range, boundary, intra_time, chart=False):
    val_tickers = ("AMAT", "C", "JD", "MSFT", "MU", "TWTR")
    PRIOR_DAY = 1
    try:
        # Intitial value(s)
        if intra_time == False:
            mod_intra_time = "1755"
        else:
            mod_intra_time = intra_time

        ticker = str.upper(ticker)

        if boundary < 0:
            raise Exception()

        if price_range == "intraprice_open":

            mod_intra_time = ":".join([intra_time[:2], intra_time[2:4], "00"])

        raw_intra_quotes_df = read_quotes(ticker)
        trading_days = get_trading_days(raw_intra_quotes_df.Date)
        intra_quotes_df = adjust_time(raw_intra_quotes_df)
        open_price, close_price, prior_close_price, intra_price, intra_open = \
        create_price_arrays(intra_quotes_df, trading_days, prior_day=PRIOR_DAY, intra_time=mod_intra_time)

        func_dict = {
                    "open_priorclose": lambda: open_priorclose_analysis(open_price, prior_close_price),
                    "close_open": lambda: close_open_analysis(close_price, open_price),
                    "close_priorclose": lambda: close_priorclose_analysis(close_price, prior_close_price),
                    "intraprice_open": lambda: intraprice_open_analysis(intra_price, intra_open, intra_time),
                    }
        data, doc = func_dict[price_range]()
        res_dict = display_result(data, doc, ticker, boundary, chart)
        return res_dict

    except Exception:
        print("[Error] Please check the input parameter(s)")


if __name__ == "__main__":
    run("TWTR", "intraprice_open", 0.5, "1900", True)
