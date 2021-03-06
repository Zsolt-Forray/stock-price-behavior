# Stock Price Behavior

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/317cc311bf4646ffa314929634c3e0af)](https://www.codacy.com/app/forray.zsolt/stock-price-behavior?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Zsolt-Forray/stock-price-behavior&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/317cc311bf4646ffa314929634c3e0af)](https://www.codacy.com/manual/forray.zsolt/stock-price-behavior?utm_source=github.com&utm_medium=referral&utm_content=Zsolt-Forray/stock-price-behavior&utm_campaign=Badge_Coverage)
[![Build Status](https://travis-ci.com/Zsolt-Forray/stock-price-behavior.svg?branch=master)](https://travis-ci.com/Zsolt-Forray/stock-price-behavior)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Description
Understanding stock price daily and intraday fluctuations is necessary for developing successful trading strategies. This `Price Behavior Analyzing` tool provides statistics of the distribution of predefined stock price ranges (e.g. close price and open price difference) over a given period of time.

#### Predefined Stock Price Ranges  

* [Open Price - Prior Close Price](#open-price-and-prior-close-price-difference)
* [Close Price - Open Price](#close-price-and-open-price-difference)
* [Close Price - Prior Close Price](#close-price-and-prior-close-price-difference)
* [Intraday Price - Open Price](#intraday-price-and-open-price-difference)

## Usage
This project uses sample `5-minutes stock quotes` from the `IntraQuotes` folder. If you want, you can add other 5-minutes stock quotes to this folder. If you add stock quotes having different timeframe, do not forget to update the other quotes accordingly.

### Usage Example

**Parameters:**

* ticker: Ticker symbol
* boundary: Positive number, specifies price range boundaries to calculate the number of data fall into those boundaries (+/- boundary). E.g. `boundary = 0.5` means that the lower boundary is -0.5, the upper boundary is +0.5, exclusive.
* intra_time: Time of the trading session eg. `'1600'`, set according to Hungarian trading time.   
As 5-minutes trading data are used, you must enter minutes with 5 minute increment eg.: from '1530', '1535', '1540' ... to '2150', '2155'.   
The first valid time is `'1530'`, means the close price of the first 5 minutes.   
The last valid time value is `'2155'`, means the close price of the last 5 minutes (= daily close price).
* show_chart: If `True`, the 'Histogram' is shown. The default is `False`.

**Available methods:**

* open_priorclose_analysis
* close_open_analysis
* close_priorclose_analysis
* intraprice_open_analysis

### Output
Dictionary of key statistics:

* min_price_change: minimum value of price range data
* max_price_change: maximum value of price range data
* all_obs_number: number of price range data
* obs_btw_boundaries: number of data fall into the boundaries (+/- boundary)
* obs_btw_boundaries_perc: percentage of data fall into the boundaries (+/- boundary)
* mean: mean of price range data
* std: standard deviation of price range data

Example:

![Screenshot](/png/dictionary_out.png)

#### Open Price and Prior Close Price difference  

The difference of the daily open price and the previous day's close price.

```python
#!/usr/bin/python3

from price_behavior import PriceAnalysis

pa_obj = PriceAnalysis(ticker="MU", boundary=0.5, intra_time=False, show_chart=True)
res = pa_obj.open_priorclose_analysis()
```

![Screenshot](/png/open_priorclose_chart_out.png)

#### Close Price and Open Price difference  

The difference of the daily close and open price.

```python
#!/usr/bin/python3

from price_behavior import PriceAnalysis

pa_obj = PriceAnalysis(ticker="C", boundary=0.5, intra_time=False, show_chart=True)
res = pa_obj.close_open_analysis()
```

![Screenshot](/png/close_open_chart_out.png)

#### Close Price and Prior Close Price difference

The difference of the daily close price and the previous day's close price.

```python
#!/usr/bin/python3

from price_behavior import PriceAnalysis

pa_obj = PriceAnalysis(ticker="TWTR", boundary=0.5, intra_time=False, show_chart=True)
res = pa_obj.close_priorclose_analysis()
```

![Screenshot](/png/close_priorclose_chart_out.png)

#### Intraday Price and Open Price difference

The difference of a selected intraday price (e.g. current trading price at 16:30 (CET)- Hungarian time) and the daily open price.

```python
#!/usr/bin/python3

from price_behavior import PriceAnalysis

pa_obj = PriceAnalysis(ticker="JD", boundary=0.5, intra_time="1700", show_chart=True)
res = pa_obj.intraprice_open_analysis()
```

![Screenshot](/png/intra_open_chart_out.png)

## LICENSE
MIT

## Contributions
Contributions to this repository are always welcome.
This repo is maintained by Zsolt Forray (forray.zsolt@gmail.com).
